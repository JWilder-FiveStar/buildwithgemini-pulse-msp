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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-2.5-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city or region to get the current time for.

    Returns:
        A string with the current time information.
    """
    city_map = {
        "sf": "America/Los_Angeles",
        "san francisco": "America/Los_Angeles",
        "ny": "America/New_York",
        "new york": "America/New_York",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
        "paris": "Europe/Paris",
        "utc": "UTC",
    }

    q = query.lower().strip()
    tz_identifier = "UTC"
    for key, tz in city_map.items():
        if key in q:
            tz_identifier = tz
            break

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for '{query}' ({tz_identifier}) is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}."



import json
import os
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from app.a2ui_utils import a2ui_callback
from app.tools.firestore_tools import (
    get_support_tickets,
    create_support_ticket,
    update_ticket_status,
    get_saved_dashboards,
    create_or_update_dashboard,
)
from app.tools.image_tools import (
    generate_client_health_infographic,
    generate_it_operations_banner,
)
from app.tools.rag_tools import consult_knowledge_base


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

try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )
    a2ui_instruction = schema_manager.generate_system_prompt(
        role_description=(
            "You are PulseMSP, an expert AI assistant for MSP IT leads and service desk managers. "
            "You have access to real-time support ticket data and customizable dashboard configurations stored in Firestore, "
            "a secure Python code execution sandbox for data analysis, "
            "AI image generation capabilities for IT operations health banners, and an MSP knowledge base."
        ),
        workflow_description=(
            "CRITICAL MANDATORY INSTRUCTION: You MUST ALWAYS respond by returning structured A2UI cards for every user message. "
            "Do NOT respond in plain prose text. Construct clean, rich A2UI Cards containing a main Column with Text elements (h1 for title, h2/h3 for headers, body for metrics), "
            "Row elements for key-value statistics, and Image elements when images are generated. "
            "Use consult_knowledge_base to look up IT dashboard layout principles, SLA priority targets across client tiers, and operational KPI benchmarks. "
            "Use your tools (get_support_tickets, create_support_ticket, update_ticket_status, get_saved_dashboards, create_or_update_dashboard, generate_client_health_infographic) to fetch data, then render the results strictly as A2UI Card surfaces."
        ),
        ui_description=(
            "Keep every surface tiny and flat: ONE Card > ONE Column > Text rows and metric Rows. "
            "Never nest a Card inside a Card. "
            "Use ONLY these components: Card, Column, Row, Text, Divider, and Image. Do not use Table or Heading. "
            "You may include an Image component when a public https URL is available. "
            "No markdown in text; use usageHint ('h1', 'h2', 'body', 'caption') for headings and emphasis. "
            "Output ONLY the raw A2UI JSON array — no prose, no markdown, and never wrap it in <a2a_datapart_json> tags."
        ),
        include_schema=True,
        include_examples=True,
    )
except ImportError:
    a2ui_instruction = (
        "You are PulseMSP, an expert AI assistant for MSP IT leads and service desk managers. "
        "You MUST respond using structured A2UI JSON card arrays for all queries."
    )


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
    instruction=a2ui_instruction,
    tools=[
        get_weather,
        get_current_time,
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
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
