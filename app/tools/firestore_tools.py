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

"""Firestore database tools for PulseMSP IT ticket and dashboard management."""

import datetime
import json
from typing import Any
from google.cloud import firestore

# Hardcoded GCP project ID as requested to prevent Agent Platform project number resolution issues
PROJECT_ID = "qwiklabs-gcp-04-0fd928efe4fc"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def get_support_tickets(
    client_name: str | None = None,
    priority: str | None = None,
    status: str | None = None,
) -> str:
    """Retrieve support tickets from Firestore with optional filtering.

    Args:
        client_name: Optional client name filter (e.g. 'Acme Corp', 'Contoso Cyber').
        priority: Optional priority filter (e.g. 'P1', 'Critical', 'High', 'Medium', 'Low').
        status: Optional ticket status filter (e.g. 'Open', 'In Progress', 'Resolved').

    Returns:
        JSON string of matching tickets.
    """
    db = _get_firestore_client()
    query = db.collection("tickets")

    if client_name:
        query = query.where("client_name", "==", client_name)
    if priority:
        query = query.where("priority", "==", priority)
    if status:
        query = query.where("status", "==", status)

    docs = query.stream()
    tickets: list[dict[str, Any]] = [doc.to_dict() for doc in docs]
    return json.dumps(tickets, indent=2)


def create_support_ticket(
    title: str,
    client_name: str,
    priority: str = "Medium",
    technician: str = "Unassigned",
) -> str:
    """Create a new MSP support ticket in Firestore.

    Args:
        title: Summary of the issue.
        client_name: Name of the client account.
        priority: Priority level ('Critical', 'High', 'Medium', 'Low').
        technician: Name of assigned technician.

    Returns:
        JSON string containing the created ticket metadata.
    """
    db = _get_firestore_client()
    # Generate simple ticket ID
    ticket_count = len(list(db.collection("tickets").stream()))
    ticket_id = f"TICK-{100 + ticket_count + 1}"

    ticket_data = {
        "ticket_id": ticket_id,
        "title": title,
        "client_name": client_name,
        "priority": priority,
        "status": "Open",
        "technician": technician,
        "sla_status": "OK",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    db.collection("tickets").document(ticket_id).set(ticket_data)
    return json.dumps({"status": "success", "ticket": ticket_data}, indent=2)


def update_ticket_status(
    ticket_id: str,
    status: str,
    sla_status: str | None = None,
) -> str:
    """Update an existing ticket's status and SLA status in Firestore.

    Args:
        ticket_id: The unique ID of the ticket (e.g. 'TICK-101').
        status: New status ('Open', 'In Progress', 'Resolved').
        sla_status: Optional new SLA status ('OK', 'At Risk', 'Breached').

    Returns:
        JSON string confirming the update.
    """
    db = _get_firestore_client()
    doc_ref = db.collection("tickets").document(ticket_id)
    doc = doc_ref.get()

    if not doc.exists:
        return json.dumps({"error": f"Ticket {ticket_id} not found."})

    update_payload: dict[str, Any] = {"status": status}
    if sla_status:
        update_payload["sla_status"] = sla_status

    doc_ref.update(update_payload)
    return json.dumps(
        {"status": "success", "ticket_id": ticket_id, "updated": update_payload},
        indent=2,
    )


def get_saved_dashboards() -> str:
    """Retrieve saved customizable MSP dashboards from Firestore.

    Returns:
        JSON string of saved dashboard configurations.
    """
    db = _get_firestore_client()
    docs = db.collection("dashboards").stream()
    dashboards: list[dict[str, Any]] = [doc.to_dict() for doc in docs]
    return json.dumps(dashboards, indent=2)


def create_or_update_dashboard(
    dashboard_id: str,
    title: str,
    widgets: list[dict[str, Any]],
) -> str:
    """Save or update a customizable MSP dashboard layout in Firestore.

    Args:
        dashboard_id: Unique identifier for the dashboard (e.g. 'dash-001').
        title: Title of the dashboard.
        widgets: List of widget definitions (e.g. [{'widget_id': 'w1', 'name': 'SLA Breach Rate', 'widget_type': 'metric_card'}]).

    Returns:
        JSON string confirming dashboard save operation.
    """
    db = _get_firestore_client()
    dashboard_data = {
        "dashboard_id": dashboard_id,
        "title": title,
        "widgets": widgets,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    db.collection("dashboards").document(dashboard_id).set(dashboard_data)
    return json.dumps(
        {"status": "success", "dashboard": dashboard_data}, indent=2
    )
