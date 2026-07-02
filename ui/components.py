# ═══════════════════════════════════════════════════════════════════════════
# ui/components.py — All visual building blocks (masthead, sidebar, chat
# bubbles, welcome state, footer). app.py only calls these; it never
# contains raw HTML/CSS itself.
# ═══════════════════════════════════════════════════════════════════════════

import os
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

AGENT_META = {
    "ocr"    : {"label": "Document Analysis", "badge": "badge-ocr"},
    "rag"    : {"label": "Clinic Information", "badge": "badge-rag"},
    "search" : {"label": "Medical Search",     "badge": "badge-search"},
    "general": {"label": "General Health",     "badge": "badge-general"},
}

QUICK_QUESTIONS = [
    ("CBC-র দাম কত?",        "CBC test er dam koto BDT? Kothay korte hobe?"),
    ("Doctor schedule",       "Cardiologist er schedule ki? Kobe achen?"),
    ("Dengue update",         "Latest dengue fever outbreak Bangladesh 2024"),
    ("Jor hoise, ki korbo?",  "Amar 3 din dhore jor, matha betha. Ki korbo?"),
]


def render_masthead(title: str, subtitle: str, online: bool, agent_count: int, model_label: str):
    """Glowing dark hero banner with gradient wordmark title + live status eyebrow."""
    status_text = "SYSTEM ONLINE" if online else "API KEY MISSING"
    offline_class = "" if online else "offline"
    st.markdown(f"""
    <div class="masthead">
        <div class="mh-inner">
            <div class="eyebrow {offline_class}"><span class="pulse"></span> {status_text} · {agent_count} AGENTS · {model_label}</div>
            <h1>{title}</h1>
            <div class="sub">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_toggle():
    """A custom, always-visible ☰ button fixed at the top-left corner.
    Streamlit's own sidebar collapse control only appears on hover, which
    made it effectively invisible in this dark theme. This button is pure
    CSS (always rendered, never hidden) and a small script bridges its
    click through to whichever native toggle element Streamlit exposes,
    so the real open/close behaviour is reused as-is."""
    st.markdown("""
    <div class="ca-toggle" id="ca-sidebar-toggle" role="button" aria-label="Toggle sidebar" tabindex="0">
        <div class="ca-toggle-bars">
            <span></span><span></span><span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    components.html("""
    <script>
    (function() {
        function bind() {
            try {
                var doc = window.parent.document;
                var toggle = doc.getElementById('ca-sidebar-toggle');
                if (!toggle || toggle.dataset.bound === '1') return;
                toggle.dataset.bound = '1';
                var fire = function() {
                    var selectors = [
                        '[data-testid="stSidebarCollapseButton"] button',
                        '[data-testid="stSidebarCollapsedControl"] button',
                        '[data-testid="collapsedControl"] button',
                        '[data-testid="stSidebarCollapseButton"]',
                        '[data-testid="stSidebarCollapsedControl"]',
                        '[data-testid="collapsedControl"]'
                    ];
                    for (var i = 0; i < selectors.length; i++) {
                        var btn = doc.querySelector(selectors[i]);
                        if (btn) { btn.click(); return; }
                    }
                };
                toggle.addEventListener('click', fire);
                toggle.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fire(); }
                });
            } catch (e) { /* not ready yet, retry below */ }
        }
        bind();
        var attempts = 0;
        var iv = setInterval(function() {
            attempts += 1;
            bind();
            if (attempts > 15) clearInterval(iv);
        }, 300);
    })();
    </script>
    """, height=0)


def render_sidebar_brand(name: str, tagline: str):
    st.markdown(f"""
    <div class="sb-brand">
        <div class="cross">+</div>
        <div>
            <div class="name">{name}</div>
            <div class="tag">{tagline}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_row(label: str, ok: bool):
    st.markdown(
        f'<div class="sb-row"><span><span class="dot {"ok" if ok else "off"}"></span>{label}</span>'
        f'<span class="val">{"ACTIVE" if ok else "NOT SET"}</span></div>',
        unsafe_allow_html=True,
    )


def render_agent_list():
    for key, m in AGENT_META.items():
        st.markdown(
            f'<div class="sb-row"><span>{m["label"]}</span>'
            f'<span class="val">{key.upper()}</span></div>',
            unsafe_allow_html=True,
        )


def render_microlabel(text: str):
    st.markdown(f'<div class="microlabel">{text}</div>', unsafe_allow_html=True)


def render_clinic_hours():
    st.markdown("""
    <div class="sb-hours">
        <b>SAT–THU</b> &nbsp;08:00 – 21:00<br>
        <b>FRIDAY</b> &nbsp;&nbsp;16:00 – 21:00<br>
        <b>EMERGENCY</b> &nbsp;24 / 7<br>
        <b>PHONE</b> &nbsp;&nbsp;&nbsp;+880-1700-000000
    </div>
    """, unsafe_allow_html=True)


def render_langsmith_link():
    st.markdown(
        '<a class="sb-link" href="https://smith.langchain.com" target="_blank">'
        'VIEW LANGSMITH TRACES ↗</a>',
        unsafe_allow_html=True,
    )


def handle_file_upload():
    """Renders the uploader + remove button, writes chosen file to session state."""
    uploaded = st.file_uploader("Upload a document (JPG, PNG, or PDF)",
                                 type=["jpg", "jpeg", "png", "pdf"],
                                 label_visibility="collapsed",
                                 key="sidebar_uploader")
    if uploaded:
        ext = Path(uploaded.name).suffix.lower()
        ftype = "pdf" if ext == ".pdf" else "image"
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(uploaded.read())
        st.session_state.uploaded_file_path = tmp.name
        st.session_state.uploaded_file_type = ftype
        st.session_state.uploaded_file_name = uploaded.name
        st.success(f"Loaded: {uploaded.name}")

    if st.session_state.uploaded_file_name:
        if st.button("Remove file", use_container_width=True):
            p = st.session_state.uploaded_file_path
            if p and os.path.exists(p):
                os.unlink(p)
            st.session_state.uploaded_file_path = None
            st.session_state.uploaded_file_type = None
            st.session_state.uploaded_file_name = None
            st.rerun()


def render_quick_actions():
    """Renders the quick-question buttons; selected text is stashed in session_state['_qi']."""
    render_microlabel("Quick questions")
    cols = st.columns(4)
    for col, (lbl, q) in zip(cols, QUICK_QUESTIONS):
        with col:
            if st.button(lbl, use_container_width=True):
                st.session_state["_qi"] = q
    st.markdown("---")


def render_file_chip():
    if st.session_state.uploaded_file_name:
        st.markdown(
            f'<div class="file-chip">Document attached: '
            f'<code>{st.session_state.uploaded_file_name}</code> '
            f'<span>— type a question below to analyse it.</span></div>',
            unsafe_allow_html=True,
        )


def render_welcome_state():
    st.markdown("""
    <div class="welcome">
        <div class="mark">+</div>
        <h3>How can we help you today?</h3>
        <p>Ask a health question, check clinic services, or upload a medical report from the sidebar.</p>
        <div class="caps">
            <span class="cap">General health guidance</span>
            <span class="cap">Medical report analysis</span>
            <span class="cap">Clinic info &amp; test prices</span>
            <span class="cap">Disease outbreak updates</span>
        </div>
        <div class="lang">EN · বাংলা · BANGLISH SUPPORTED</div>
    </div>
    """, unsafe_allow_html=True)


def render_agent_badge(agent_key: str):
    meta = AGENT_META.get(agent_key, AGENT_META["general"])
    st.markdown(f'<span class="agent-badge {meta["badge"]}">{meta["label"]}</span>',
                unsafe_allow_html=True)


def render_chat_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "⚕️"):
            if msg["role"] == "assistant":
                render_agent_badge(msg.get("agent", "general"))
            st.markdown(msg["content"])


def render_footer():
    st.markdown("""
    <div class="app-footer">
        <b>Medical disclaimer:</b> ClinicAssist AI provides information only and is not a
        substitute for a licensed physician. Always consult a qualified healthcare provider
        for clinical decisions.
        <div class="stack">LANGCHAIN · LANGGRAPH · GEMINI · STREAMLIT · TRACED VIA LANGSMITH</div>
    </div>
    """, unsafe_allow_html=True)
