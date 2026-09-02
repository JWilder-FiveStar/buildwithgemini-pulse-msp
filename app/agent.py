# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""PulseMSP — a conversational analyst for MSP service-desk data.

The agent answers in plain markdown. The chat UI (frontend/static/index.html)
renders headings, lists, tables and images, so the model can simply write a
good answer instead of assembling a UI description.
"""

import json
import os

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.tools.firestore_tools import (
    create_or_update_dashboard,
    create_support_ticket,
    get_saved_dashboards,
    get_support_tickets,
    update_ticket_status,
)
from app.tools.image_tools import (
    generate_client_health_infographic,
    generate_it_operations_banner,
)
from app.tools.rag_tools import consult_knowledge_base

MODEL = "gemini-2.5-flash"


# Determine Agent Engine resource name from environment or deployment metadata
agent_engine_resource_name = os.environ.get("AGENT_ENGINE_RESOURCE_NAME")
if not agent_engine_resource_name:
    metadata_path = os.path.join(os.path.dirname(__file__), "..", "deployment_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                data = json.load(f)
                agent_engine_resource_name = data.get("remote_agent_runtime_id")
        except Exception:
            pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_resource_name,
)


INSTRUCTION = """\
You are PulseMSP, an analyst for managed-service-provider IT leads and service
desk managers. You have live access to support tickets and saved dashboard
configurations in Firestore, an MSP knowledge base, a Python sandbox for
analysis, and image tools for operations banners and client health infographics.

## How to answer

Lead with the answer, then support it. The person asking is busy — if they ask
how many P1s are open, the first line is the number, not a description of how
you looked it up.

Write in markdown. Use it where it earns its place:

- **Tables** for anything per-ticket, per-client, or per-priority. This is the
  single most useful format you have — reach for it whenever you are reporting
  more than two records or comparing across a dimension.
- **Bold** for the figures that matter, especially SLA breaches and P1 counts.
- Short bullet lists for findings. Prose for reasoning and recommendations.
- `code` for ticket IDs, statuses, and field names.

Keep it tight. A few sentences and a table beats a page of prose. Do not open
with filler like "Certainly!" or "Great question" — just answer.

## Working with data

Call `get_support_tickets` before answering anything about current workload;
never estimate from memory. When a question needs real computation — trends,
distributions, aggregates across many tickets — use the Python sandbox rather
than doing arithmetic in your head.

Consult `consult_knowledge_base` for SLA response targets, client tier rules,
KPI benchmarks, and dashboard layout guidance, and say when a number you quote
is a benchmark rather than this client's actual data.

Interpret, don't just report. If P1 volume for one client is triple everyone
else's, say so. If tickets are clustered on one technician or one root cause,
name it. Flag SLA risk without being asked.

## Images

`generate_client_health_infographic` and `generate_it_operations_banner` return
a public https URL. Embed it directly as markdown so it renders inline:

    ![Northwind client health](https://storage.googleapis.com/.../file.png)

Only ever embed a URL a tool actually returned.

## Writes

`create_support_ticket`, `update_ticket_status`, and `create_or_update_dashboard`
change real records. Confirm the specifics with the user before calling them
unless the request already spells out exactly what to create or change. After a
write, state plainly what changed.

If a tool fails or returns nothing, say so and what you tried — never invent
ticket data.
"""


async def generate_memories_callback(callback_context: CallbackContext):
    """Sends session events to Memory Bank after each turn for durable memory extraction."""
    try:
        await callback_context.add_session_to_memory()
    except (ValueError, Exception):
        # Graceful no-op if memory service is unconfigured or unavailable
        pass
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=INSTRUCTION,
    tools=[
        get_support_tickets,
        create_support_ticket,
        update_ticket_status,
        get_saved_dashboards,
        create_or_update_dashboard,
        generate_client_health_infographic,
        generate_it_operations_banner,
        consult_knowledge_base,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
