# ═══════════════════════════════════════════════════════════════════════════
# app.py — ClinicAssist AI
# Chatbot logic only. All visual code lives in ui/theme.py and ui/components.py
# ═══════════════════════════════════════════════════════════════════════════

import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
from backend import process_query
from ui.theme import CSS
from ui import components as ui

st.set_page_config(
    page_title            = "ClinicAssist AI",
    page_icon             = "⚕️",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

st.markdown(CSS, unsafe_allow_html=True)
ui.render_sidebar_toggle()

# ────────────────────────────────────────────────────────────────────────────
# Session state
# ────────────────────────────────────────────────────────────────────────────
def _init_state():
    for k, v in {
        "messages": [], "lc_messages": [],
        "uploaded_file_path": None,
        "uploaded_file_type": None,
        "uploaded_file_name": None,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ────────────────────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    ui.render_sidebar_brand("ClinicAssist AI", "Multi-agent healthcare assistant")

    st.markdown("---")
    ui.render_microlabel("System status")
    ui.render_status_row("Gemini 2.5 Flash",  bool(os.getenv("GEMINI_API_KEY")))
    ui.render_status_row("LangSmith tracing", bool(os.getenv("LANGCHAIN_API_KEY")))
    ui.render_status_row("Tavily search",     bool(os.getenv("TAVILY_API_KEY")))

    st.markdown("---")
    ui.render_microlabel("Agents")
    ui.render_agent_list()

    st.markdown("---")
    ui.render_microlabel("Upload medical document")
    ui.handle_file_upload()

    st.markdown("---")
    ui.render_microlabel("Clinic hours")
    ui.render_clinic_hours()

    st.markdown("---")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages    = []
        st.session_state.lc_messages = []
        st.rerun()

    if os.getenv("LANGCHAIN_API_KEY"):
        ui.render_langsmith_link()

# ────────────────────────────────────────────────────────────────────────────
# Main page
# ────────────────────────────────────────────────────────────────────────────
ui.render_masthead(
    title       = "ClinicAssist Medical Center",
    subtitle    = "AI-powered healthcare assistant · Dhanmondi, Dhaka · English / বাংলা / Banglish",
    online      = bool(os.getenv("GEMINI_API_KEY")),
    agent_count = 4,
    model_label = "GEMINI 2.5",
)

ui.render_quick_actions()
ui.render_file_chip()

if not st.session_state.messages:
    ui.render_welcome_state()

ui.render_chat_history()

# ────────────────────────────────────────────────────────────────────────────
# Chat input + backend call
# ────────────────────────────────────────────────────────────────────────────
_pending = st.session_state.pop("_qi", "")
user_input = st.chat_input(placeholder="Ask in English, বাংলায়, or Banglish…") or _pending

if user_input:
    disp = (f"*Attached: {st.session_state.uploaded_file_name}*\n\n{user_input}"
            if st.session_state.uploaded_file_name else user_input)

    with st.chat_message("user", avatar="🧑"):
        st.markdown(disp)
    st.session_state.messages.append({"role": "user", "content": disp})

    with st.chat_message("assistant", avatar="⚕️"):
        with st.spinner("Processing your request…"):
            try:
                result = process_query(
                    user_input   = user_input,
                    file_path    = st.session_state.uploaded_file_path,
                    file_type    = st.session_state.uploaded_file_type,
                    chat_history = st.session_state.lc_messages,
                )
                resp       = result["response"]
                agent_used = result.get("route", "general")

                ui.render_agent_badge(agent_used)
                st.markdown(resp)

                st.session_state.messages.append(
                    {"role": "assistant", "content": resp, "agent": agent_used})
                st.session_state.lc_messages.extend([
                    HumanMessage(content=user_input),
                    AIMessage(content=resp),
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
                err = f"**Error:** {e}\n\nCheck that the required API keys are set in `.env`."
                st.error(err)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err, "agent": "general"})

ui.render_footer()
