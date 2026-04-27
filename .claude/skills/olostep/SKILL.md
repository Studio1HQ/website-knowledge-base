---
name: olostep
description: This skill should be used when writing code that uses the Olostep SDK, crawls websites, handles the crawl lifecycle, or extracts clean markdown content from pages. Use it whenever the user mentions Olostep, web crawling, or ingesting website content.
version: 1.0.0
---

# Olostep Skill

Correct patterns for using the Olostep Python SDK to crawl websites and extract clean markdown content.

## Installation

```bash
pip install olostep
```

## Client setup

Always use the async client and manage it as a context manager so connections are properly closed:

```python
from olostep import AsyncOlostep

async with AsyncOlostep(api_key=OLOSTEP_API_KEY) as client:
    # all crawl operations go here
```

## Starting a crawl

```python
crawl = await client.crawls.create(url=url, max_pages=max_pages)
```

- `url` — the root URL to start crawling from
- `max_pages` — cap on how many pages Olostep will visit

## Iterating over pages

Use `client.crawls.pages()` with `wait_for_completion=True` to stream pages as they finish. This avoids manual polling:

```python
async for page in client.crawls.pages(crawl.id, wait_for_completion=True):
    result = await page.retrieve(formats=["markdown"])
    content = result.markdown_content or ""
    if content.strip():
        # process the page
        print(page.url, content[:200])
```

## Extracting markdown

Always request `formats=["markdown"]` in `page.retrieve()`. Guard against empty content before processing:

```python
result = await page.retrieve(formats=["markdown"])
content = result.markdown_content or ""
if not content.strip():
    continue  # skip empty pages
```

## Error handling

Wrap individual page retrieval in try/except so a single failed page doesn't abort the whole crawl:

```python
async for page in client.crawls.pages(crawl.id, wait_for_completion=True):
    try:
        result = await page.retrieve(formats=["markdown"])
        content = result.markdown_content or ""
        if content.strip():
            pages.append({"url": page.url, "markdown_content": content})
    except Exception as e:
        print(f"Skipping {page.url}: {e}")
```

## Running async code from sync context

Use `asyncio.run()` to call async crawl functions from a synchronous entry point:

```python
import asyncio

def ingest_website(url: str, max_pages: int) -> list[dict]:
    return asyncio.run(_crawl_and_collect(url, max_pages))
```

## What to avoid

- Do not use `requests` or `httpx` directly to scrape pages — Olostep handles JS rendering, redirects, and rate limiting.
- Do not poll crawl status manually — use `wait_for_completion=True` in `crawls.pages()`.
- Do not assume `markdown_content` is always populated — always fall back to `""` and check `.strip()`.
