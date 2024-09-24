# **GenAI Summarization with Memory**

**GenAI Summarization with Memory** is a tool designed to fetch research papers from various sources (currently only used HuggingFace Daily Papers), store them in both a SQLite database and a memory storage system (`mem0`), and interact with a Large Language Model (LLM) for summarization and question answering. This project attempts to leverage memory to enhance the LLM's ability to reference previously stored research papers and related information. Currently due to limitations with mem0, the abstract of each paper is first converted to sound like a diary from the prespective of the researcher before being put into memory by mem0.


## **Features**
- Fetch research papers from customizable sources (e.g., Hugging Face).
- Store research papers and related metadata in a local SQLite database.
- Utilize the `mem0` memory system to store and retrieve memories of papers.
- Query stored research papers in memory or a database.
- Ask questions to an LLM, optionally enhanced by relevant memories.
- Customize the `mem0` configuration using external config files.

## **Installation**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/genai_summarization_with_memory.git
   cd genai_summarization_with_memory

2. **Set up the virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # For Linux/MacOS
   venv\Scripts\activate       # For Windows

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Create a .env file: Set up environment variables in a .env file (such as API keys, endpoint URLs, etc.).**:
   Example:
   ```bash
   QDRANT_URL=http://localhost:6333
   QDRANT_PORT=6333
   AZURE_OPENAI_ENDPOINT=https://your-azure-openai-instance.openai.azure.com
   AZURE_OPENAI_API_KEY=your-openai-api-key
   OPENAI_API_VERSION=v1

## **Installation**

You can customize the behavior of the program using external configuration files or environment variables. The system supports overriding the default mem0 configuration via a JSON config file passed in the --config-file argument.

## **Usage**

The tool is designed around several subcommands, allowing you to fetch, store, query, and interact with research papers and memory storage. Below are examples of each command.

### Main Command

The main command fetches research papers from a specified source URL (default: Hugging Face), stores them in the SQLite database and the mem0 memory system, and processes the papers for future reference.
   ```bash
   python paper_memory_manager.py main --source-url "https://huggingface.co/papers" --config-file path/to/config.json --test
   ```
- `--source-url`: The URL of the paper source (defaults to Hugging Face).
- `--config-file`: Path to the custom `mem0` configuration file (optional).
- `--test`: Run in test mode to only fetch, process, and store one article.

### Query Memory

The query-memory command queries stored memories from the mem0 system.
   ```bash
   python paper_memory_manager.py query-memory --config-file path/to/config.json
   ```
- `--config-file`: Path to the custom `mem0` configuration file (optional).

### Querying Database

The `query-db` command queries the SQLite database for stored research papers and prints them.
   ```bash
   python paper_memory_manager.py query-db
   ```

### Asking Questions to LLM

The `ask-llm` command allows you to ask a question to the LLM, optionally including relevant memories from the `mem0` system.
   ```bash
   python main.py ask-llm --question "What are the latest advancements in AI?" --include-memory --config-file path/to/config.json
   ```
- `--question`: The question you want to ask the LLM (required).
- `--include-memory`: Include relevant stored memories in the prompt to the LLM (optional).
- `--config-file`: Path to the custom `mem0` configuration file (optional).

