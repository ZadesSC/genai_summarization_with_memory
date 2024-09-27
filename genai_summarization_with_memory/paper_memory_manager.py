import argparse
import requests
import httpx
import sqlite3
import os
import json
from mem0 import Memory
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging

# Load environment variables at the beginning of the program for clarity
load_dotenv()

# Set up logging for error handling and background messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for database and collection names
PAPER_DB_NAME = 'daily_papers.db'
PAPER_QDRANT_COLLECTION_NAME = "papers_collection"


class Config:
    """Configuration class to hold environment variables."""
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_port = os.getenv("QDRANT_PORT")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.openai_api_version = os.getenv("OPENAI_API_VERSION")


def get_mem0_memory(config, model_name='w1', config_file=None):
    """Set up Mem0 memory instance with the provided configuration."""
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as file:
            mem0_config = json.load(file)
    else:
        # Default configuration
        mem0_config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": PAPER_QDRANT_COLLECTION_NAME,
                    "embedding_model_dims": 1536,
                    # Uncomment if needed
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


def generate_llm_response(prompt, deployment_name, config):
    """Generate a response from the Azure LLM."""
    base_url = config.azure_openai_endpoint
    api_key = config.azure_openai_api_key
    api_version = config.openai_api_version

    payload = {
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0,
        "top_p": 0.95,
        "max_tokens": 2000
    }

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = httpx.post(
            f"{base_url}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]

    except (httpx.RequestError, KeyError) as e:
        logging.error(f"Error generating response from Azure LLM: {e}")
        return None


def create_database():
    """Create a SQLite database and table for storing papers."""
    conn = sqlite3.connect(PAPER_DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        abstract TEXT
    )
    ''')
    conn.commit()
    conn.close()


def insert_paper(paper):
    """Insert paper data into the database."""
    conn = sqlite3.connect(PAPER_DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO papers (id, title, link, abstract)
        VALUES (?, ?, ?, ?)
        ''', (paper['id'], paper['title'], paper['link'], paper.get('abstract', '')))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Paper with ID {paper['id']} already exists in the database.")
    conn.close()


def get_all_papers():
    """Query and display all papers from the database."""
    conn = sqlite3.connect(PAPER_DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM papers')
    rows = cursor.fetchall()
    papers = []
    for row in rows:
        paper = {
            'id': row[0],
            'title': row[1],
            'link': row[2],
            'abstract': row[3]
        }
        papers.append(paper)
    conn.close()
    return papers


def make_http_request(url, method="GET", headers=None, params=None, data=None, json_data=None, return_type="json"):
    """
    Make HTTP requests with support for different methods, headers, and return types.
    """
    try:
        method = method.upper()
        response = None

        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, params=params, data=data, json=json_data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, params=params, data=data, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params)
        else:
            return f"Error: Unsupported HTTP method '{method}'"

        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"

        if return_type == "json":
            return response.json()
        elif return_type == "text":
            return response.text
        elif return_type == "html":
            return response.content.decode('utf-8')
        elif return_type == "raw":
            return response.content
        else:
            return f"Error: Unsupported return type '{return_type}'"

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


def get_daily_papers(input_data):
    """Retrieve daily papers from the specified input data source."""
    if input_data.startswith('http'):
        return get_papers_from_url(input_data)
    else:
        # Implement logic to read papers from a file or other sources
        print("Input data source not supported.")
        return []


def get_papers_from_url(url):
    """Retrieve papers from the specified URL."""
    response = make_http_request(url=url, method="GET", return_type="html")
    if isinstance(response, str) and response.startswith("Error"):
        print(response)
        return []

    soup = BeautifulSoup(response, 'html.parser')
    papers = soup.find_all('article')
    return_list = []

    for paper in papers:
        title_tag = paper.find('h3')
        title = title_tag.text.strip() if title_tag else 'No title'
        link_tag = paper.find('a', href=True)
        link = f"https://huggingface.co{link_tag['href']}" if link_tag else 'No link'
        paper_id = link.split('/')[-1]

        print(f"Title: {title}")
        print(f"Link: {link}")
        print(f"Id: {paper_id}")
        print("-" * 40)

        return_paper = {
            "title": title,
            "link": link,
            "id": paper_id
        }
        return_list.append(return_paper)

    return return_list


def extract_abstract_from_url(url):
    """
    Retrieve the abstract section from an HTML page.
    """
    response = make_http_request(
        url=url,
        method='GET',
        return_type='html'
    )
    if not response:
        return "Failed to retrieve the page"

    soup = BeautifulSoup(response, 'html.parser')
    abstract_section = soup.find('blockquote', class_='abstract')
    if not abstract_section:
        return "Abstract not found"

    abstract = abstract_section.get_text(separator=' ', strip=True)
    return abstract


def convert_paper_to_diary_entry(paper, config, model_name):
    """
    Convert a paper to a diary entry from the author's perspective using the LLM.
    """
    diary_prompt = f'''Write a diary entry from the perspective of an author who has just completed a research paper. Reflect on the challenges faced during the research, the key discoveries made, and the significance of the findings. Discuss any innovative methods or frameworks introduced and their implications for the field. Conclude with feelings of pride and anticipation for the community's response to the work. Do not sign off at the end of the diary.

Paper Details:
    ID: {paper['id']}
    Title: {paper['title']}
    Link: {paper['link']}
    Abstract: {paper['abstract']}
    '''

    print(diary_prompt)
    diary_response = generate_llm_response(diary_prompt, model_name, config)
    # print("LLM diary conversion:")
    # print(diary_response)

    return diary_response



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


def query_papers_db():
    """Query and print all papers from the SQLite database."""
    papers = get_all_papers()
    for paper in papers:
        print(f"ID: {paper['id']}, Title: {paper['title']}, Link: {paper['link']}, Abstract: {paper['abstract']}")
        print("-" * 40)
    return


def main_command(config, source_url, config_file, test):
    """Main command to fetch papers and store them."""
    
    # Load custom Mem0 config if provided, otherwise use the default one
    mem0_memory = get_mem0_memory(config, config_file=config_file)

    # Fetch the daily papers from the specified source URL
    daily_papers = get_daily_papers(source_url)

    if not daily_papers:
        print("No papers found or an error occurred.")
        return

    # Iterate over the fetched papers and process them
    paper_count = 0
    for paper in daily_papers:
        paper_id = paper['id']
        arxiv_url = f"https://arxiv.org/abs/{paper_id}"
        
        # Extract the abstract from the corresponding arXiv page
        abstract = extract_abstract_from_url(url=arxiv_url)
        paper['abstract'] = abstract

        # Insert the paper into the SQLite database
        insert_paper(paper)

        # Convert the paper details into a diary entry format and add it to memory
        diary_entry = convert_paper_to_diary_entry(paper, config, 'w1')
        response = mem0_memory.add(diary_entry, "papers_memory")
        print(f"Added memory: {response}")

        paper_count += 1
        # If in test mode, process only 1 paper and break
        if test and paper_count >= 1:
            break

    print(f"Main command: {paper_count} paper(s) processed and stored.")


def query_memory_command(config, config_file):
    """Subcommand to query stored memories."""
    # Load custom mem0 config if provided, otherwise use the default one
    mem0_memory = get_mem0_memory(config, config_file=config_file)
    
    query_papers_memory(mem0_memory, "papers_memory")


def query_db_command():
    """Subcommand to query the SQLite database."""
    query_papers_db()


def ask_llm_command(config, question, include_memory, config_file):
    """Subcommand to ask a question directly to the LLM, optionally including relevant stored memories."""
    # Load custom mem0 config if provided, otherwise use the default one
    mem0_memory = get_mem0_memory(config, config_file=config_file)
    
    # Initialize the prompt with the user's question
    prompt = f"Question: {question}"

    # If --include-memory is enabled, search for relevant memories
    if include_memory:
        print("Searching for relevant memories...")
        # Use the question as the search query
        search_results = mem0_memory.search(question, "papers_memory")
        
        if 'results' in search_results and search_results['results']:
            prompt += "\n\nRelevant Memories:\n"
            for entry in search_results['results']:
                memory_content = entry.get('memory', 'No content')
                prompt += f"- {memory_content}\n"
        else:
            print("No relevant memories found.")

    # Send the prompt to the LLM
    response = generate_llm_response(prompt, 'w1', config)
    
    print(f"LLM Response:\n{response}")


def main():
    # Initialize argument parser with a usage text
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
    
    # Create subparsers for subcommands
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
    ask_llm_parser.add_argument('--include-memory', action='store_true', 
                                help='Include stored memories from Qdrant in the prompt to the LLM')
    ask_llm_parser.add_argument('--config-file', type=str, help='Path to custom mem0 config file')

    # Parse the arguments
    args = parser.parse_args()

    # Load configuration
    config = Config()

    # Handle the subcommands
    if args.command == 'main':
        main_command(config, args.source_url, args.config_file, args.test)
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
