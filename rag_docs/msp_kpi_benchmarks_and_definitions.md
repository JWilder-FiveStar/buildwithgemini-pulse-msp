# MSP Operational KPIs, Formulas & Performance Industry Benchmarks

This document details key performance indicators (KPIs), calculation formulas, targets, and analysis guidelines for Managed Service Providers (MSPs).

---

## 1. Core Service Desk Metrics

### Mean Time to Resolution (MTTR)
* **Definition:** The average elapsed operational time required to fully resolve and close a support ticket from initial logging.
* **Formula:**
  $$\text{MTTR} = \frac{\sum (\text{Ticket Resolution Time} - \text{Ticket Creation Time} - \text{SLA Paused Duration})}{\text{Total Resolved Tickets}}$$
* **Industry Benchmarks:**
  * **Top Performing (Best in Class):** $< 3.5 \text{ operational hours}$
  * **Average MSP Target:** $4.0 - 6.0 \text{ operational hours}$
  * **At-Risk Threshold:** $> 8.0 \text{ operational hours}$

### First Contact Resolution (FCR) Rate
* **Definition:** The percentage of support tickets resolved during the initial contact (first phone call, chat session, or first email reply) without requiring follow-up or escalation.
* **Formula:**
  $$\text{FCR \%} = \left( \frac{\text{Tickets Resolved on First Interaction}}{\text{Total Inbound Tickets}} \right) \times 100$$
* **Industry Benchmarks:**
  * **Top Performing:** $> 75\%$
  * **Average Target:** $65\% - 72\%$
  * **At-Risk Threshold:** $< 55\%$ (Indicates poor Knowledge Base usage or inadequate Tier 1 training)

### First Response Time (FRT)
* **Definition:** The duration from ticket creation until a human technician makes initial recorded contact with the client.
* **Industry Benchmarks:**
  * **P1 Critical Target:** $< 15 \text{ minutes}$
  * **P2 High Target:** $< 30 \text{ minutes}$
  * **Overall Average Inbound FRT:** $< 20 \text{ minutes}$

---

## 2. SLA Compliance & Queue Health

### SLA Compliance Rate (%)
* **Definition:** Percentage of total tickets closed or responded to within contractually agreed SLA targets.
* **Formula:**
  $$\text{SLA Compliance \%} = \left( \frac{\text{Total Tickets Met SLA}}{\text{Total Tickets Eligible for SLA}} \right) \times 100$$
* **Industry Benchmarks:**
  * **Target:** $\ge 95.0\%$
  * **Platinum Client Target:** $\ge 99.0\%$
  * **At-Risk Threshold:** $< 90.0\%$ (Triggers internal service review and client audit)

### Ticket Backlog Aging Profile
* **Definition:** Distribution of open, unresolved tickets grouped by duration open.
* **Healthy Target Distribution:**
  * **0 – 2 Days:** $70\% - 80\%$ of total open queue
  * **3 – 5 Days:** $15\% - 20\%$ of total open queue
  * **6+ Days (Aged Backlog):** $< 5\%$ of total open queue
* **Action Threshold:** Any ticket open $> 7 \text{ days}$ must be flagged for management review.

---

## 3. Capacity & Client Experience Metrics

### Technician Utilization Rate
* **Definition:** Percentage of billable or direct ticket work time logged by technicians relative to available work hours.
* **Formula:**
  $$\text{Utilization \%} = \left( \frac{\text{Logged Ticket Hours}}{\text{Total Available Shift Hours}} \right) \times 100$$
* **Healthy Target:** $70\% - 80\%$ (Allows 20–30% capacity buffer for emergency P1 outages, training, and administrative documentation).

### Customer Satisfaction (CSAT) Score
* **Definition:** Post-ticket closure customer rating average on a 1 to 5 scale (or percentage satisfied).
* **Industry Benchmark Target:** $\ge 96\%$ positive rating ($\ge 4.8 / 5.0$).
