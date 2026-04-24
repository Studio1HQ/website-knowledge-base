import asyncio
from olostep import AsyncOlostep
from config import (
    OLOSTEP_API_KEY,
    WEAVIATE_URL,
    WEAVIATE_API_KEY,
    COLLECTION_NAME,
)



def _get_knowledge_base():
    import weaviate
    from weaviate.auth import AuthApiKey
    from agno.vectordb.weaviate import Weaviate, VectorIndex, Distance
    from agno.vectordb.search import SearchType
    from agno.knowledge.knowledge import Knowledge

    weaviate_client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=AuthApiKey(WEAVIATE_API_KEY),
        skip_init_checks=True,
    )
    vector_db = Weaviate(
        collection=COLLECTION_NAME,
        client=weaviate_client,
        search_type=SearchType.hybrid,
        vector_index=VectorIndex.HNSW,
        distance=Distance.COSINE,
    )
    return Knowledge(vector_db=vector_db)


async def _crawl_and_collect(url: str, max_pages: int) -> list[dict]:
    """Crawl url and return list of {url, markdown_content} dicts."""
    pages = []
    async with AsyncOlostep(api_key=OLOSTEP_API_KEY) as client:
        crawl = await client.crawls.create(url=url, max_pages=max_pages)
        async for page in client.crawls.pages(
            crawl.id, wait_for_completion=True
        ):
            try:
                result = await page.retrieve(formats=["markdown"])
                content = result.markdown_content or ""
                if content.strip():
                    pages.append({"url": page.url, "markdown_content": content})
            except Exception as e:
                print(f"Skipping {page.url}: {e}")
    return pages


def ingest_website(url: str, max_pages: int) -> dict:
    pages = asyncio.run(_crawl_and_collect(url, max_pages))

    knowledge_base = _get_knowledge_base()
    chunks_inserted = 0

    for page in pages:
        try:
            source_url = str(page["url"])
            content = page["markdown_content"]
            knowledge_base.insert(
                text_content=content,
                name=source_url,
                metadata={"source_url": source_url, "title": source_url},
            )
            chunks_inserted += 1
        except Exception as e:
            print(f"Failed to insert {page['url']}: {e}")

    return {
        "pages_crawled": len(pages),
        "chunks_inserted": chunks_inserted,
        "url": url,
    }
