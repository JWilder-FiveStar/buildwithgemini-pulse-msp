#!/usr/bin/env python3
"""Standalone verification script to test RAG retrieval with consult_knowledge_base."""

import os
import sys
from pathlib import Path

# Add app to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load .env file
env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            if line.startswith("RAG_CORPUS_NAME="):
                os.environ["RAG_CORPUS_NAME"] = line.strip().split("=", 1)[1]

from app.tools.rag_tools import consult_knowledge_base

def main():
    print("=== Testing RAG Knowledge Base Retrieval ===")
    queries = [
        "How should I structure a 3-layer layout for an IT operational dashboard?",
        "What are the P1 response and resolution targets for a Platinum tier client?",
        "What is the industry benchmark target for First Contact Resolution (FCR) in MSPs?",
    ]

    for q in queries:
        print(f"\nQuery: '{q}'")
        result = consult_knowledge_base(q)
        print("Result Preview:")
        print(result[:400] + ("..." if len(result) > 400 else ""))

if __name__ == "__main__":
    main()
