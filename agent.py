import weaviate
from weaviate.auth import AuthApiKey
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.vectordb.weaviate import Weaviate, VectorIndex, Distance
from agno.vectordb.search import SearchType
from agno.knowledge.knowledge import Knowledge
from config import WEAVIATE_URL, WEAVIATE_API_KEY, COLLECTION_NAME


def _build_weaviate_client():
    return weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=AuthApiKey(WEAVIATE_API_KEY),
        skip_init_checks=True,
    )


def get_agent() -> Agent:
    weaviate_client = _build_weaviate_client()
    vector_db = Weaviate(
        collection=COLLECTION_NAME,
        client=weaviate_client,
        search_type=SearchType.hybrid,
        vector_index=VectorIndex.HNSW,
        distance=Distance.COSINE,
    )
    knowledge_base = Knowledge(vector_db=vector_db)

    return Agent(
        model=OpenAIChat(id="gpt-5.2"),
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=(
            "You are a helpful assistant that answers questions based strictly on "
            "the ingested website content. Always cite the source URL of the content "
            "you reference."
        ),
        markdown=True,
    )
