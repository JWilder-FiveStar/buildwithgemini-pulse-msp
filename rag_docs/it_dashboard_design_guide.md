# IT Operational Dashboard Design Guide for MSPs

This guide establishes the visual hierarchy, layout architecture, color discipline, and widget mapping standards for IT operations and service desk dashboards in Managed Service Providers (MSPs).

---

## 1. Visual Hierarchy & Grid Layout (The 3-Layer Architecture)

When designing an IT operational dashboard, structure elements using a 3-Layer Visual Hierarchy following a top-to-bottom, left-to-right Z-pattern grid. This ensures users grasp critical health indicators within 5 seconds.

### Layer 1: Executive Summary & Critical Health (Top Header / Row 1)
* **Purpose:** Immediate situational awareness of overall client fleet health and high-priority risks.
* **Key Components:**
  * **System Fleet Health Score:** Aggregated percentage of operational servers and endpoints.
  * **Active P1 / Critical Incidents:** Prominent badge showing active outage count.
  * **SLA Breach Risk Counter:** Count of open tickets within 30 minutes of SLA expiration.
  * **Overall CSAT / NPS Score:** Latest average client satisfaction rating.

### Layer 2: Operational Queues & Performance Trends (Middle / Row 2)
* **Purpose:** Real-time visibility into workload distribution, queue velocity, and technician utilization.
* **Key Components:**
  * **Ticket Volume & Backlog Trend:** Time-series chart showing incoming vs. resolved ticket velocity.
  * **Unassigned Ticket Queue:** Real-time queue list filtered by age and priority.
  * **First Contact Resolution (FCR) Trend:** Weekly FCR percentage line graph against target threshold.
  * **Technician Workload Heatmap:** Active assigned tickets per technician categorized by priority.

### Layer 3: Diagnostic & Account Breakdown (Bottom / Row 3)
* **Purpose:** Deep-dive analysis, ticket lists, and client-by-client breakdowns.
* **Key Components:**
  * **Active Ticket Data Table:** Filterable grid with columns for Ticket ID, Client, Priority, Status, Assigned Tech, SLA Countdown, and Category.
  * **Top Incident Categories:** Donut chart showing top root causes (e.g., Entra ID/Auth, Network/Firewall, Endpoint Security, M365).
  * **Client SLA Compliance Table:** Client-by-client breakdown of SLA met vs. breached percentages.

---

## 2. Color Discipline & Palette Rules (The 60-30-10 Rule)

To prevent visual noise and alert fatigue, strictly enforce color usage:

* **60% Neutral Background & Structural Surfaces:** Dark slate/charcoal (for NOC environments) or crisp light gray (for web dashboards).
* **30% Muted Informational Tones:** Cool blues, teals, and slate grays for normal metrics, neutral charts, and static labels.
* **10% High-Contrast Alert Accents (Reserved Colors):**
  * **RED (#EF4444 / Danger):** Reserved strictly for active P1 critical outages, hard SLA breaches, and system down states.
  * **AMBER (#F59E0B / Warning):** Reserved for impending SLA breaches (<30 mins remaining), high priority (P2) unassigned tickets, and warning threshold alerts.
  * **GREEN (#10B981 / Success):** Used for healthy SLA compliance (>95%), resolved tickets, and target met badges.

*Rule:* Never use red or amber for non-critical chart series or decorative elements.

---

## 3. Persona-Specific Dashboard Templates

### A. Service Desk Lead Dashboard
* **Primary Goal:** Queue management, SLA enforcement, and dispatcher optimization.
* **Recommended Widgets:**
  1. SLA Breach Risk Gauge (<30 mins remaining).
  2. Unassigned Ticket Queue Table with single-click assign action.
  3. Technician Capacity & Ticket Load Chart.
  4. Real-time First Response Time (FRT) vs. Target.

### B. NOC / Infrastructure Engineer Dashboard
* **Primary Goal:** Real-time alert monitoring, incident mitigation, and system uptime.
* **Recommended Widgets:**
  1. Active Infrastructure Outage Banner.
  2. Server & Firewall Availability Status Matrix.
  3. Mean Time to Detect (MTTD) & Mean Time to Resolution (MTTR) Counters.
  4. Active P1/P2 Critical Incident Triage List.

### C. Client Success & Executive Account Manager Dashboard
* **Primary Goal:** Client relationship health, SLA compliance reporting, and contract renewal metrics.
* **Recommended Widgets:**
  1. Client-by-Client SLA Compliance Summary Table.
  2. Monthly CSAT & NPS Trend Graph.
  3. Ticket Volume by Client & Tier (Platinum vs. Gold vs. Silver).
  4. Executive Health Summary Cards with exportable infographic capabilities.
