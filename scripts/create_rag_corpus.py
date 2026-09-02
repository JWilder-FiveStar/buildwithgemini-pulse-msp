#!/usr/bin/env python3
"""Script to upload MSP knowledge base docs, create a serverless Vertex AI RAG corpus,
and save the corpus resource name to .env.
"""

import os
import sys
from pathlib import Path
import google.auth
from google.cloud import storage
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

# Project and Location Configuration
LOCATION = "us-central1"  # Serverless RAG Engine is us-central1 only
BUCKET_NAME = "bwg3-qwiklabs-gcp-04-0fd928efe4fc"
GCS_FOLDER = "rag_docs"
GCS_PREFIX = f"gs://{BUCKET_NAME}/{GCS_FOLDER}/"

LOCAL_RAG_DIR = Path(__file__).resolve().parent.parent / "rag_docs"

PARSING_PROMPT = (
    "Extract all IT dashboard design principles, SLA priority metrics, response/resolution targets, "
    "client tiering frameworks, KPI formulas, and operational guidelines from this document. "
    "Omit boilerplate and formatting artifacts. Output clean, self-contained, domain-rich prose."
)

def get_project_id() -> str:
    """Get GCP project ID from default credentials or gcloud config."""
    try:
        _, project = google.auth.default()
        if project:
            return project
    except Exception:
        pass
    return os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-0fd928efe4fc")

def upload_docs_to_gcs(project_id: str):
    """Upload local markdown files to Cloud Storage."""
    print(f"Uploading local docs from {LOCAL_RAG_DIR} to {GCS_PREFIX}...")
    client = storage.Client(project=project_id)
    bucket = client.bucket(BUCKET_NAME)

    for doc in LOCAL_RAG_DIR.glob("*.md"):
        blob_path = f"{GCS_FOLDER}/{doc.name}"
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(str(doc))
        print(f"  Uploaded {doc.name} -> gs://{BUCKET_NAME}/{blob_path}")

def update_env_file(corpus_name: str):
    """Save RAG_CORPUS_NAME into pulse-msp/.env file."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    lines = []
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()
    
    updated = False
    new_line = f"RAG_CORPUS_NAME={corpus_name}\n"
    for i, line in enumerate(lines):
        if line.startswith("RAG_CORPUS_NAME="):
            lines[i] = new_line
            updated = True
            break
    if not updated:
        lines.append(new_line)

    with open(env_path, "w") as f:
        f.writelines(lines)
    print(f"Updated {env_path} with RAG_CORPUS_NAME={corpus_name}")

def main():
    project_id = get_project_id()
    print(f"Initializing RAG Corpus creation for Project: {project_id} in {LOCATION}...")

    # Step 1: Upload docs to GCS
    upload_docs_to_gcs(project_id)

    # Step 2: Initialize Vertex AI
    vertexai.init(project=project_id, location=LOCATION)

    # Step 3: Enable serverless mode for ragEngineConfig
    cfg_name = f"projects/{project_id}/locations/{LOCATION}/ragEngineConfig"
    print("Setting RAG Engine configuration to Serverless mode...")
    try:
        rag.update_rag_engine_config(
            rag_engine_config=rag.RagEngineConfig(
                name=cfg_name,
                rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
            )
        )
    except Exception as e:
        print(f"Notice during update_rag_engine_config: {e}")

    # Step 4: Create the RAG Corpus
    corpus_display_name = "pulsemsp-knowledge-base"
    print(f"Creating RAG Corpus '{corpus_display_name}'...")
    corpus = rag.create_corpus(
        display_name=corpus_display_name,
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    print(f"Created RAG Corpus: {corpus.name}")

    # Step 5: Import documents with LLM Parser
    print(f"Importing and indexing files from {GCS_PREFIX} using LLM parser (gemini-2.5-flash)...")
    import_resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PREFIX],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print(f"Import complete! Imported files count: {import_resp.imported_rag_files_count}")

    # Step 6: Save corpus resource name to .env
    update_env_file(corpus.name)
    print("\nRAG Corpus setup successful!")

if __name__ == "__main__":
    main()
