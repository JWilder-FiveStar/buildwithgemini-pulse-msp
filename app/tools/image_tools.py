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

"""Image generation tools for PulseMSP IT Operations Health Infographics and Banners."""

import datetime
import json
import os
import uuid
from PIL import Image, ImageDraw
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

BUCKET_NAME = "pulsemsp-public-assets-qwiklabs-gcp-04-0fd928efe4fc"
PROJECT_ID = "qwiklabs-gcp-04-0fd928efe4fc"


async def generate_it_operations_banner(
    description: str,
    tool_context: ToolContext,
) -> str:
    """Generate an IT operations health status banner or summary visual for an MSP client using AI image generation.

    Args:
        description: Detailed prompt or description of the IT health banner to generate (e.g. 'A dark slate IT health status banner showing 99.5% SLA compliance for Contoso Cyber').
        tool_context: ADK ToolContext instance injected at runtime to manage session artifacts.

    Returns:
        The public HTTPS URL (https://storage.googleapis.com/<bucket>/<object>) of the generated image.
    """
    client = genai.Client(
        enterprise=True,
        project=PROJECT_ID,
        location="global",
    )

    prompt = (
        f"A professional modern IT operations health status banner for an MSP dashboard. "
        f"Details: {description}. Style: dark slate UI background, glowing blue metric gauges, high-tech enterprise IT operations status display."
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/png"

    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break

    if not image_bytes:
        return "Error: Image generation failed to return image data."

    ext = "png" if "png" in mime_type.lower() else "jpg"
    filename = f"it_health_banner_{uuid.uuid4().hex[:8]}.{ext}"

    # (1) Save artifact with tool_context.save_artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
    )

    # (2) Upload image bytes to public Cloud Storage bucket in-memory and return its public https URL
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"banners/{filename}")
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/banners/{filename}"
    return public_url


def generate_client_health_infographic(
    client_name: str,
    status_summary: str = "Healthy",
    sla_compliance_pct: float = 98.5,
    open_tickets_count: int = 3,
) -> str:
    """Generate a visual IT operations health status infographic for a client and publish to GCS.

    Args:
        client_name: Name of the MSP client account (e.g. 'Contoso Cyber', 'Acme Corp').
        status_summary: General health status ('Healthy', 'At Risk', 'Critical SLA Alert').
        sla_compliance_pct: SLA compliance percentage (e.g. 98.5 or 85.0).
        open_tickets_count: Total active open tickets count.

    Returns:
        JSON string containing the public URL and markdown embed tag.
    """
    # 1200 x 675 Widescreen High-Res Canvas (Omni Dark Mode Theme)
    width, height = 1200, 675
    image = Image.new("RGBA", (width, height), (11, 15, 25, 255))  # Deep Slate Navy #0B0F19
    draw = ImageDraw.Draw(image)

    # Subtle vertical gradient background
    for y in range(height):
        r = int(11 + (23 - 11) * (y / height))
        g = int(15 + (31 - 15) * (y / height))
        b = int(25 + (51 - 25) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Subtle tech grid pattern
    grid_color = (255, 255, 255, 8)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Status accent colors & theme selection
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

    # Top Cyan-Blue Header Gradient Accent Line
    for x in range(width):
        ratio = x / width
        r = int(6 + (59 - 6) * ratio)
        g = int(182 + (130 - 182) * ratio)
        b = int(212 + (246 - 212) * ratio)
        draw.line([(x, 0), (x, 5)], fill=(r, g, b, 255))

    # Header Bar & Platform Badge Pill
    draw.rounded_rectangle([50, 30, 220, 58], radius=14, fill=(30, 58, 138, 100), outline=(59, 130, 246, 200), width=1)
    draw.text((65, 38), "PULSE MSP • OMNI", fill="#60A5FA")

    draw.text((50, 70), f"{client_name}", fill="#FFFFFF")
    draw.text((50, 105), "Executive IT Operations & SLA Performance Overview", fill="#94A3B8")

    # Live Status Badge Pill (Top Right)
    draw.rounded_rectangle([920, 45, 1150, 85], radius=20, fill=badge_bg, outline=accent_color, width=1)
    draw.ellipse((940, 59, 952, 71), fill=accent_color)
    draw.text((962, 57), status_title, fill=accent_hex)

    # Main System Status Card
    draw.rounded_rectangle([50, 145, 1150, 235], radius=12, fill=(26, 36, 56, 220), outline=(51, 65, 85, 255), width=1)
    draw.rounded_rectangle([50, 145, 62, 235], radius=6, fill=accent_color)
    draw.text((85, 165), "SYSTEM STATUS OVERVIEW", fill="#64748B")
    draw.text((85, 192), f"Account Health: {status_summary}  •  Primary Focus: SLA & Service Desk Throughput", fill="#E2E8F0")

    # KPI Card 1: SLA Compliance Rate (with Circular Arc Gauge)
    draw.rounded_rectangle([50, 260, 580, 580], radius=16, fill=(26, 36, 56, 220), outline=(51, 65, 85, 255), width=1)
    draw.text((80, 285), "SLA COMPLIANCE RATE", fill="#94A3B8")
    draw.text((80, 315), f"{sla_compliance_pct:.1f}%", fill="#F8FAFC")
    draw.text((80, 360), "Target SLA: 98.0%", fill="#64748B")

    # Arc Gauge Meter
    gauge_cx, gauge_cy, gauge_r = 430, 420, 90
    bbox = [gauge_cx - gauge_r, gauge_cy - gauge_r, gauge_cx + gauge_r, gauge_cy + gauge_r]
    draw.arc(bbox, start=135, end=405, fill=(51, 65, 85, 255), width=16)
    sweep = 270.0 * (min(max(sla_compliance_pct, 0.0), 100.0) / 100.0)
    draw.arc(bbox, start=135, end=135 + sweep, fill=accent_color, width=16)
    draw.text((gauge_cx - 25, gauge_cy - 8), f"{sla_compliance_pct:.1f}%", fill="#FFFFFF")

    # KPI Card 2: Active Open Tickets Queue & Distribution
    draw.rounded_rectangle([620, 260, 1150, 580], radius=16, fill=(26, 36, 56, 220), outline=(51, 65, 85, 255), width=1)
    draw.text((650, 285), "SERVICE DESK ACTIVE QUEUE", fill="#94A3B8")
    draw.text((650, 315), f"{open_tickets_count} Active Tickets", fill="#F8FAFC")

    # Mini Queue Distribution Bars
    categories = [
        ("P1 Critical", max(0, open_tickets_count - 2), "#EF4444"),
        ("P2 High", 1 if open_tickets_count > 1 else 0, "#F59E0B"),
        ("P3 Normal", max(1, open_tickets_count - 1), "#3B82F6"),
    ]
    bar_y = 370
    for label, count, color in categories:
        draw.text((650, bar_y), label, fill="#94A3B8")
        draw.text((760, bar_y), str(count), fill="#F8FAFC")
        draw.rounded_rectangle([800, bar_y + 4, 1110, bar_y + 16], radius=4, fill=(15, 23, 42, 255))
        max_val = max(1, open_tickets_count + 2)
        fill_w = int((count / max_val) * 310)
        if fill_w > 0:
            draw.rounded_rectangle([800, bar_y + 4, 800 + fill_w, bar_y + 16], radius=4, fill=color)
        bar_y += 45

    # Footer Metadata
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    draw.line([(50, 610), (1150, 610)], fill=(51, 65, 85, 255), width=1)
    draw.text((50, 625), f"PulseMSP Omni Engine • Automated Operations Intelligence Report • Generated: {now_str}", fill="#64748B")

    # Upload to Cloud Storage in-memory
    import io
    file_id = uuid.uuid4().hex[:8]
    filename = f"infographic_{client_name.lower().replace(' ', '_')}_{file_id}.png"
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"infographics/{filename}")
    blob.upload_from_string(image_bytes, content_type="image/png")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/infographics/{filename}"
    markdown_embed = f"![{client_name} IT Operations Health Infographic]({public_url})"

    return json.dumps(
        {
            "status": "success",
            "client_name": client_name,
            "filename": filename,
            "public_url": public_url,
            "markdown_embed": markdown_embed,
        },
        indent=2,
    )
