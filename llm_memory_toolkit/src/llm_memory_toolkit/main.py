# main.py

import os
import json
import logging
import sys
import argparse
import time
from dotenv import load_dotenv

# Import from the genai_app_utils module
from genai_app_utils.config.config import Config
from genai_app_utils.memory.memory import (
    get_mem0_memory, 
    store_statements_in_memory, 
    cleanup_qdrant, 
    format_memories
)
from genai_app_utils.llm.llm import generate_llm_response

# Set up environment variables and logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for retry mechanism
RETRIES_ATTEMPT = 3
RETRY_DELAY = 5


# Define a utility class to redirect stdout to both terminal and file
class Tee:
    def __init__(self, output_file):
        self.terminal = sys.stdout
        self.log = open(output_file, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()


def setup_mem0_memory(config, model_name, config_file=None):
    """
    Set up the Mem0 memory instance for a specific model using a configuration file if provided.

    Parameters:
        - config (Config): Configuration object holding LLM and API settings.
        - model_name (str): The model name to use (e.g., 'llama', 'gpt35', 'gpt4').
        - config_file (str): Optional path to a memory configuration file.

    Returns:
        - Memory: The Mem0 memory instance configured with the specified settings.
    """
    return get_mem0_memory(config, model_name=model_name, config_file=config_file)


def process_queries(memory, memories, queries, user_id, result_list, llm):
    """
    Process a list of queries and store the results.

    Parameters:
        - memory (Memory): The Mem0 memory instance to search and store results in.
        - memories (list): A list of formatted memories to use as context.
        - queries (list): A list of query strings to process.
        - user_id (str): The user ID associated with the queries.
        - result_list (list): A list to store the results of the queries.
        - llm (str): The LLM model to use for the queries.

    Returns:
        - None
    """
    for query in queries:
        try:
            response = memory.search(query, user_id=user_id)
            formatted_response = format_memories(response)
            result_list.append({"query": query, "response": formatted_response})
            print(f"Query: {query}")
            print(f"Searched Memories: {formatted_response}")
            print("LLM Response:", generate_llm_response(formatted_response, deployment_name=llm, config=config))
        except Exception as e:
            logging.error(f"Error processing query: {query}: {e}")
            continue


def parse_and_test_json(memory, json_file, llm):
    """
    Parse a JSON file containing test cases and use memory and LLM for testing.

    Parameters:
        - memory (Memory): The Mem0 memory instance to store and query memories.
        - json_file (str): The path to the JSON file containing test cases.
        - llm (str): The LLM model to use for testing.

    Returns:
        - dict: The results of the test cases.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    results = {}
    for category, content in data.items():
        print(f"\nProcessing category: {category}")
        results[category] = {"query_testcases_1": [], "query_testcases_2": []}

        category_user_id = f"{llm}_{category}"

        # Store statements in memory
        for statement in content["statements"]:
            store_statements_in_memory(memory, statement, category_user_id)

        print("\nOutputting all user_id memories for validation")
        user_memories = memory.get_all(category_user_id)
        formatted_memories = format_memories(user_memories)
        for single_memory in formatted_memories:
            print(single_memory)

        # Process query testcases 1
        print("\nExecuting query testcases 1")
        process_queries(memory, formatted_memories, content["query_testcases_1"], category_user_id, results[category]["query_testcases_1"], llm)

        # Process query testcases 2
        print("\nExecuting query testcases 2")
        process_queries(memory, formatted_memories, content["query_testcases_2"], category_user_id, results[category]["query_testcases_2"], llm)

    return results


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="LLM Memory Test Utility")
    parser.add_argument("--input", required=True, help="Input JSON file containing test cases.")
    parser.add_argument("--model", required=True, choices=["llama", "gpt4", "gpt35"], help="Model to use for testing.")
    parser.add_argument("--config-file", required=False, help="Optional path to a Mem0 configuration file.")
    parser.add_argument("--output", required=False, help="Optional output file for logging results.")
    args = parser.parse_args()

    # Set up the config object
    config = Config()

    # Redirect stdout to both terminal and file if the output argument is provided
    if args.output:
        sys.stdout = Tee(args.output)

    # Clean up existing Qdrant collections before starting tests
    cleanup_qdrant()

    # Set up the Mem0 memory instance based on the provided model
    memory = setup_mem0_memory(config, model_name=args.model, config_file=args.config_file)

    # Run tests and parse the input JSON file
    results = parse_and_test_json(memory, args.input, args.model)

    # Restore original stdout if it was redirected
    if args.output:
        sys.stdout.log.close()
        sys.stdout = sys.__stdout__

    # Clean up Qdrant collections after tests are completed
    cleanup_qdrant()


if __name__ == "__main__":
    main()
