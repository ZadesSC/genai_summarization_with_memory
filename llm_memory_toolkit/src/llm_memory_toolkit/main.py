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
from genai_app_utils.llm.llm import generate_llm_response, create_prompt
from genai_app_utils.config.config import Config
from genai_app_utils.utils.tee import Tee

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up the config object for environment variables
config = Config()

# Saves mem0 config for use later
mem0_config = None

# Constants for retry mechanism
RETRIES_ATTEMPT = 3
RETRY_DELAY = 5

# Database values
DATABASE_NAME = "memory_toolkit"


def setup_mem0_memory(mem0_config=None):
    """
    Set up the Mem0 memory instance for a specific model using a configuration file if provided.

    Parameters:
        - config (Config): Mem0 configuration file

    Returns:
        - Memory: The Mem0 memory instance configured with the specified settings.
    """
    return get_mem0_memory(mem0_config)


def add_statement_to_memory(memory, content, user_id):
    store_statements_in_memory(memory, content, user_id)


def update_statement_in_memory(memory, old_content, new_content, user_id):
    """
    Update a statement in memory by deleting the old one and adding the new one.

    Parameters:
        - memory (Memory): The Mem0 memory instance.
        - old_content (str): The old statement content to be updated.
        - new_content (str): The new statement content.
        - user_id (str): The user ID associated with the statements.

    Returns:
        - None
    """
    #delete_statement_from_memory(memory, old_content, user_id)
    #add_statement_to_memory(memory, new_content, user_id)
    pass


def delete_statement_from_memory(memory, content, user_id):
    """
    Delete a statement from memory.

    Parameters:
        - memory (Memory): The Mem0 memory instance.
        - content (str): The statement content to be deleted.
        - user_id (str): The user ID associated with the statements.

    Returns:
        - None
    """
    # Assuming the memory instance has a delete method
    #memory.delete(content, user_id=user_id)
    pass


def parse_and_test_json(memory, test_file, provider_name, model_name):
    """
    Parse a JSON file containing test cases and use memory and LLM for testing.

    Parameters:
        - memory (Memory): The Mem0 memory instance to store and query memories.
        - test_file (str): The path to the JSON file containing test cases.
        - provider_name: The provider as given in mem0 config.
        - model_name (str): The model as given in mem0 config.

    Returns:
        - dict: The results of the test cases.
    """
    with open(test_file, 'r') as f:
        data = json.load(f)

    results = {}
    for test_case in data:
        test_name = test_case.get('test_name', 'Unnamed Test')
        print(f"\nProcessing test case: {test_name}")
        results[test_name] = {"queries": []}

        user_id = f"{provider_name}_{test_name}"

        # Process statements (add, update, delete)
        for statement in test_case.get('statements', []):
            operation = statement.get('operation', 'add')
            content = statement.get('content', '')

            if operation == 'add':
                add_statement_to_memory(memory, content, user_id)
                print(f"Added to memory: {content}")
            elif operation == 'update':
                old_content = statement.get('old_content', '')
                new_content = content
                update_statement_in_memory(memory, old_content, new_content, user_id)
                print(f"Updated memory: '{old_content}' to '{new_content}'")
            elif operation == 'delete':
                delete_statement_from_memory(memory, content, user_id)
                print(f"Deleted from memory: {content}")
            else:
                logging.error(f"Unknown operation: {operation}")

        # Output all user_id memories for validation
        print("\nCurrent memories:")
        user_memories = memory.get_all(user_id)
        formatted_memories = format_memories(user_memories)
        for single_memory in formatted_memories:
            print(single_memory)

        # Process queries
        for query in test_case.get('queries', []):
            operation = query.get('operation')
            query_content = query.get('content', '')
            expected_answer = query.get('expected_answer', None)

            if operation == 'ask':
                try:
                    # Perform the search operation to retrieve relevant memories
                    response = memory.search(query_content, user_id=user_id)
                    formatted_response = format_memories(response)

                    # Create a prompt and get an LLM response
                    prompt = create_prompt(formatted_response, query_content)
                    llm_response = generate_llm_response(prompt=prompt, provider_name=provider_name, deployment_name=model_name, config=config)

                    # Compare llm_response to expected_answer if it exists
                    is_correct = None
                    if expected_answer is not None:
                        is_correct = (llm_response.strip().lower() == expected_answer.strip().lower())

                    results[test_name]["queries"].append({
                        "query": query_content,
                        "expected_answer": expected_answer,
                        "llm_response": llm_response,
                        "is_correct": is_correct
                    })

                    # Print the results in a readable format
                    print(f"Query: {query_content}")
                    if expected_answer is not None:
                        print(f"Expected Answer: {expected_answer}")
                    print(f"LLM Response: {llm_response}")
                    if is_correct is not None:
                        print(f"Result: {'Correct' if is_correct else 'Incorrect'}\n")
                    else:
                        print("No expected answer provided for comparison.\n")

                except Exception as e:
                    logging.error(f"Error processing query: {query_content}: {e}")
                    continue
            elif operation == 'search':
                # Implement additional logic for 'search' operation if needed
                pass
            else:
                logging.error(f"Unknown query operation: {operation}")

    return results

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="LLM Memory Test Utility")
    parser.add_argument("--input-test-cases", required=True, help="Input JSON file containing test cases.")
    parser.add_argument("--mem0-config", required=True, help="Required path to a Mem0 configuration file.")
    parser.add_argument("--output", required=False, help="Optional output file for logging results.")
    args = parser.parse_args()

    # Redirect stdout to both terminal and file if the output argument is provided
    if args.output:
        sys.stdout = Tee(args.output)

        # Set up the Mem0 memory instance based on the provided model
    MEM0_CONFIG_PATH = args.mem0_config

    # Load mem0 config into json object
    if MEM0_CONFIG_PATH and os.path.exists(MEM0_CONFIG_PATH):
        with open(MEM0_CONFIG_PATH, 'r') as file:
            mem0_config = json.load(file)

    # Clean up existing Qdrant collections before starting tests
    cleanup_qdrant(mem0_config)

    llm_provider = mem0_config['llm']['provider']
    llm_model = mem0_config['llm']['config']['model']

    memory = setup_mem0_memory(mem0_config=MEM0_CONFIG_PATH)

    # Run tests and parse the input JSON file
    results = parse_and_test_json(memory, args.input_test_cases, llm_provider, llm_model)

    # Restore original stdout if it was redirected
    if args.output:
        sys.stdout.log.close()
        sys.stdout = sys.__stdout__

    # Clean up Qdrant collections after tests are completed
    cleanup_qdrant(mem0_config)


if __name__ == "__main__":
    main()
