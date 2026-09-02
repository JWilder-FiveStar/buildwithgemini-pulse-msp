# MSP Service Level Agreements (SLAs) & Client Contract Tiering Framework

This document outlines the priority matrix, response/resolution targets, clock pause rules, and escalation paths for Managed Service Provider (MSP) client agreements.

---

## 1. Ticket Priority Matrix & Severity Definitions

Every incoming support ticket must be categorized into a Priority level based on **Business Impact** and **Urgency**:

| Priority Level | Severity Name | Definition & Examples | First Response Target | Resolution Target |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | **Critical / Emergency** | Complete site/office outage, core server down, active ransomware/security breach, entire department unable to work. | **15 Minutes** | **2 Hours** |
| **P2** | **High** | Major business function degraded, key VIP or executive blocked, primary internet line failed with secondary active. | **30 Minutes** | **4 Hours** |
| **P3** | **Normal / Standard** | Single user issue with workaround available, non-critical software glitch, printer issue affecting individual user. | **2 Hours** | **24 Hours** (1 Business Day) |
| **P4** | **Low / Request** | Routine service request, new user onboarding request, software installation, general inquiry or quote request. | **4 Hours** | **72 Hours** (3 Business Days) |

---

## 2. Client Contract Service Tiers

Response and resolution targets are scaled based on the client's service agreement tier:

### 🥇 Platinum Tier (Mission Critical / 24x7)
* **Target Audience:** Financial services, healthcare, legal firms, 24/7 manufacturing.
* **Service Hours:** 24x7x365 coverage with dedicated primary engineer and immediate phone dispatch.
* **SLA Modifiers:**
  * P1 First Response: **10 Minutes** | Resolution: **1.5 Hours**.
  * P2 First Response: **20 Minutes** | Resolution: **3 Hours**.
* **Guaranteed SLA Compliance Floor:** 99.0% met per month.

### 🥈 Gold Tier (Standard Enterprise / Business Hours+)
* **Target Audience:** Professional services, corporate offices, mid-market businesses.
* **Service Hours:** 8:00 AM – 8:00 PM local time, Monday through Friday.
* **SLA Modifiers:** Standard Priority Matrix targets apply (P1 = 15m response / 2h resolution).
* **Guaranteed SLA Compliance Floor:** 95.0% met per month.

### 🥉 Silver Tier (Essential Support / Business Hours)
* **Target Audience:** Small businesses, non-profits, light IT footprint accounts.
* **Service Hours:** 9:00 AM – 5:00 PM local time, Monday through Friday.
* **SLA Modifiers:**
  * P1 First Response: **30 Minutes** | Resolution: **4 Hours**.
  * P2 First Response: **1 Hour** | Resolution: **8 Hours**.
* **Guaranteed SLA Compliance Floor:** 90.0% met per month.

---

## 3. SLA Clock Management & Pause Rules

To ensure fair measurement, the SLA clock automatically pauses under specific operational conditions:

1. **Pending Client Info (`status = "Pending Client"`):**
   * The SLA clock is paused immediately when a technician requests required credentials, clarification, or testing verification from the client end-user.
   * *Rule:* The clock resumes as soon as the client responds.

2. **Pending Third-Party Vendor (`status = "Pending Vendor"`):**
   * Paused when waiting on external hardware replacement (e.g., Cisco TAC, Dell ProSupport) or ISP line repair beyond the MSP's direct control.

3. **Scheduled Maintenance Window (`status = "Scheduled"`):**
   * Paused during pre-approved maintenance windows agreed upon with the client.

4. **Outside Business Hours (Gold/Silver Tiers):**
   * For non-24x7 clients, the SLA clock halts at the close of business and resumes at the start of the next business day.

---

## 4. Automated Incident Escalation Lifecycle

When an SLA approaches breach or an issue cannot be resolved at Tier 1, follow the mandatory escalation matrix:

1. **Tier 1 (Service Desk Engineer):** Initial triage, logging, diagnostic, and resolution attempt (0–30 mins).
2. **Tier 2 (Senior Systems Lead):** Escalated if unresolved after 30 mins (P1/P2) or if complex network/active directory intervention is needed.
3. **Tier 3 (Practice Lead / Solutions Architect):** Auto-escalated if P1 reaches 50% of SLA resolution window (60 mins) without root cause identified.
4. **Service Delivery Manager (SDM) / Executive Alert:** Immediate notification sent if a P1 ticket breaches SLA or if a Platinum client experiences a P1 incident.
