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

import os
import vertexai
from vertexai.preview import rag


def consult_knowledge_base(query: str) -> str:
    """Search the MSP IT knowledge base for IT dashboard layout guidelines, SLA priority definitions, client contract tiers, and operational KPI benchmarks.

    Args:
        query: What to look up (e.g., dashboard layout recommendations, SLA response targets for P1, FCR benchmarks, or client tiering rules).

    Returns:
        The matched passages from the MSP knowledge base, or a note if no relevant information was found.
    """
    corpus_name = os.environ.get("RAG_CORPUS_NAME", "")
    if not corpus_name:
        # Fallback check from .env if not loaded in environment
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("RAG_CORPUS_NAME="):
                        corpus_name = line.strip().split("=", 1)[1]
                        break

    if not corpus_name:
        return "Knowledge base unconfigured (RAG_CORPUS_NAME is not set)."

    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-0fd928efe4fc")
        # Ensure vertexai is initialized to us-central1 where the serverless RAG corpus resides
        vertexai.init(project=project_id, location="us-central1")

        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
        return "\n\n---\n\n".join(passages) or "No relevant passage found in knowledge base."
    except Exception as e:
        return f"Knowledge base query failed: {e}"
