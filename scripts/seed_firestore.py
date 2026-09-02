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

"""Seed script to populate initial Firestore collections for PulseMSP."""

import datetime
from google.cloud import firestore

# HARDCODED GCP Project ID as requested to prevent Agent Platform project number resolution issues
PROJECT_ID = "qwiklabs-gcp-04-0fd928efe4fc"

SEED_TICKETS = [
    {
        "ticket_id": "TICK-101",
        "client_name": "Acme Corp",
        "title": "VPN Gateway Outage & Authentication Failures",
        "priority": "High",
        "status": "In Progress",
        "technician": "Sarah Chen",
        "sla_status": "At Risk",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "ticket_id": "TICK-102",
        "client_name": "Contoso Cyber",
        "title": "Exchange Server Disk Space Critical (< 5% left)",
        "priority": "Critical",
        "status": "Open",
        "technician": "Alex Rivera",
        "sla_status": "Breached",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "ticket_id": "TICK-103",
        "client_name": "TechStart Inc",
        "title": "New Employee Laptop Provisioning & Onboarding",
        "priority": "Low",
        "status": "Open",
        "technician": "David Kim",
        "sla_status": "OK",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "ticket_id": "TICK-104",
        "client_name": "Acme Corp",
        "title": "Firewall Rule Update for Cloud Migration",
        "priority": "Medium",
        "status": "Resolved",
        "technician": "Sarah Chen",
        "sla_status": "OK",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "ticket_id": "TICK-105",
        "client_name": "Contoso Cyber",
        "title": "Workstation Ransomware Alert Ingestion",
        "priority": "Critical",
        "status": "In Progress",
        "technician": "Alex Rivera",
        "sla_status": "OK",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
]

SEED_DASHBOARDS = [
    {
        "dashboard_id": "dash-001",
        "title": "Executive SLA Overview",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "widgets": [
            {
                "widget_id": "w-101",
                "name": "High Priority SLA Breach Rate",
                "widget_type": "metric_card",
                "metric_key": "high_priority_sla_breach_rate",
                "value": "20%",
                "target": "< 5%",
            },
            {
                "widget_id": "w-102",
                "name": "Technician Ticket Load",
                "widget_type": "table",
                "metric_key": "tech_workload",
            },
        ],
    },
    {
        "dashboard_id": "dash-002",
        "title": "Queue Health & SLA Monitor",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "widgets": [
            {
                "widget_id": "w-201",
                "name": "Open Critical Tickets",
                "widget_type": "metric_card",
                "metric_key": "open_critical_tickets",
                "value": "2",
            }
        ],
    },
]


def seed_database():
    print(f"Initializing Firestore client for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)

    print("Seeding 'tickets' collection...")
    tickets_ref = db.collection("tickets")
    for ticket in SEED_TICKETS:
        tickets_ref.document(ticket["ticket_id"]).set(ticket)
        print(f"  - Document {ticket['ticket_id']} created for {ticket['client_name']}")

    print("Seeding 'dashboards' collection...")
    dashboards_ref = db.collection("dashboards")
    for dashboard in SEED_DASHBOARDS:
        dashboards_ref.document(dashboard["dashboard_id"]).set(dashboard)
        print(f"  - Document {dashboard['dashboard_id']} ({dashboard['title']}) created.")

    print("\n✅ Firestore database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
