"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, streaming the reply
back as server-sent events so text appears as the model writes it:

  * {"type": "delta",   "text": ...}  -> append to the current reply
  * {"type": "replace", "text": ...}  -> the agent revised the whole reply
  * {"type": "error",   "text": ...}  -> show as an error
  * {"type": "done"}                  -> turn finished

Replies are plain markdown; static/index.html renders them. There is no UI
protocol in between.

Why A2A: agents-cli 1.1.0 (GA) deploys ADK agents to Agent Runtime as A2A agents
and no longer registers the reasoning-engine operation schema the old
`agent_engines.get(...).stream_query()` path relied on (operation_schemas() comes
back empty). The container serves the A2A protocol over the Agent Engine HTTP
passthrough, so this proxy fetches the agent's card and sends messages with the
a2a-sdk client (the same path `agents-cli run --mode a2a` uses). This works for
both A2A and plain ADK 1.1.0 deployments (the container serves A2A either way).

Run:
  pip install -r requirements.txt
  export AGENT_ENGINE_RESOURCE_NAME="projects/.../locations/.../reasoningEngines/..."
  export AGENT_DIRECTORY="app"   # your agent's app directory (agents-cli-manifest.yaml)
  python main.py                 # -> http://localhost:8080
"""

import json
import os
import uuid
from collections.abc import AsyncIterator

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    FilePart,
    Message,
    Part,
    Role,
    TaskArtifactUpdateEvent,
    TextPart,
    TransportProtocol,
)
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ["AGENT_ENGINE_RESOURCE_NAME"]
# The agent's app directory (matches agent_directory in agents-cli-manifest.yaml).
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
# Location is embedded in the resource name: projects/<p>/locations/<loc>/reasoningEngines/<id>.
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

# A2A endpoint for an Agent Runtime deployment, via the Agent Engine HTTP
# passthrough. The card lives at the well-known path under this base.
A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"

_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")

# One set of ADC credentials, refreshed per request (access tokens expire ~1h).
_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI()

# Reuse ONE A2A context per user so the agent remembers the conversation.
_contexts: dict[str, str] = {}
# Cache the agent card after the first fetch.
_card: AgentCard | None = None


async def _get_card(client: httpx.AsyncClient) -> AgentCard:
    global _card
    if _card is None:
        resp = await client.get(A2A_CARD_URL)
        resp.raise_for_status()
        card = AgentCard(**resp.json())
        # Agent Runtime does not serve a public card URL, so point the client at
        # the passthrough base for message sends.
        card.url = A2A_BASE
        _card = card
    return _card


def _file_markdown(uri: str) -> str:
    """A generated file becomes an inline image when it looks like one."""
    if uri.lower().endswith(_IMAGE_SUFFIXES):
        return f"\n\n![generated image]({uri})\n\n"
    return f"\n\n[{uri}]({uri})\n\n"


def _artifact_text(parts: list) -> str:
    """Flatten one artifact's parts into markdown.

    Text is read by duck-typing rather than isinstance: depending on the SDK
    path a reply can arrive as a TextPart, as a Blob/inline_data carrying utf-8
    bytes, or as a plain dict. Matching only TextPart silently dropped those and
    the turn looked empty. File parts become a markdown image when the URI looks
    like one, so generated infographics render inline instead of as a bare URL.
    """
    out: list[str] = []
    for p in parts or []:
        root = getattr(p, "root", p)

        text = getattr(root, "text", None)
        if isinstance(text, str) and text.strip():
            out.append(text)
            continue

        if isinstance(root, FilePart):
            uri = getattr(getattr(root, "file", None), "uri", None)
            if uri:
                out.append(_file_markdown(uri))
            continue

        # Blob / inline_data / data carrying utf-8 bytes.
        blob = (
            getattr(root, "inline_data", None)
            or getattr(root, "blob", None)
            or getattr(root, "data", None)
        )
        if blob is not None:
            raw = blob if isinstance(blob, (str, bytes)) else getattr(blob, "data", None)
            if isinstance(raw, bytes):
                try:
                    raw = raw.decode("utf-8")
                except UnicodeDecodeError:
                    raw = None
            if isinstance(raw, str) and raw.strip():
                out.append(raw)
                continue

        if isinstance(root, dict):
            if isinstance(root.get("text"), str) and root["text"].strip():
                out.append(root["text"])
            elif isinstance(root.get("file"), dict) and root["file"].get("uri"):
                out.append(_file_markdown(root["file"]["uri"]))
    return "".join(out)


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


async def _run_turn(message: str, user_id: str) -> AsyncIterator[str]:
    """Send one message to the agent and yield SSE frames as the reply arrives."""
    # Accumulate per artifact, then stream the growing concatenation. A2A lets an
    # artifact update either append to or replace its artifact, so we track both
    # and tell the browser which one happened rather than guessing.
    buffers: dict[str, str] = {}
    order: list[str] = []
    emitted = ""

    def merged() -> str:
        return "".join(buffers[a] for a in order)

    try:
        async with httpx.AsyncClient(headers=_auth_headers(), timeout=180) as client:
            card = await _get_card(client)
            factory = ClientFactory(
                ClientConfig(
                    streaming=True,
                    supported_transports=[
                        TransportProtocol.jsonrpc,
                        TransportProtocol.http_json,
                    ],
                    httpx_client=client,
                )
            )
            a2a_client = factory.create(card)

            msg = Message(
                message_id=str(uuid.uuid4()),
                role=Role.user,
                parts=[Part(root=TextPart(text=message))],
                context_id=_contexts.get(user_id),
            )

            last_task = None
            async for event in a2a_client.send_message(msg):
                if not isinstance(event, tuple):
                    continue
                task, update = event
                if task is not None:
                    last_task = task
                    if getattr(task, "context_id", None):
                        _contexts[user_id] = task.context_id
                if not isinstance(update, TaskArtifactUpdateEvent):
                    continue

                aid = getattr(update.artifact, "artifact_id", "") or "default"
                if aid not in buffers:
                    buffers[aid] = ""
                    order.append(aid)
                chunk = _artifact_text(update.artifact.parts)
                if getattr(update, "append", False):
                    buffers[aid] += chunk
                else:
                    buffers[aid] = chunk

                full = merged()
                if full == emitted:
                    continue
                if full.startswith(emitted):
                    yield _sse({"type": "delta", "text": full[len(emitted) :]})
                else:
                    # The agent rewrote earlier text; resend the whole reply.
                    yield _sse({"type": "replace", "text": full})
                emitted = full

            # Non-streaming fallback: pull the reply from the final task, first
            # from its artifacts and then from its history, since which of the
            # two carries the reply depends on the deployment path.
            if not emitted and last_task is not None:
                full = "".join(
                    _artifact_text(getattr(a, "parts", None))
                    for a in (getattr(last_task, "artifacts", None) or [])
                )
                if not full:
                    history = (
                        getattr(last_task, "history", None)
                        or getattr(last_task, "messages", None)
                        or []
                    )
                    full = "".join(_artifact_text(getattr(h, "parts", None)) for h in history)
                if full:
                    yield _sse({"type": "replace", "text": full})
                    emitted = full

        if not emitted:
            # The turn produced nothing (e.g. the agent only ran tools, or a tool
            # stalled). Be honest rather than silent.
            yield _sse({"type": "error", "text": "The agent didn't return a reply."})
    except Exception as exc:  # surface failures in the chat, not as a dead stream
        yield _sse({"type": "error", "text": f"{type(exc).__name__}: {exc}"})

    yield _sse({"type": "done"})


@app.post("/chat")
async def chat(req: Request) -> StreamingResponse:
    body = await req.json()
    return StreamingResponse(
        _run_turn(body.get("message", ""), body.get("user_id") or "web-user"),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Serve the chat UI (keep this mount last so /chat wins).
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
