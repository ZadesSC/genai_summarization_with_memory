import json
import os
import logging
from mem0 import Memory
from src.config.config import Config  # Update import to reflect src structure

PAPER_QDRANT_COLLECTION_NAME = "papers_collection"

def get_mem0_memory(config, model_name='w1', config_file=None):
    """Set up Mem0 memory instance with the provided configuration."""
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as file:
            mem0_config = json.load(file)
    else:
        mem0_config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": PAPER_QDRANT_COLLECTION_NAME,
                    "embedding_model_dims": 1536,
                    "host": config.qdrant_url,
                    "port": config.qdrant_port,
                }
            },
            "llm": {
                "provider": "azure_openai",
                "config": {
                    "model": model_name,
                    "temperature": 0,
                    "max_tokens": 2000,
                }
            },
            "embedder": {
                "provider": "azure_openai",
                "config": {
                    "model": "text-ada-embedding-002-2",
                }
            },
            "version": "v1.1"
        }
    return Memory.from_config(mem0_config)


def query_papers_memory(mem0_memory, user_id):
    """Query the memory for stored papers."""
    entries = mem0_memory.get_all(user_id)
    if 'results' in entries and entries['results']:
        for entry in entries['results']:
            print(f"Memory Entry ID: {entry.get('id', 'N/A')}")
            print(f"Content: {entry.get('memory', 'No content')}")
            print("-" * 80)
    else:
        print("No memories found.")
    return
