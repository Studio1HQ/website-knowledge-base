import json
import pathlib
import streamlit as st

STATE_FILE = pathlib.Path(__file__).parent / ".app_state.json"


def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"ingested": False, "messages": []}


def _save_state(ingested: bool, messages: list) -> None:
    try:
        STATE_FILE.write_text(
            json.dumps({"ingested": ingested, "messages": messages}, ensure_ascii=False, indent=2)
        )
    except Exception:
        pass


@st.cache_resource
def _get_agent():
    from agent import get_agent
    return get_agent()


st.set_page_config(
    page_title="Web Knowledge Base",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
  /* Dark navy background */
  .stApp { background-color: #0A0F1E; color: #FFFFFF; }
  [data-testid="stSidebar"] { background-color: #0D1425; border-right: 1px solid #1E2A45; }
  [data-testid="stSidebar"] * { color: #FFFFFF !important; }

  /* Input fields */
  .stTextInput input, .stNumberInput input {
    background-color: #1A2340 !important;
    color: #FFFFFF !important;
    border: 1px solid #2A3A60 !important;
    border-radius: 6px !important;
  }

  /* Buttons */
  .stButton button {
    background-color: #635BFF !important;
    color: #0A0F1E !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
  }
  .stButton button:hover { background-color: #4f47e0 !important; }

  /* Chat messages */
  [data-testid="stChatMessage"] {
    background-color: #111827 !important;
    border: 1px solid #1E2A45 !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
  }

  /* Chat input — single line, button stays inline */
  [data-testid="stChatInput"] {
    background-color: #1A2340 !important;
    border: 1px solid #2A3A60 !important;
    border-radius: 8px !important;
  }
  [data-testid="stChatInput"] textarea {
    background-color: #1A2340 !important;
    color: #FFFFFF !important;
    border: none !important;
    min-height: 44px !important;
    max-height: 44px !important;
    resize: none !important;
    padding: 10px 14px !important;
    line-height: 1.4 !important;
  }
  [data-testid="stChatInput"] button {
    background-color: #635BFF !important;
    border-radius: 6px !important;
    margin: 4px !important;
  }

  /* Expander */
  .streamlit-expanderHeader {
    background-color: #1A2340 !important;
    color: #AAAAAA !important;
    font-size: 0.8rem !important;
  }

  /* Success / info boxes */
  .stSuccess { background-color: #0D2818 !important; border-left: 3px solid #635BFF !important; }

  /* Titles */
  h1, h2, h3 { color: #FFFFFF !important; }

  /* Spinner */
  .stSpinner { color: #635BFF !important; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0A0F1E; }
  ::-webkit-scrollbar-thumb { background: #2A3A60; border-radius: 3px; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ──────────────────────────────────────────────────────────────────
col_l, col_c, col_r = st.columns([1, 3, 1])
with col_c:
    st.markdown(
        """
<div style="text-align:center; padding: 20px 0 10px 0;">
  <h1 style="font-size:2rem; font-weight:700; color:#FFFFFF; letter-spacing:-0.5px; margin:0 0 6px 0; display:flex; align-items:center; justify-content:center; gap:12px;">
    Weaviate × Agno Knowledge Base
    <img src="https://weaviate.io/img/site/weaviate-logo-light.png" height="30" alt="Weaviate"/>
  </h1>
  <p style="color:#6B7FA3; margin:0; font-size:0.95rem;">
    Crawl any website · Store in Weaviate · Ask with Agno
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("<hr style='border-color:#1E2A45; margin:0 0 20px 0;'>", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
if "ingested" not in st.session_state:
    _state = _load_state()
    st.session_state.ingested = _state["ingested"]
    st.session_state.messages = _state["messages"]
if "ingest_summary" not in st.session_state:
    st.session_state.ingest_summary = None

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
<div style="padding: 20px 0 8px 0;">
  <img src="https://www.olostep.com/images/olostep-logo-cropped.svg"
       height="26" alt="Olostep"
       style="filter: brightness(0) invert(1);"/>
</div>
<hr style="border-color:#1E2A45; margin: 0 0 20px 0;">
""",
        unsafe_allow_html=True,
    )

    st.markdown("**Ingest a Website**")

    url_input = st.text_input(
        "URL",
        placeholder="https://docs.example.com",
        label_visibility="collapsed",
        key="url_input",
    )
    max_pages = st.number_input(
        "Max pages",
        min_value=1,
        max_value=100,
        value=20,
        step=1,
        key="max_pages",
    )

    if st.button("🔍 Crawl & Ingest", use_container_width=True):
        if not url_input:
            st.error("Please enter a URL.")
        else:
            with st.spinner("Crawling with Olostep..."):
                try:
                    from ingest import ingest_website

                    summary = ingest_website(url_input.strip(), int(max_pages))
                    st.session_state.ingested = True
                    st.session_state.ingest_summary = summary
                    st.session_state.messages = []
                    _save_state(True, [])
                    st.success(
                        f"✅ {summary['pages_crawled']} pages crawled · "
                        f"{summary['chunks_inserted']} chunks stored"
                    )
                except Exception as exc:
                    st.error(f"Ingestion failed: {exc}")

    st.markdown("<hr style='border-color:#1E2A45; margin: 20px 0 12px 0;'>", unsafe_allow_html=True)

    if st.session_state.ingested:
        st.markdown(
            "<span style='color:#635BFF; font-size:0.85rem;'>● Knowledge base ready</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span style='color:#6B7FA3; font-size:0.85rem;'>○ No data ingested yet</span>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div style="position:fixed; bottom:20px; font-size:0.85rem; color:#6B7FA3;">
  Powered by Olostep
</div>
""",
        unsafe_allow_html=True,
    )

# ── Main area ────────────────────────────────────────────────────────────────
if not st.session_state.ingested:
    st.markdown("<br>" * 4, unsafe_allow_html=True)
    st.markdown(
        """
<div style="text-align:center; color:#3A4A6A; padding:60px 20px;">
  <div style="font-size:3rem; margin-bottom:16px;">🌐</div>
  <h3 style="color:#4A5A7A; font-weight:400;">No knowledge base yet</h3>
  <p style="color:#3A4A6A; max-width:400px; margin:0 auto;">
    Enter a website URL in the sidebar and click <strong>Crawl &amp; Ingest</strong>
    to build your searchable knowledge base.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    # ── Chat UI ──────────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("Sources", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(
                            f"<a href='{src}' target='_blank' "
                            f"style='color:#635BFF; font-size:0.85rem;'>{src}</a>",
                            unsafe_allow_html=True,
                        )

    if prompt := st.chat_input("Ask anything about the ingested website…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            status_placeholder = st.empty()
            placeholder = st.empty()
            full_response = ""
            sources = []

            try:
                import time

                agent = _get_agent()
                run_response = agent.run(prompt, stream=True)

                def _show_status(msg: str) -> None:
                    status_placeholder.markdown(
                        f"<span style='color:#6B7FA3; font-size:0.85rem;'>{msg}</span>",
                        unsafe_allow_html=True,
                    )

                _show_status("⏳ Thinking...")
                start = time.time()

                for chunk in run_response:
                    elapsed = time.time() - start
                    if not full_response:
                        if elapsed > 2:
                            _show_status("✍️ Writing response...")
                        elif elapsed > 0.8:
                            _show_status("🔍 Searching knowledge base...")

                    if hasattr(chunk, "content") and chunk.content:
                        full_response += chunk.content
                        status_placeholder.empty()
                        placeholder.markdown(full_response + "▌")

                status_placeholder.empty()
                placeholder.markdown(full_response)

                # Extract cited URLs from the response text
                import re
                sources = list(
                    dict.fromkeys(
                        re.findall(r"https?://[^\s\)\]\>\"']+", full_response)
                    )
                )
                if sources:
                    with st.expander("Sources", expanded=False):
                        for src in sources:
                            st.markdown(
                                f"<a href='{src}' target='_blank' "
                                f"style='color:#635BFF; font-size:0.85rem;'>{src}</a>",
                                unsafe_allow_html=True,
                            )
            except Exception as exc:
                full_response = f"⚠️ Error: {exc}"
                placeholder.markdown(full_response)

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response, "sources": sources}
            )
            _save_state(st.session_state.ingested, st.session_state.messages)
            st.rerun()
