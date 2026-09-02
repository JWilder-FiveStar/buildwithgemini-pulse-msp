import io
import datetime
import uuid
import math
from PIL import Image, ImageDraw, ImageFont

def generate_omni_style_infographic(
    client_name: str = "Contoso Cyber Solutions",
    status_summary: str = "Healthy Operational",
    sla_compliance_pct: float = 98.5,
    open_tickets_count: int = 3,
) -> Image.Image:
    # 1200 x 675 Widescreen High-Res Canvas
    width, height = 1200, 675
    img = Image.new("RGBA", (width, height), (11, 15, 25, 255))  # Deep Slate Navy #0B0F19
    draw = ImageDraw.Draw(img)

    # 1. Subtle Gradient / Tech Grid background effect
    for y in range(height):
        # Subtle vertical gradient transition from #0B0F19 to #171F33
        r = int(11 + (23 - 11) * (y / height))
        g = int(15 + (31 - 15) * (y / height))
        b = int(25 + (51 - 25) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Tech grid lines (subtle alpha)
    grid_color = (255, 255, 255, 8)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Status colors and theme selection
    status_lower = status_summary.lower()
    if "critical" in status_lower or sla_compliance_pct < 90.0:
        accent_color = (239, 68, 68, 255)      # Red #EF4444
        accent_hex = "#EF4444"
        badge_bg = (239, 68, 68, 30)
        status_title = "CRITICAL SLA ALERT"
    elif "risk" in status_lower or sla_compliance_pct < 95.0:
        accent_color = (245, 158, 11, 255)     # Amber #F59E0B
        accent_hex = "#F59E0B"
        badge_bg = (245, 158, 11, 30)
        status_title = "AT RISK"
    else:
        accent_color = (16, 185, 129, 255)     # Emerald #10B981
        accent_hex = "#10B981"
        badge_bg = (16, 185, 129, 30)
        status_title = "HEALTHY OPERATIONAL"

    # Top Cyan Header Gradient Line
    for x in range(width):
        ratio = x / width
        r = int(6 + (59 - 6) * ratio)
        g = int(182 + (130 - 182) * ratio)
        b = int(212 + (246 - 212) * ratio)
        draw.line([(x, 0), (x, 5)], fill=(r, g, b, 255))

    # 2. Header Bar
    # Platform Tag Pill
    draw.rounded_rectangle([50, 30, 220, 58], radius=14, fill=(30, 58, 138, 100), outline=(59, 130, 246, 200), width=1)
    draw.text((65, 38), "PULSE MSP • OMNI", fill="#60A5FA")

    draw.text((50, 70), f"{client_name}", fill="#FFFFFF")
    draw.text((50, 105), "Executive IT Operations & SLA Performance Overview", fill="#94A3B8")

    # Live Status Badge Pill (Top Right)
    draw.rounded_rectangle([920, 45, 1150, 85], radius=20, fill=badge_bg, outline=accent_color, width=1)
    # Status indicator dot
    draw.ellipse((940, 59, 952, 71), fill=accent_color)
    draw.text((962, 57), status_title, fill=accent_hex)

    # 3. Main System Status Card (Full Width)
    card1_box = [50, 145, 1150, 235]
    draw.rounded_rectangle(card1_box, radius=12, fill=(26, 36, 56, 220), outline=(51, 65, 85, 255), width=1)

    # Left accent indicator bar inside card
    draw.rounded_rectangle([50, 145, 62, 235], radius=6, fill=accent_color)
    draw.text((85, 165), "SYSTEM STATUS OVERVIEW", fill="#64748B")
    draw.text((85, 192), f"Account Health: {status_summary}  •  Primary Focus: SLA & Service Desk Throughput", fill="#E2E8F0")

    # 4. KPI Card 1: SLA Compliance Rate (with Circular Arc Gauge)
    sla_card = [50, 260, 580, 580]
    draw.rounded_rectangle(sla_card, radius=16, fill=(26, 36, 56, 220), outline=(51, 65, 85, 255), width=1)
    draw.text((80, 285), "SLA COMPLIANCE RATE", fill="#94A3B8")
    draw.text((80, 315), f"{sla_compliance_pct:.1f}%", fill="#F8FAFC")
    draw.text((80, 360), f"Target SLA: 98.0%", fill="#64748B")

    # Draw Arc Gauge Meter
    gauge_cx, gauge_cy, gauge_r = 430, 420, 90
    bbox = [gauge_cx - gauge_r, gauge_cy - gauge_r, gauge_cx + gauge_r, gauge_cy + gauge_r]
    # Background Track Arc (135 deg to 405 deg = 270 deg span)
    draw.arc(bbox, start=135, end=405, fill=(51, 65, 85, 255), width=16)
    # Value Arc
    sweep = 270.0 * (min(max(sla_compliance_pct, 0.0), 100.0) / 100.0)
    draw.arc(bbox, start=135, end=135 + sweep, fill=accent_color, width=16)
    # Inner center text
    draw.text((gauge_cx - 25, gauge_cy - 8), f"{sla_compliance_pct:.1f}%", fill="#FFFFFF")

    # 5. KPI Card 2: Active Open Tickets & Service Metrics
    ticket_card = [620, 260, 1150, 580]
    draw.rounded_rectangle(ticket_card, radius=16, fill=(26, 36, 56, 220), outline=(51, 65, 85, 255), width=1)
    draw.text((650, 285), "SERVICE DESK ACTIVE QUEUE", fill="#94A3B8")
    draw.text((650, 315), f"{open_tickets_count} Active Tickets", fill="#F8FAFC")

    # Mini Ticket Queue Distribution Bars
    categories = [
        ("P1 Critical", max(0, open_tickets_count - 2), "#EF4444"),
        ("P2 High", 1 if open_tickets_count > 1 else 0, "#F59E0B"),
        ("P3 Normal", max(1, open_tickets_count - 1), "#3B82F6"),
    ]
    bar_y = 370
    for label, count, color in categories:
        draw.text((650, bar_y), label, fill="#94A3B8")
        draw.text((760, bar_y), str(count), fill="#F8FAFC")
        # Bar track
        draw.rounded_rectangle([800, bar_y + 4, 1110, bar_y + 16], radius=4, fill=(15, 23, 42, 255))
        # Fill width
        max_val = max(1, open_tickets_count + 2)
        fill_w = int((count / max_val) * 310)
        if fill_w > 0:
            draw.rounded_rectangle([800, bar_y + 4, 800 + fill_w, bar_y + 16], radius=4, fill=color)
        bar_y += 45

    # 6. Footer Branding & Timestamp
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    draw.line([(50, 610), (1150, 610)], fill=(51, 65, 85, 255), width=1)
    draw.text((50, 625), f"PulseMSP Omni Engine • Automated Operations Intelligence Report • Generated: {now_str}", fill="#64748B")

    return img

if __name__ == "__main__":
    img = generate_omni_style_infographic()
    img.save("test_omni_infographic.png")
    print("Successfully generated test_omni_infographic.png!")
