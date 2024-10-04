import json
import os
import time
import httpx
import sys
from dotenv import load_dotenv
from mem0 import Memory
from qdrant_client import QdrantClient
import argparse
import logging

# Load environment variables at the beginning of the program for clarity
load_dotenv()

# Set up logging for error handling and background messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for collections
OLLAMA_COLLECTION_NAME = "llama"
AZURE_GPT40_COLLECTION_NAME = "azure_gpt40"
AZURE_GPT35_COLLECTION_NAME = "azure_gpt35"

# Constants for retry mechanism
RETRIES_ATTEMPT = 3
RETRY_DELAY = 5


# Custom class to write to both terminal and file
class Tee:
    def __init__(self, output_file):
        self.terminal = sys.stdout  # Save the original stdout (terminal)
        self.log = open(output_file, 'w')

    def write(self, message):
        self.terminal.write(message)  # Write to terminal
        self.log.write(message)  # Write to the file

    def flush(self):
        self.terminal.flush()
        self.log.flush()


# Set up configurations for each model (Mem0)
def setup_mem0_for_llama31():
    llama_url = os.getenv("OLLAMA_URL")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_port = os.getenv("QDRANT_PORT")
    
    config_llama = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": OLLAMA_COLLECTION_NAME,
                "embedding_model_dims": 768,
                "host": qdrant_url,
                "port": qdrant_port,
            }
        },
        "llm": {
            "provider": "ollama",
            "config": {
                "model": "llama3.1:latest",
                "temperature": 0,
                "max_tokens": 2000,
                "ollama_base_url": llama_url,
            }
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": "nomic-embed-text:latest",
                "ollama_base_url": llama_url,
            },
        },
        "version": "v1.1"
    }
    return Memory.from_config(config_llama)


def setup_mem0_for_gpt40():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_port = os.getenv("QDRANT_PORT")

    config_gpt40 = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": AZURE_GPT40_COLLECTION_NAME,
                "embedding_model_dims": 1536,
                "host": qdrant_url,
                "port": qdrant_port,
            }
        },
        "llm": {
            "provider": "azure_openai",
            "config": {
                "model": "w1",
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
    return Memory.from_config(config_gpt40)


def setup_mem0_for_gpt35():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_port = os.getenv("QDRANT_PORT")

    config_gpt35 = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": AZURE_GPT35_COLLECTION_NAME,
                "embedding_model_dims": 1536,
                "host": qdrant_url,
                "port": qdrant_port,
            }
        },
        "llm": {
            "provider": "azure_openai",
            "config": {
                "model": "gpt-35-turbo",
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
    return Memory.from_config(config_gpt35)


# Refactored function names for clarity
def execute_llm(memories, query, llm_model):
    try:
        if llm_model == "llama":
            return generate_llm_response_ollama(memories, query)
        elif llm_model == "gpt4":
            return generate_llm_response_azure_gpt4(memories, query)
        elif llm_model == "gpt35":
            return generate_llm_response_azure_gpt35(memories, query)
    except Exception as e:
        logging.error(f"Error calling LLM model {llm_model} for query '{query}': {e}")
        return None


def generate_llm_response_ollama(memories, query):
    base_url = os.getenv("OLLAMA_URL")
    prompt = create_prompt(memories, query)
    
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "temperature": 0.1,
        "max_tokens": 2000
    }

    try:
        response = httpx.post(f"{base_url}/api/generate", json=payload)
        response.raise_for_status()

        llm_response = ""
        for line in response.iter_lines():
            if line:
                json_obj = json.loads(line)
                llm_response += json_obj.get("response", "")
        return llm_response

    except httpx.RequestError as e:
        logging.error(f"Error requesting LLM: {e}")
        return None


def generate_llm_response_azure_gpt4(memories, query):
    return generate_azure_llm_response(memories, query, "w1")


def generate_llm_response_azure_gpt35(memories, query):
    return generate_azure_llm_response(memories, query, "gpt-35-turbo")


def generate_azure_llm_response(memories, query, deployment_name):
    base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("OPENAI_API_VERSION")

    prompt = create_prompt(memories, query)

    payload = {
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0,
        "top_p": 0.95,
        "max_tokens": 800
    }

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = httpx.post(
            f"{base_url}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]

    except (httpx.RequestError, KeyError) as e:
        logging.error(f"Error generating response from Azure LLM: {e}")
        return None


def create_prompt(memories, query):
    prompt = f"""You are an AI Assistant. You are given memories and a question. Use the memories to respond.
    Question: {query}\nMemories:\n"""
    for memory in memories:
        prompt += f"{memory}\n"
    return prompt


def parse_and_test_json(memory, json_file, llm):
    with open(json_file, 'r') as f:
        data = json.load(f)

    results = {}
    for category, content in data.items():
        print("\n")
        print(f"Processing category: {category}")
        results[category] = {"query_testcases_1": [], "query_testcases_2": []}

        category_user_id = f"{llm}_{category}"

        for statement in content["statements"]:
            store_statements_in_memory(memory, statement, category_user_id)

        
        print("\n")
        print("Outputing all user_id memories for validation")
        user_memories = memory.get_all(category_user_id)
        formatted_memories = format_memories(user_memories)
        for single_memory in formatted_memories:
            print(single_memory)
        
        print("\n")
        print("Executing query testcases 1")
        process_queries(memory, formatted_memories, content["query_testcases_1"], category_user_id, results[category]["query_testcases_1"], llm)
        
        print("\n")
        print("Executing query testcases 2")
        process_queries(memory, formatted_memories, content["query_testcases_2"], category_user_id, results[category]["query_testcases_2"], llm)

    return results


def store_statements_in_memory(memory, statement, user_id):
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
                # Skip this statement and continue with the rest
                return


def process_queries(memory, memories, queries, user_id, result_list, llm):
    for query in queries:
        try:
            response = memory.search(query, user_id=user_id)
            formatted_response = format_memories(response)
            result_list.append({"query": query, "response": formatted_response})
            print(f"Query: {query}")
            print(f"Searched Memories: {formatted_response}")
            print("LLM Response:", execute_llm(formatted_response, query, llm))
        except Exception as e:
            logging.error(f"Error processing query: {query}: {e}")
            # Log the error and continue with the next query
            continue


def format_memories(raw_memories):
    return [memory_data.get("memory", "No memory text") for memory_data in raw_memories.get("memories", [])]


def cleanup_qdrant():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_port = os.getenv("QDRANT_PORT")
    client = QdrantClient(host=qdrant_url, port=qdrant_port)
    client.delete_collection(OLLAMA_COLLECTION_NAME)
    client.delete_collection(AZURE_GPT35_COLLECTION_NAME)
    client.delete_collection(AZURE_GPT40_COLLECTION_NAME)


def main():
    parser = argparse.ArgumentParser(description="LLM Memory Test")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--model", required=True, choices=["llama", "gpt4", "gpt35"], help="Model to use")
    parser.add_argument("--output", required=False, help="Output file (optional)")
    args = parser.parse_args()

    # Redirecting stdout to both terminal and file if output argument is provided
    if args.output:
        sys.stdout = Tee(args.output)

    # Clean up collections before starting
    cleanup_qdrant()

    # Select model based on input
    if args.model == "llama":
        memory = setup_mem0_for_llama31()
    elif args.model == "gpt4":
        memory = setup_mem0_for_gpt40()
    elif args.model == "gpt35":
        memory = setup_mem0_for_gpt35()

    results = parse_and_test_json(memory, args.input, args.model)

    # Reset stdout to original state and close file
    if args.output:
        sys.stdout.log.close()
        sys.stdout = sys.__stdout__

    # Clean up collections after tests
    cleanup_qdrant()


if __name__ == "__main__":
    main()
