#!/usr/bin/env python3
"""Standalone test for generate_it_operations_banner tool."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add app to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools.image_tools import generate_it_operations_banner

async def main():
    print("=== Testing generate_it_operations_banner Tool ===")
    mock_context = MagicMock()
    mock_context.save_artifact = AsyncMock(return_value=1)

    description = "Sleek blue dark-mode IT operations health status banner showing 99.8% SLA compliance for Contoso Cyber"
    print(f"Calling tool with description: '{description}'...")

    url = await generate_it_operations_banner(
        description=description,
        tool_context=mock_context,
    )

    print("\nResult URL:", url)
    print("save_artifact call count:", mock_context.save_artifact.call_count)
    if mock_context.save_artifact.call_count > 0:
        call_args = mock_context.save_artifact.call_args
        print("save_artifact kwargs:", call_args.kwargs)

if __name__ == "__main__":
    asyncio.run(main())
