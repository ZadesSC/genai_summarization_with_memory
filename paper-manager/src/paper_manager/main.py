# src/main/main.py

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../genai_app_utils/src')))

import argparse
from genai_app_utils.config.config import Config
from genai_app_utils.database.database import get_all_papers
from genai_app_utils.memory.memory import get_mem0_memory, query_papers_memory
from genai_app_utils.papers.papers import process_daily_papers
from genai_app_utils.llm.llm import generate_llm_response

def query_memory_command(config, config_file):
    """Subcommand to query stored memories."""
    mem0_memory = get_mem0_memory(config, config_file=config_file)
    query_papers_memory(mem0_memory, "papers_memory")


def query_db_command():
    """Subcommand to query the SQLite database."""
    papers = get_all_papers()
    for paper in papers:
        print(f"ID: {paper['id']}, Title: {paper['title']}, Link: {paper['link']}, Abstract: {paper['abstract']}")
        print("-" * 40)


def ask_llm_command(config, question, include_memory, config_file):
    """Subcommand to ask a question directly to the LLM, optionally including relevant stored memories."""
    mem0_memory = get_mem0_memory(config, config_file=config_file)

    prompt = f"Question: {question}"

    if include_memory:
        print("Searching for relevant memories...")
        search_results = mem0_memory.search(question, "papers_memory")
        
        if 'results' in search_results and search_results['results']:
            prompt += "\n\nRelevant Memories:\n"
            for entry in search_results['results']:
                memory_content = entry.get('memory', 'No content')
                prompt += f"- {memory_content}\n"
        else:
            print("No relevant memories found.")

    response = generate_llm_response(prompt, 'w1', config)
    print(f"LLM Response:\n{response}")


def main():
    parser = argparse.ArgumentParser(
        description='Research Paper Memory Manager',
        usage=(
            "Usage:\n"
            "  paper_memory_manager.py main             # Fetch and store research papers\n"
            "  paper_memory_manager.py query-memory     # Query stored memories from memory\n"
            "  paper_memory_manager.py query-db         # Query the SQLite database for stored papers\n"
            "  paper_memory_manager.py ask-llm          # Ask a question to the LLM\n"
        )
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available subcommands')
    
    # Define the main command for fetching and storing papers
    main_parser = subparsers.add_parser('main', help='Fetch and store research papers')
    main_parser.add_argument('--source-url', type=str, default='https://huggingface.co/papers', 
                             help='The URL source for fetching research papers')
    main_parser.add_argument('--config-file', type=str, help='Path to custom mem0 config file')
    main_parser.add_argument('--test', action='store_true', help='Process only 1 paper for testing')

    # Subcommand for querying memory
    memory_parser = subparsers.add_parser('query-memory', help='Query stored memories from memory')
    memory_parser.add_argument('--config-file', type=str, help='Path to custom mem0 config file')

    # Subcommand for querying the SQLite database
    db_parser = subparsers.add_parser('query-db', help='Query the SQLite database for stored papers')

    # Subcommand for asking LLM questions directly
    ask_llm_parser = subparsers.add_parser('ask-llm', help='Ask a question to the LLM')
    ask_llm_parser.add_argument('--question', type=str, required=True, help='Question to ask the LLM')
    ask_llm_parser.add_argument('--include-memory', action='store_true', help='Include stored memories from Qdrant in the prompt to the LLM')
    ask_llm_parser.add_argument('--config-file', type=str, help='Path to custom mem0 config file')

    args = parser.parse_args()

    config = Config()

    # Handle the subcommands
    if args.command == 'main':
        process_daily_papers(args.source_url, config, args.config_file, args.test)
    elif args.command == 'query-memory':
        query_memory_command(config, args.config_file)
    elif args.command == 'query-db':
        query_db_command()
    elif args.command == 'ask-llm':
        ask_llm_command(config, args.question, args.include_memory, args.config_file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
