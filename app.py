# ═══════════════════════════════════════════════════════════════════════════
# ClinicAssist AI — app.py  |  Full Dark Theme
# ═══════════════════════════════════════════════════════════════════════════

import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
from backend import process_query

st.set_page_config(
    page_title            = "ClinicAssist AI",
    page_icon             = "🏥",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

# ── Full Dark Theme CSS ───────────────────────────────────────────────────
st.markdown("""
<style>

/* ── MAIN BACKGROUND ─────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="block-container"],
section.main, .main {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}

/* ── ALL MAIN TEXT ───────────────────────────────────────────────── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] b,
[data-testid="stMarkdownContainer"] a,
.stMarkdown p, .stMarkdown li {
    color: #e6edf3 !important;
}

/* ── CHAT MESSAGES ───────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    margin-bottom: 8px;
}
[data-testid="stChatMessageContent"] *,
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessageContent"] span,
[data-testid="stChatMessageContent"] div,
[data-testid="stChatMessageContent"] strong,
[data-testid="stChatMessageContent"] b,
[data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessageContent"] h3,
[data-testid="stChatMessageContent"] td,
[data-testid="stChatMessageContent"] th {
    color: #e6edf3 !important;
}

/* ── TABLE IN CHAT ───────────────────────────────────────────────── */
[data-testid="stChatMessageContent"] table {
    background: #161b22 !important;
    border-collapse: collapse;
    width: 100%;
}
[data-testid="stChatMessageContent"] th {
    background: #1f2937 !important;
    color: #7dd3fc !important;
    padding: 8px;
    border: 1px solid #30363d;
}
[data-testid="stChatMessageContent"] td {
    color: #e6edf3 !important;
    padding: 7px;
    border: 1px solid #30363d;
}
[data-testid="stChatMessageContent"] tr:nth-child(even) td {
    background: #1a2030 !important;
}

/* ── SIDEBAR ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0a1628 0%, #0f2244 60%, #0a1a36 100%) !important;
    border-right: 1px solid #1e3a5f !important;
}
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: #c9d8f0 !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #c9d8f0 !important;
    border-radius: 8px;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: rgba(255,255,255,0.3) !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px dashed rgba(255,255,255,0.2) !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
    color: #7eaad4 !important;
}

/* ── QUICK ACTION BUTTONS ────────────────────────────────────────── */
div[data-testid="column"] .stButton > button {
    border-radius: 20px;
    font-size: 12px;
    padding: 6px 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #7dd3fc !important;
    transition: all 0.2s;
    width: 100%;
}
div[data-testid="column"] .stButton > button:hover {
    background: #1f2937 !important;
    border-color: #3b82f6 !important;
    color: #93c5fd !important;
}

/* ── CLINIC HERO HEADER ──────────────────────────────────────────── */
.clinic-header {
    background: linear-gradient(135deg, #1a4a8a 0%, #1d6fd4 100%);
    color: white;
    padding: 22px 28px;
    border-radius: 14px;
    margin-bottom: 18px;
    box-shadow: 0 4px 24px rgba(29,111,212,0.4);
    border: 1px solid rgba(255,255,255,0.1);
}
.clinic-header h2 { margin: 0 0 4px 0; font-size: 26px; font-weight: 700; color: white !important; }
.clinic-header p  { margin: 0; font-size: 14px; opacity: 0.85; color: #bfdbfe !important; }

/* ── AGENT BADGES ────────────────────────────────────────────────── */
.agent-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 600;
    margin-bottom: 8px;
    letter-spacing: 0.4px;
}
.badge-ocr     { background: #1e3a5f !important; color: #7dd3fc !important; border: 1px solid #2563eb; }
.badge-rag     { background: #14422a !important; color: #6ee7b7 !important; border: 1px solid #059669; }
.badge-search  { background: #3d2a00 !important; color: #fbbf24 !important; border: 1px solid #d97706; }
.badge-general { background: #2d1f4a !important; color: #c4b5fd !important; border: 1px solid #7c3aed; }

/* ── FILE BANNER ─────────────────────────────────────────────────── */
.file-banner {
    background: #1e3a5f !important;
    border: 1px solid #2563eb;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 12px;
    font-size: 13px;
    color: #93c5fd !important;
}
.file-banner code {
    background: rgba(255,255,255,0.1) !important;
    color: #7dd3fc !important;
    padding: 1px 5px;
    border-radius: 4px;
}

/* ── WELCOME BOX ─────────────────────────────────────────────────── */
.welcome-box {
    text-align: center;
    padding: 50px 20px;
}
.welcome-box h3 { color: #7dd3fc !important; margin-bottom: 10px; }
.welcome-box p  { color: #8b949e !important; }

/* ── CHAT INPUT ──────────────────────────────────────────────────── */
[data-testid="stChatInputTextArea"],
[data-testid="stChatInputTextArea"] textarea {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
}

/* ── DIVIDER ─────────────────────────────────────────────────────── */
hr { border-color: #30363d !important; }

/* ── QUICK QUESTIONS LABEL ───────────────────────────────────────── */
.stMarkdown strong { color: #e6edf3 !important; }

/* ── FOOTER ──────────────────────────────────────────────────────── */
.footer {
    text-align: center;
    color: #484f58 !important;
    font-size: 12px;
    padding: 14px 0 6px 0;
    border-top: 1px solid #21262d;
    margin-top: 10px;
}

/* ── SPINNER ─────────────────────────────────────────────────────── */
[data-testid="stSpinner"] * { color: #7dd3fc !important; }

/* ── SUCCESS BOX IN SIDEBAR ──────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(6, 78, 59, 0.3) !important;
    border: 1px solid #059669 !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] * {
    color: #6ee7b7 !important;
}

</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# Session State
# ────────────────────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "messages": [], "lc_messages": [],
        "uploaded_file_path": None,
        "uploaded_file_type": None,
        "uploaded_file_name": None,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

AGENT_META = {
    "ocr"    : {"label": "📄 Document Analysis Agent", "badge": "badge-ocr",     "icon": "📄"},
    "rag"    : {"label": "📚 Clinic Info Agent",        "badge": "badge-rag",     "icon": "📚"},
    "search" : {"label": "🌐 Medical Search Agent",     "badge": "badge-search",  "icon": "🌐"},
    "general": {"label": "🩺 General Health Agent",     "badge": "badge-general", "icon": "🩺"},
}

# ────────────────────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:8px 0 20px 0;">
        <div style="font-size:52px; line-height:1;">🏥</div>
        <div style="font-size:22px; font-weight:700; margin-top:8px; color:#e8f2ff;">ClinicAssist AI</div>
        <div style="font-size:11.5px; color:#7eaad4; margin-top:4px;">
            Multi-Agent Healthcare Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**🔧 System Status**")

    def _s(label, ok):
        st.markdown(f"{'🟢' if ok else '🔴'} **{label}:** {'Active' if ok else 'Not Set'}")

    _s("OpenAI GPT-4o",     bool(os.getenv("OPENAI_API_KEY")))
    _s("LangSmith Tracing", bool(os.getenv("LANGCHAIN_API_KEY")))
    _s("Tavily Search",     bool(os.getenv("TAVILY_API_KEY")))

    st.markdown("---")
    st.markdown("**🤖 Available Agents**")
    for m in AGENT_META.values():
        st.markdown(f"{m['icon']} {m['label']}")

    st.markdown("---")
    st.markdown("**📎 Upload Medical Document**")
    st.markdown("<small style='color:#7eaad4;'>Supports: JPG · PNG · PDF</small>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload", type=["jpg","jpeg","png","pdf"],
                                label_visibility="collapsed", key="sidebar_uploader")
    if uploaded:
        ext = Path(uploaded.name).suffix.lower()
        ftype = "pdf" if ext == ".pdf" else "image"
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(uploaded.read())
        st.session_state.uploaded_file_path = tmp.name
        st.session_state.uploaded_file_type = ftype
        st.session_state.uploaded_file_name = uploaded.name
        st.success(f"✅ {uploaded.name}")

    if st.session_state.uploaded_file_name:
        if st.button("🗑️ Remove File", use_container_width=True):
            p = st.session_state.uploaded_file_path
            if p and os.path.exists(p): os.unlink(p)
            st.session_state.uploaded_file_path = None
            st.session_state.uploaded_file_type = None
            st.session_state.uploaded_file_name = None
            st.rerun()

    st.markdown("---")
    st.markdown("**🕐 Clinic Hours**")
    st.markdown("""
    <div style="font-size:12.5px; line-height:1.9; color:#7eaad4;">
        📅 Sat–Thu: 8:00 AM – 9:00 PM<br>
        📅 Friday: 4:00 PM – 9:00 PM<br>
        🚨 Emergency: 24 / 7<br>
        📞 +880-1700-000000
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages    = []
        st.session_state.lc_messages = []
        st.rerun()

    if os.getenv("LANGCHAIN_API_KEY"):
        st.markdown("""
        <a href="https://smith.langchain.com" target="_blank"
           style="display:block;text-align:center;margin-top:10px;
                  background:rgba(255,255,255,0.07);color:#7eaad4;
                  padding:9px 0;border-radius:9px;text-decoration:none;
                  font-size:12.5px;border:1px solid rgba(255,255,255,0.12);">
            🔍 View LangSmith Traces
        </a>
        """, unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# Main Content
# ────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="clinic-header">
    <h2>🏥 ClinicAssist Medical Center</h2>
    <p>AI-Powered Multi-Agent Healthcare Assistant &nbsp;·&nbsp;
       Dhanmondi, Dhaka &nbsp;·&nbsp;
       English · বাংলা · Banglish supported</p>
</div>
""", unsafe_allow_html=True)

st.markdown("**⚡ Quick Questions:**")
col1, col2, col3, col4 = st.columns(4)
QUICK = [
    ("💉 CBC-র দাম কত?",       "CBC test er dam koto BDT? Kothay korte hobe?"),
    ("👨‍⚕️ Doctor schedule",    "Cardiologist er schedule ki? Kobe achen?"),
    ("🦟 Dengue update",        "Latest dengue fever outbreak Bangladesh 2024"),
    ("🤒 Jor hoise ki korbo?",  "Amar 3 din dhore jor, matha betha. Ki korbo?"),
]
for col, (lbl, q) in zip([col1, col2, col3, col4], QUICK):
    with col:
        if st.button(lbl, use_container_width=True):
            st.session_state["_qi"] = q

st.markdown("---")

if st.session_state.uploaded_file_name:
    st.markdown(
        f'<div class="file-banner">📎 <b>File loaded:</b> '
        f'<code>{st.session_state.uploaded_file_name}</code> — '
        f'Type your question and press Enter to analyse.</div>',
        unsafe_allow_html=True,
    )

# Chat display
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        <div style="font-size:56px;margin-bottom:14px;">💬</div>
        <h3>Welcome to ClinicAssist AI</h3>
        <p style="font-size:15px;">I can help you with:</p>
        <p style="color:#8b949e;">
            🩺 General health questions &nbsp;|&nbsp; 📄 Medical report analysis<br>
            📚 Clinic info &amp; test prices &nbsp;|&nbsp; 🌐 Disease outbreak updates
        </p>
        <p style="font-size:13px;color:#484f58;margin-top:12px;">
            ✨ English, বাংলা, এবং Banglish — সবই বুঝি! 😊
        </p>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"]=="user" else "🏥"):
        if msg["role"] == "assistant":
            meta = AGENT_META.get(msg.get("agent","general"), AGENT_META["general"])
            st.markdown(f'<span class="agent-badge {meta["badge"]}">{meta["label"]}</span>',
                        unsafe_allow_html=True)
        st.markdown(msg["content"])

# Chat input
_q = st.session_state.pop("_qi", "")
user_input = st.chat_input(
    placeholder="Ask in English, বাংলায়, or Banglish..."
) or _q

if user_input:
    disp = f"📎 *[{st.session_state.uploaded_file_name}]*\n\n{user_input}" \
           if st.session_state.uploaded_file_name else user_input

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(disp)
    st.session_state.messages.append({"role":"user","content":disp})

    with st.chat_message("assistant", avatar="🏥"):
        with st.spinner("🔄 Processing..."):
            try:
                result = process_query(
                    user_input   = user_input,
                    file_path    = st.session_state.uploaded_file_path,
                    file_type    = st.session_state.uploaded_file_type,
                    chat_history = st.session_state.lc_messages,
                )
                resp       = result["response"]
                agent_used = result.get("route", "general")
                meta       = AGENT_META.get(agent_used, AGENT_META["general"])

                st.markdown(f'<span class="agent-badge {meta["badge"]}">{meta["label"]}</span>',
                            unsafe_allow_html=True)
                st.markdown(resp)

                st.session_state.messages.append({"role":"assistant","content":resp,"agent":agent_used})
                st.session_state.lc_messages.extend([
                    HumanMessage(content=user_input),
                    AIMessage(content=resp)
                ])
                if len(st.session_state.lc_messages) > 20:
                    st.session_state.lc_messages = st.session_state.lc_messages[-20:]

                if st.session_state.uploaded_file_path:
                    try:
                        if os.path.exists(st.session_state.uploaded_file_path):
                            os.unlink(st.session_state.uploaded_file_path)
                    except OSError:
                        pass
                    st.session_state.uploaded_file_path = None
                    st.session_state.uploaded_file_type = None
                    st.session_state.uploaded_file_name = None

            except Exception as e:
                err = f"❌ **Error:** {e}\n\nPlease check your API keys."
                st.error(err)
                st.session_state.messages.append({"role":"assistant","content":err,"agent":"general"})

st.markdown("""
<div class="footer">
    ⚕️ <b>Medical Disclaimer:</b> ClinicAssist AI is an information assistant only.
    NOT a substitute for a licensed doctor. Always consult a qualified healthcare provider.<br><br>
    🔍 Traced via <b>LangSmith</b> · Built with <b>LangChain · LangGraph · Gemini · Streamlit</b>
</div>
""", unsafe_allow_html=True)
