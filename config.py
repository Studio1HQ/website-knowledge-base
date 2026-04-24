import os
from dotenv import load_dotenv

load_dotenv()

OLOSTEP_API_KEY = os.getenv("OLOSTEP_API_KEY", "")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

COLLECTION_NAME = "WebKnowledgeBase"
MAX_PAGES_DEFAULT = 20
