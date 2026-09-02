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

"""Expanded seed script to generate 35 MSP tickets and update Firestore and CSV."""

import csv
import random
import os
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-0fd928efe4fc"

CSV_HEADER = [
    "internal_ticket_id",
    "ticket_id",
    "summary_redacted",
    "created",
    "updated",
    "state",
    "status",
    "status_id",
    "priority",
    "assignee_pseudo",
    "assignee_is_unassigned",
    "board",
    "board_type",
    "ticket_type",
    "sentiment",
    "contact_pseudo",
    "contact_party",
    "client_pseudo",
    "client_sector",
    "merged_into_ticket_id",
    "bundled_into_ticket_id",
    "record_category",
    "student_record_risk",
    "summary_had_pii",
    "pii_kinds_removed",
]

CLIENTS = [
    {
        "name": "Oakridge Unified School District",
        "client_pseudo": "CLIENT_0062",
        "sector": "k12_education",
        "board": "Ticket - Oakridge Unified School District",
        "has_student_risk": True,
    },
    {
        "name": "Contoso Cyber Security",
        "client_pseudo": "CLIENT_0012",
        "sector": "cybersecurity",
        "board": "Ticket - Contoso Cyber Security",
        "has_student_risk": False,
    },
    {
        "name": "Acme Financial Services",
        "client_pseudo": "CLIENT_0088",
        "sector": "financial_services",
        "board": "Ticket - Acme Financial Services",
        "has_student_risk": False,
    },
    {
        "name": "HealthFirst Medical Group",
        "client_pseudo": "CLIENT_0045",
        "sector": "healthcare",
        "board": "Ticket - HealthFirst Medical Group",
        "has_student_risk": False,
    },
    {
        "name": "Vanguard Legal Partners",
        "client_pseudo": "CLIENT_0091",
        "sector": "legal_services",
        "board": "Ticket - Vanguard Legal Partners",
        "has_student_risk": False,
    },
    {
        "name": "Apex Precision Manufacturing",
        "client_pseudo": "CLIENT_0034",
        "sector": "manufacturing",
        "board": "Ticket - Apex Precision Manufacturing",
        "has_student_risk": False,
    },
]

TECHNICIANS = ["TECH_012", "TECH_035", "TECH_007", "TECH_044", "TECH_089", ""]
PRIORITIES = [
    "Priority 1 - Critical",
    "Priority 2 - High",
    "Priority 3 - Medium",
    "Priority 4 - Low",
]
BOARD_TYPES = ["Phone", "Email", "Portal", "Monitoring Alert", "Automated Scan"]
CATEGORIES = [
    ("general_support", "Hardware", "Desk Phone Not Powering On and Frozen Screen Issue"),
    ("network_infrastructure", "Infrastructure", "VPN Gateway High Latency and Packet Drops"),
    ("wireless_connectivity", "Wireless Network", "Student Chromebook Wi-Fi Auth Failure Batch"),
    ("server_maintenance", "Server Hardware", "Exchange Server Storage Space Low (< 5% Free)"),
    ("identity_access", "User Onboarding", "New Executive Assistant Laptop & MFA Setup"),
    ("threat_response", "Security Incident", "Suspicious Phishing Email with PDF Malware"),
    ("classroom_tech", "Hardware", "Smart Board Touchscreen Calibration Offset Error"),
    ("cloud_backup", "Software", "Nightly Offsite Backup Job Failed with Timeout"),
    ("firewall_security", "Network", "Palo Alto Firewall Core Policy Sync Disruption"),
    ("voip_telephony", "Phone", "SIP Trunk Line Disconnect during High Call Volume"),
    ("database_perf", "Software", "SQL Database CPU Utilization Spike to 99%"),
    ("endpoint_antivirus", "Security Incident", "EDR Malware Quarantine Alert on Finance PC"),
    ("workstation_deploy", "User Onboarding", "CAD Station Monitor Dual Output Failure"),
    ("active_directory", "Identity", "Domain Controller Kerberos Ticket Auth Timeout"),
    ("print_services", "Peripheral", "Floor 2 Print Spooler Crash and Document Backlog"),
]

SENTIMENTS = [
    "20/100 (Extremely Frustrated)",
    "35/100 (Frustrated)",
    "50/100 (Neutral)",
    "65/100 (Satisfied)",
    "85/100 (Delighted)",
]


def generate_tickets(count=35):
    random.seed(42)  # Deterministic seed for reproducible testing
    tickets = []
    start_internal_id = 284371380
    start_ticket_id = 679880

    for i in range(count):
        internal_id = str(start_internal_id + i)
        t_id = str(start_ticket_id + i)
        client = random.choice(CLIENTS)
        cat_info = random.choice(CATEGORIES)
        record_cat, ticket_type, summary_base = cat_info
        summary = f"{summary_base} [Ref #{t_id}]"

        created_day = random.randint(1, 28)
        updated_day = min(created_day + random.randint(0, 3), 28)
        created_str = f"2026-08-{created_day:02d}"
        updated_str = f"2026-08-{updated_day:02d}"

        priority = random.choice(PRIORITIES)
        assignee = random.choice(TECHNICIANS)
        is_unassigned = "true" if not assignee else "false"

        if "Critical" in priority or "High" in priority:
            state = random.choice(["in_progress", "open", "done"])
        else:
            state = random.choice(["done", "in_progress", "waiting_on_client"])

        if state == "done":
            status = ">Closed"
            status_id = "829416"
        elif state == "in_progress":
            status = "In Progress"
            status_id = "829417"
        elif state == "waiting_on_client":
            status = "Waiting on Client"
            status_id = "829419"
        else:
            status = "New"
            status_id = "829418"

        sentiment = random.choice(SENTIMENTS)
        contact_id = f"CONTACT_{random.randint(100, 999):05d}"
        contact_party = "internal_system" if "Monitoring" in random.choice(BOARD_TYPES) else "external_client"
        student_risk = "true" if client["has_student_risk"] and random.random() > 0.5 else "false"
        had_pii = "true" if random.random() > 0.4 else "false"
        pii_kinds = random.choice(["email", "ip_address", "student_name,student_id", "phone_number", ""]) if had_pii == "true" else ""

        tickets.append(
            {
                "internal_ticket_id": internal_id,
                "ticket_id": t_id,
                "summary_redacted": summary,
                "created": created_str,
                "updated": updated_str,
                "state": state,
                "status": status,
                "status_id": status_id,
                "priority": priority,
                "assignee_pseudo": assignee,
                "assignee_is_unassigned": is_unassigned,
                "board": client["board"],
                "board_type": random.choice(BOARD_TYPES),
                "ticket_type": ticket_type,
                "sentiment": sentiment,
                "contact_pseudo": contact_id,
                "contact_party": contact_party,
                "client_pseudo": client["client_pseudo"],
                "client_sector": client["sector"],
                "merged_into_ticket_id": "",
                "bundled_into_ticket_id": "",
                "record_category": record_cat,
                "student_record_risk": student_risk,
                "summary_had_pii": had_pii,
                "pii_kinds_removed": pii_kinds,
                # Convenience helper fields for Firestore queries
                "title": summary,
                "client_name": client["name"],
                "technician": assignee or "Unassigned",
                "sla_status": (
                    "Breached" if "Critical" in priority and state != "done"
                    else "At Risk" if "High" in priority and state != "done"
                    else "OK"
                ),
            }
        )

    return tickets


def seed_tickets():
    data = generate_tickets(35)

    # 1. Write CSV file locally
    os.makedirs("data", exist_ok=True)
    csv_path = "data/seed_tickets.csv"
    print(f"Writing {len(data)} tickets to CSV dataset {csv_path}...")

    # Exclude internal convenience fields from raw CSV export header
    csv_data = []
    for item in data:
        row = {k: v for k, v in item.items() if k in CSV_HEADER}
        csv_data.append(row)

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(csv_data)
    print(f"✅ Saved {len(data)} tickets to {csv_path}")

    # 2. Write to Firestore DB
    print(f"\nInitializing Firestore client for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)

    tickets_ref = db.collection("tickets")

    # Clear existing documents first to avoid legacy references to old client names
    existing_docs = tickets_ref.limit(100).get()
    for doc in existing_docs:
        doc.reference.delete()
    print(f"Cleared {len(existing_docs)} legacy ticket documents.")

    for item in data:
        tickets_ref.document(item["ticket_id"]).set(item)

    print(f"\n✅ Firestore tickets collection populated with {len(data)} tickets successfully!")


if __name__ == "__main__":
    seed_tickets()
