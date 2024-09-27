import os
from dotenv import load_dotenv

# Load environment variables at the beginning of the program for clarity
load_dotenv()

class Config:
    """Configuration class to hold environment variables."""
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_port = os.getenv("QDRANT_PORT")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.openai_api_version = os.getenv("OPENAI_API_VERSION")
