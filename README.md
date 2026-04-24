# Website Knowledge Base

A developer tool that turns any live website into a searchable, AI-powered knowledge base. Point it at a documentation site or any URL, and within minutes you can ask natural language questions and get cited answers — powered by **Olostep** for web crawling, **Weaviate** as the vector store, and **Agno** as the intelligence layer with a clean Streamlit UI.

## Architecture

```
User URL
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Olostep  (crawl)                                           │
│  POST /v1/crawls → poll → markdown pages                    │
└────────────────────┬────────────────────────────────────────┘
                     │  clean markdown + metadata
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Weaviate  (store)                                          │
│  Hybrid HNSW collection · text2vec-openai embeddings        │
└────────────────────┬────────────────────────────────────────┘
                     │  semantic / hybrid search
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Agno Agent  (answer)                                       │
│  GPT-5.2 · knowledge-grounded · cites source URLs           │
└────────────────────┬────────────────────────────────────────┘
                     │  streamed markdown response
                     ▼
             Streamlit Chat UI
```

## Prerequisites

- Python 3.11+
- API keys for:
  - **Olostep** — [olostep.com/dashboard/api-keys](https://www.olostep.com/dashboard/api-keys)
  - **Weaviate Cloud** — [console.weaviate.cloud](https://console.weaviate.cloud) (free sandbox available)
  - **OpenAI** — [platform.openai.com/api-keys](https://platform.openai.com/api-keys) (used for embeddings + GPT-5.2)

## Setup

```bash
# 1. Clone / enter the project
cd website-knowledge-base

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and fill in your four API keys

# 4. Run the app
streamlit run app.py
```

## Usage

1. Open the app in your browser (default: http://localhost:8501)
2. In the sidebar, enter a website URL (e.g. `https://docs.agno.com`) and set the max pages to crawl
3. Click **🔍 Crawl & Ingest** — Olostep will crawl the site and store the content in Weaviate
4. Once ingestion is complete, type a question in the chat box and get a cited answer

> **Screenshot placeholder** — add a screenshot of the running app here

## Why these tools?

| Tool | Role | Why |
|------|------|-----|
| **Olostep** | Web crawling | Delivers clean markdown from any site in one API call — no HTML parsing required |
| **Weaviate** | Vector store | Hybrid search (keyword + semantic) out of the box, cloud-hosted with no infra to manage |
| **Agno** | Agent framework | First-class knowledge-base integration with Weaviate, streaming responses, and citation support |

## Project structure

```
website-knowledge-base/
├── app.py          # Streamlit frontend (sidebar + chat UI)
├── agent.py        # Agno agent wired to the Weaviate knowledge base
├── ingest.py       # Olostep crawl → Weaviate ingestion pipeline
├── config.py       # Environment variables and shared constants
├── requirements.txt
└── .env.example
```
