# memory.py

import json
import os
import logging
import time
from mem0 import Memory
from genai_app_utils.config.config import Config

# Default collection name for papers in Qdrant
PAPER_QDRANT_COLLECTION_NAME = "papers_collection"

# Constants for retry mechanism
RETRIES_ATTEMPT = 3
RETRY_DELAY = 5


def get_mem0_memory(config, model_name='gpt4', deployment_name='w1', config_file=None):
    """
    Set up Mem0 memory instance with the provided configuration.

    Parameters:
        - config (Config): Configuration object holding LLM and API settings.
        - model_name (str): The name of the model to use in the memory configuration.
        - config_file (str): Optional path to a configuration file for the memory.

    Returns:
        - Memory: An instance of Memory set up with the specified configuration.
    """
    # Load configuration from file if provided, else use default configuration
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as file:
            mem0_config = json.load(file)
    else:
        mem0_config = _generate_default_mem0_config(config, deployment_name)

    return Memory.from_config(mem0_config)


def _generate_default_mem0_config(config, deployment_name):
    """
    Generate a default Mem0 configuration dictionary based on the provided config and model name.

    Parameters:
        - config (Config): Configuration object holding LLM and API settings.
        - deployment_name (str): The deployment name of the model to use in the memory configuration.

    Returns:
        - dict: A default configuration dictionary for the Mem0 memory.
    """
    return {
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
                "model": deployment_name,
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


def query_papers_memory(mem0_memory, user_id):
    """
    Query the memory for stored papers.

    Parameters:
        - mem0_memory (Memory): The Mem0 memory instance to query.
        - user_id (str): The ID of the user whose memory entries to query.

    Returns:
        - None
    """
    try:
        entries = mem0_memory.get_all(user_id)
        if 'results' in entries and entries['results']:
            for entry in entries['results']:
                print(f"Memory Entry ID: {entry.get('id', 'N/A')}")
                print(f"Content: {entry.get('memory', 'No content')}")
                print("-" * 80)
        else:
            print("No memories found.")
    except Exception as e:
        logging.error(f"Error querying papers memory: {e}")


def store_statements_in_memory(memory, statement, user_id):
    """
    Store a statement in the memory with retry logic.

    Parameters:
        - memory (Memory): The Mem0 memory instance to store the statement in.
        - statement (str): The statement to store in memory.
        - user_id (str): The ID of the user to associate with the stored memory.

    Returns:
        - None
    """
    for attempt in range(RETRIES_ATTEMPT):
        try:
            memory.add(statement, user_id)
            print(f"Stored statement: {statement}")
            break
        except Exception as e:
            logging.error(f"Error storing statement: {statement} on attempt {attempt + 1}: {e}")
            if attempt < RETRIES_ATTEMPT - 1:
                print(f"Retrying due to error: {e}")
                time.sleep(RETRY_DELAY)
            else:
                logging.error(f"Max retries reached. Skipping statement: {statement}")


def format_memories(raw_memories):
    """
    Format raw memory entries for display.

    Parameters:
        - raw_memories (dict): The raw memory entries to format.

    Returns:
        - list: A list of formatted memory strings.
    """
    if not isinstance(raw_memories, dict):
        return []
    return [memory_data.get("memory", "No memory text") for memory_data in raw_memories.get("memories", [])]


def cleanup_qdrant():
    """
    Clean up all Qdrant collections related to papers and LLM models.

    This function deletes collections for 'papers_collection', 'azure_gpt35', 'azure_gpt40', and 'ollama'.
    """
    from qdrant_client import QdrantClient

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_port = os.getenv("QDRANT_PORT")
    client = QdrantClient(host=qdrant_url, port=qdrant_port)

    collections_to_delete = [
        PAPER_QDRANT_COLLECTION_NAME,
        "azure_gpt35",
        "azure_gpt40",
        "ollama"
    ]

    for collection in collections_to_delete:
        try:
            client.delete_collection(collection)
            print(f"Deleted collection: {collection}")
        except Exception as e:
            logging.error(f"Error deleting collection {collection}: {e}")
