# Supplementary Briefing: Website Knowledge Base — Real Outputs, Errors & UI Guide

> Companion to `BRIEFING.md`. Contains verbatim agent responses, exact error messages,
> ingestion timing data, and precise UI state descriptions for screenshot annotations.

---

## 1. Package Versions (Exact, From Live Environment)

These are the pinned versions installed in the project's `.venv` at the time of writing.

| Package | Version | Role |
|---|---|---|
| `agno` | 2.5.17 | Agent framework, Knowledge abstraction, Weaviate adapter |
| `olostep` | 1.0.4 | Async web crawler SDK |
| `weaviate-client` | 4.20.5 | Weaviate Cloud Python client (v4 API) |
| `openai` | 2.32.0 | GPT-4o model backend |
| `streamlit` | 1.56.0 | Frontend / chat UI |
| `python-dotenv` | (latest) | `.env` loading |

Python runtime: **3.13** (system Python 3.9 lacks `olostep` support — venv with 3.13 is required).

---

## 2. Verbatim Agent Responses

These responses were captured by running the live agent against the `docs.agno.com` knowledge base
(previously ingested into Weaviate at collection `WebKnowledgeBase`). The model is `gpt-4o`.
Agno retrieved **10 documents** per query via hybrid search before generating each answer.

---

### Q1: "What is Agno and what can I build with it?"

```
Agno is a platform for building, running, and managing agentic software at scale.
It provides a range of capabilities to create and deploy agents using its SDK, as
well as operating system-like features for agents through AgentOS. Agno allows
developers to build agents that can connect to various services, manage session
data, and operate as production-ready APIs.

With Agno, you can build applications like:

1. **Text-to-SQL Agents**: These agents can query databases using natural language.
2. **Research Agents**: Agents designed for deep research that provide citations.
3. **Knowledge Agents**: These answer questions from a knowledge base.

Agno supports deploying these applications in various environments, such as Docker,
Railway, or AWS, and allows for integration with platforms like Slack or Discord to
expose your agents to end-users.

For more information, you can visit the Agno website at https://docs.agno.com and
explore specifics on building your first agent at https://docs.agno.com/first-agent.
```

**Agno's RAG log:** `INFO Found 10 documents`

---

### Q2: "How do I add a knowledge base to an Agno agent?"

```
To add a knowledge base to an Agno agent, you can utilize the "Knowledge Agent"
which is designed to answer questions from your knowledge base. You will need to
deploy AgentOS and customize it according to your use case. You can see this
concept in the deployment and customization phases described on the Agno
documentation here: https://docs.agno.com/production/overview

For detailed steps on deploying and customizing your agent to integrate a knowledge
base, you may refer to the overview page which outlines the steps needed to deploy,
customize, and connect your agent within your environment.
```

**Agno's RAG log:** `INFO Found 10 documents`

> **Note for writer:** The agent gave a higher-level answer here because `docs.agno.com`'s
> ingested pages skewed toward overview/production content rather than SDK tutorials.
> This illustrates how knowledge base *coverage* shapes answer quality — a good angle
> to cover in an article.

---

### Q3: "What vector databases does Agno support?"

```
I couldn't find specific information on which vector databases Agno supports from
the ingested content. You can explore the Agno documentation at https://docs.agno.com
for more detailed information or contact their support for precise technical inquiries.
```

**Agno's RAG log:** `INFO Found 10 documents` (×2 — Agno performed a second search pass)

> **Note for writer:** This is an honest "I don't know" — the crawled pages didn't
> include the vector DB reference pages. The agent refused to hallucinate. Good example
> of the system being *faithfully limited* to its ingested data.

---

### Q4: "What is the difference between an Agent and a Team in Agno?"

```
I couldn't find specific details on the difference between an "Agent" and a "Team"
in Agno from the current available resources. It's possible that this information
is not provided in the publicly available documentation. For more detailed or
specific inquiries, you might consider reaching out through Agno's getting help
resources at https://docs.agno.com/get-help or their community support channels.

For more information, you can visit the Agno documentation at docs.agno.com.
```

**Agno's RAG log:** `INFO Found 10 documents` (×2 — second search pass triggered)

> **Note for writer:** Same pattern as Q3. A richer crawl (more pages, or targeted
> subsections) would yield better answers. Another article-worthy point: the
> `max_pages` slider directly controls answer depth.

---

## 3. Error States — Exact UI Text

### Error 1: Empty URL field, user clicks "Crawl & Ingest"

**Trigger:** Leave the URL field blank and click the button.

**UI output (red error box):**
```
Please enter a URL.
```

**Code path:** `app.py` lines 180–181 — `if not url_input: st.error("Please enter a URL.")`

**Visual:** Red `st.error()` banner below the Crawl & Ingest button, within the sidebar.

---

### Error 2: Invalid or unreachable URL

**Trigger:** Enter a URL that Olostep cannot crawl (e.g., `https://not-a-real-domain-xyz.com`).

**UI output (red error box):**
```
Ingestion failed: <exception message from Olostep SDK>
```

**Code path:** `app.py` lines 196–197 — the `except Exception as exc` block around `ingest_website()`.

**Visual:** Red `st.error()` banner in sidebar. Spinner disappears. `ingested` state stays `False`.
The main panel continues showing the empty-state globe icon.

---

### Error 3: Missing API keys (`.env` not configured)

**Trigger:** Run the app without a `.env` file or with blank values for `OLOSTEP_API_KEY`,
`WEAVIATE_URL`, `WEAVIATE_API_KEY`, or `OPENAI_API_KEY`.

**UI output (red error box, during crawl attempt):**
```
Ingestion failed: API key is required when using the real HTTP transport
```

**Code path:** Olostep's `AsyncOlostep(api_key="")` raises this exception immediately.
The `.env` file must be present and populated before starting the app.

**Fix shown in article:** Copy `.env.example` → `.env` and fill in real credentials.

---

### Error 4: Agent query fails (e.g., OpenAI API key invalid)

**Trigger:** Valid data in Weaviate, user submits a question, but OpenAI key is invalid.

**UI output (inline in assistant chat bubble):**
```
⚠️ Error: <exception message from OpenAI SDK>
```

**Code path:** `app.py` lines 308–310 — `except Exception as exc` inside the chat
response block. The error is rendered inside the assistant's `st.chat_message()` bubble
so it appears inline with the conversation.

**Visual:** The ⚠️ prefix makes it visually distinct from a normal response. The chat
history is saved with this error message so it persists across refreshes.

---

## 4. Ingestion Timing Benchmarks

Timing is dominated by two sequential phases:

1. **Olostep crawl phase** — network I/O, scales with `max_pages` and site complexity.
   Olostep crawls pages in parallel internally; wall time does not scale 1:1 with page count.
2. **Weaviate insert phase** — one `knowledge_base.insert()` call per page; each call
   triggers an OpenAI embedding (via Agno/Weaviate's auto-vectorization) and a Weaviate upsert.

**Approximate timing on `docs.agno.com` over typical broadband:**

| max_pages | Pages crawled | Chunks inserted | Estimated wall time |
|---|---|---|---|
| 5 | 5 | 5 | ~25–40 s |
| 10 | 10 | 10 | ~45–70 s |
| 20 | 20 | 20 | ~90–140 s |
| 30 | 30 | 30 | ~2–4 min |

> **Note:** "Chunks inserted" equals "pages crawled" in this implementation — one
> Weaviate document per crawled page. Each document may be split into multiple
> embedding vectors internally by Weaviate, but the app only calls `insert()` once
> per page. The success toast shows both numbers: `✅ 20 pages crawled · 20 chunks stored`.

**During crawl:** The sidebar spinner displays `Crawling with Olostep...` with no progress
bar — it is a blocking call. The UI is unresponsive until `ingest_website()` returns.

---

## 5. UI State Descriptions (For Screenshot Annotations)

### State A: Empty / No Data Ingested

**Sidebar:**
- Olostep logo (white, top-left), horizontal rule
- Bold text: "Ingest a Website"
- URL text input (placeholder: `https://docs.example.com`), dark navy background
- Number input labeled "Max pages", default value 20
- Purple button: "🔍 Crawl & Ingest", full sidebar width
- Horizontal rule
- Status badge: grey circle `○ No data ingested yet` (color `#6B7FA3`)
- Footer (fixed bottom): "Powered by Olostep" in grey

**Main panel:**
- Center-aligned: globe emoji `🌐` (3rem, grey)
- Subheading: "No knowledge base yet" (muted blue-grey)
- Body text: "Enter a website URL in the sidebar and click **Crawl & Ingest** to build
  your searchable knowledge base."
- No chat input visible

---

### State B: Ingestion In Progress

**Sidebar:**
- Spinner animation replacing the button content: `Crawling with Olostep...`
- All other sidebar elements unchanged and non-interactive

**Main panel:** Unchanged from State A (globe + empty state text).

---

### State C: Ingested, Ready to Chat

**Sidebar:**
- Status badge changes to: purple filled circle `● Knowledge base ready` (color `#635BFF`)
- All input controls remain editable (user can crawl a new site)

**Main panel:**
- Empty chat history (if first session) — no messages shown
- Chat input bar visible at the bottom, dark navy background, single-line height (44 px)
  with inline send button (purple, `#635BFF`) on the right edge
- Placeholder text: `Ask anything about the ingested website…`

---

### State D: Active Conversation

**Message layout:**
- **User messages:** Default Streamlit chat bubble, no avatar, flush-left label
- **Assistant messages:** `🤖` avatar, dark card background `#111827`, 1 px border `#1E2A45`,
  10 px border radius

**Streaming animation:**
- A blinking cursor character `▌` appended to the assistant text while streaming
- Status label above response transitions: `⏳ Thinking...` → `🔍 Searching knowledge base...`
  (after 0.8 s) → `✍️ Writing response...` (after 2 s) → disappears when first text arrives

**After response completes:**
- If the response contains HTTP URLs: a collapsed `Sources` expander appears below the
  assistant bubble, listing each URL as a clickable purple link (`color: #635BFF`)
- `st.rerun()` is called, re-rendering the full conversation history cleanly

**Scrolling:** Streamlit auto-scrolls to the latest message on `st.rerun()`.

---

## 6. Architecture Cheat-Sheet (For Diagrams)

```
Browser → Streamlit (app.py)
              │
    ┌─────────┴──────────┐
    │                    │
  Sidebar              Main panel
  [URL input]          [Chat history]
  [Crawl button]       [Chat input]
    │                    │
    ▼                    ▼
 ingest.py            agent.py
    │                    │
    ├── AsyncOlostep      ├── OpenAIChat (gpt-4o)
    │   (crawl + pages)  │
    │                    ├── Agno Knowledge
    └── Agno Knowledge        (search_knowledge=True)
         │                    │
         └────── Weaviate Cloud ──────┘
                 (HNSW + Hybrid search)
                 collection: WebKnowledgeBase

State persistence: .app_state.json (local file)
  { "ingested": bool, "messages": [...] }
```

**Data flow on question:**
1. User types question → `agent.run(prompt, stream=True)`
2. Agno auto-calls `search_knowledge` → hybrid query to Weaviate → top-10 docs returned
3. Docs injected into GPT-4o system context alongside the question
4. GPT-4o streams tokens → app renders `▌` cursor in real time
5. Response saved to `.app_state.json` → `st.rerun()` cleanly re-renders history

**Data flow on ingestion:**
1. `asyncio.run(_crawl_and_collect(url, max_pages))` → Olostep crawl job created
2. Async iterator yields pages as they complete → markdown extracted per page
3. Each page markdown → `knowledge_base.insert(text_content=..., name=url, metadata={...})`
4. Weaviate auto-vectorizes via OpenAI embeddings → stored in HNSW index
5. Summary dict returned → `st.success("✅ N pages crawled · N chunks stored")`

---

*Generated 2026-04-17. Verbatim agent responses captured from live `gpt-4o` + Weaviate
instance against `docs.agno.com` knowledge base. Package versions from `.venv` pip freeze.*
