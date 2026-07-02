# ═══════════════════════════════════════════════════════════════════════════
# ui/theme.py — "Aurora Console" dark theme (COSMOQ-inspired glow aesthetic)
# Import CSS and inject once from app.py:  st.markdown(CSS, unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════════════

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg:       #060608;
    --surface:  #0d1016;
    --surface2: #11141b;
    --ink:      #F4F6F9;
    --muted:    #8A94A6;
    --faint:    #5B6472;
    --line:     rgba(255,255,255,0.09);
    --line-soft:rgba(255,255,255,0.06);
    --orange:   #FF8A3D;
    --blue:     #3A8BFF;
    --grad:     linear-gradient(90deg, #FF8A3D 0%, #FFCF6B 18%, #FFFFFF 38%, #FFFFFF 62%, #6FD6FF 78%, #3A8BFF 100%);
    --teal-bg:  rgba(58,139,255,0.12);
    --teal-ink: #7EC4FF;
    --amber-bg: rgba(255,190,90,0.12);  --amber-ink: #FFC876;
    --green-bg: rgba(74,222,128,0.12);  --green-ink: #4ADE80;
    --blue-bg:  rgba(58,139,255,0.12);  --blue-ink:  #6FB4FF;
    --violet-bg:rgba(167,139,250,0.14); --violet-ink:#C4B5FD;
    --red:      #F0645C;
    --radius:   14px;
    --shadow:   0 8px 30px rgba(0,0,0,0.45);
}

/* ── Base ────────────────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main, .main {
    background-color: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}
[data-testid="stMainBlockContainer"],
[data-testid="block-container"] {
    background-color: var(--bg) !important;
    max-width: 1060px !important;
    padding-top: 1.4rem !important;
}
#MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden; }

/* ── Hide Streamlit chrome: Deploy button + running-man spinner ───── */
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"] {
    visibility: hidden !important;
    display: none !important;
}

/* The zero-height helper iframe used to bridge the custom sidebar
   toggle's click through to Streamlit's native control — no border,
   no stray gap in the layout. */
iframe { border: none !important; }

/* faint ambient glows behind the whole app */
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    width: 520px; height: 520px;
    border-radius: 50%;
    filter: blur(150px);
    opacity: 0.16;
    z-index: 0;
    pointer-events: none;
}
[data-testid="stAppViewContainer"]::before { background: var(--orange); top: -220px; left: -220px; }
[data-testid="stAppViewContainer"]::after  { background: var(--blue);   bottom: -220px; right: -220px; }

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div,
.stMarkdown p, .stMarkdown li { color: var(--ink); }

h1, h2, h3 { font-family: 'Sora', sans-serif !important; }

hr { border-color: var(--line) !important; margin: 0.9rem 0 !important; }

/* ── Micro-label ─────────────────────────────────────────────────── */
.microlabel {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10.5px;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--faint);
    margin: 4px 0 10px 0;
}

/* ── Masthead (glowing hero card) ───────────────────────────────── */
.masthead {
    position: relative;
    overflow: hidden;
    background: radial-gradient(120% 140% at 50% -10%, #12151d 0%, var(--surface) 55%, #030304 100%);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 28px 30px 26px 30px;
    margin-bottom: 18px;
    box-shadow: var(--shadow);
    text-align: center;
}
.masthead::before, .masthead::after {
    content: "";
    position: absolute;
    width: 300px; height: 300px;
    border-radius: 50%;
    filter: blur(110px);
    opacity: 0.45;
    z-index: 0;
}
.masthead::before { background: var(--orange); top: -120px; left: -100px; }
.masthead::after  { background: var(--blue);   bottom: -140px; right: -100px; }

.masthead .mh-inner { position: relative; z-index: 2; }

.masthead .eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--muted);
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--line);
    padding: 5px 12px; border-radius: 999px; margin-bottom: 16px;
}
.masthead .eyebrow .pulse {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green-ink);
    box-shadow: 0 0 0 3px rgba(74,222,128,0.18);
}
.masthead .eyebrow.offline .pulse { background: var(--red); box-shadow: 0 0 0 3px rgba(240,100,92,0.18); }

.masthead h1 {
    margin: 0;
    font-weight: 800;
    font-size: clamp(24px, 4vw, 34px);
    letter-spacing: -0.01em;
    background: var(--grad);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 26px rgba(120,170,255,0.18));
    line-height: 1.15;
}
.masthead .sub {
    font-size: 13px;
    color: var(--muted);
    margin-top: 8px;
}

/* ── Status dots ─────────────────────────────────────────────────── */
.dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 7px;
    vertical-align: 1px;
}
.dot.ok  { background: var(--green-ink); box-shadow: 0 0 0 3px rgba(74,222,128,0.14); }
.dot.off { background: var(--red);       box-shadow: 0 0 0 3px rgba(240,100,92,0.14); }

/* ── Quick action buttons ────────────────────────────────────────── */
div[data-testid="column"] .stButton > button {
    width: 100%;
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    color: var(--ink) !important;
    border-radius: 10px !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    padding: 10px 12px !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: border-color .15s, background .15s, transform .15s;
    box-shadow: none !important;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: rgba(58,139,255,0.5) !important;
    background: var(--surface2) !important;
    color: #fff !important;
    transform: translateY(-1px);
}
div[data-testid="column"] .stButton > button:focus-visible {
    outline: 2px solid var(--blue) !important;
    outline-offset: 2px;
}

/* ── Chat messages ───────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--radius) !important;
    padding: 14px 16px !important;
    margin-bottom: 10px;
    box-shadow: var(--shadow);
}
[data-testid="stChatMessageContent"] *,
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessageContent"] td,
[data-testid="stChatMessageContent"] th { color: var(--ink) !important; }

[data-testid="stChatMessageContent"] table {
    background: var(--surface) !important;
    border-collapse: collapse;
    width: 100%;
    font-size: 13.5px;
    margin: 6px 0;
}
[data-testid="stChatMessageContent"] th {
    background: var(--surface2) !important;
    color: var(--teal-ink) !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 8px 10px;
    border: 1px solid var(--line);
    text-align: left;
}
[data-testid="stChatMessageContent"] td {
    padding: 7px 10px;
    border: 1px solid var(--line);
}
[data-testid="stChatMessageContent"] tr:nth-child(even) td {
    background: rgba(255,255,255,0.02) !important;
}
[data-testid="stChatMessageContent"] code {
    background: var(--surface2) !important;
    color: var(--teal-ink) !important;
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 1px 5px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
}

/* ── Agent badges ────────────────────────────────────────────────── */
.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10.5px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 10px;
    border: 1px solid var(--line-soft);
}
.agent-badge::before {
    content: "";
    width: 6px; height: 6px;
    border-radius: 50%;
    background: currentColor;
}
.badge-ocr     { background: var(--blue-bg)   !important; color: var(--blue-ink)   !important; }
.badge-rag     { background: var(--green-bg)  !important; color: var(--green-ink)  !important; }
.badge-search  { background: var(--amber-bg)  !important; color: var(--amber-ink)  !important; }
.badge-general { background: var(--violet-bg) !important; color: var(--violet-ink) !important; }

/* ── File chip ───────────────────────────────────────────────────── */
.file-chip {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--teal-bg);
    border: 1px solid rgba(58,139,255,0.28);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 13px;
    color: var(--teal-ink);
    flex-wrap: wrap;
}
.file-chip code {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(58,139,255,0.25);
    color: var(--teal-ink);
    padding: 1px 7px;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
}

/* ── Welcome / empty state ───────────────────────────────────────── */
.welcome {
    position: relative;
    overflow: hidden;
    background: radial-gradient(120% 140% at 50% -10%, #12151d 0%, var(--surface) 55%, #030304 100%);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    text-align: center;
    padding: 50px 24px;
    margin-top: 6px;
}
.welcome::before, .welcome::after {
    content: "";
    position: absolute;
    width: 320px; height: 320px;
    border-radius: 50%;
    filter: blur(120px);
    opacity: 0.30;
    z-index: 0;
}
.welcome::before { background: var(--orange); top: -140px; left: -120px; }
.welcome::after  { background: var(--blue);   bottom: -150px; right: -120px; }
.welcome > * { position: relative; z-index: 2; }

.welcome .mark {
    width: 52px; height: 52px;
    margin: 0 auto 18px auto;
    border-radius: 13px;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--line);
    color: var(--ink);
    display: flex; align-items: center; justify-content: center;
    font-size: 26px; font-weight: 700;
    font-family: 'Sora', sans-serif;
}
.welcome h3 {
    color: var(--ink) !important;
    font-size: 20px;
    font-weight: 700;
    margin: 0 0 8px 0;
}
.welcome p { color: var(--muted) !important; font-size: 14px; margin: 4px 0; }
.welcome .caps {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 20px;
}
.welcome .cap {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12.5px;
    color: var(--muted);
}
.welcome .lang {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--faint) !important;
    margin-top: 20px;
    letter-spacing: 0.06em;
}

/* ── Chat input ──────────────────────────────────────────────────── */
[data-testid="stChatInput"],
[data-testid="stChatInputTextArea"],
[data-testid="stChatInputTextArea"] textarea {
    background-color: var(--surface) !important;
    color: var(--ink) !important;
    border-color: var(--line) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(58,139,255,0.16) !important;
}
[data-testid="stChatInputTextArea"] textarea::placeholder { color: var(--faint) !important; }

/* ── Sidebar: same dark surface as the rest of the app ────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--line) !important;
}

[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label { color: var(--ink); }

[data-testid="stSidebar"] hr { border-color: var(--line) !important; }

/* ── Native collapse control: hidden (it's hover-only and unreliable) ──
   Kept in the DOM — our custom .ca-toggle button below clicks it
   programmatically — just not shown, since it visually disappears
   depending on hover/theme in ways CSS alone couldn't fix. */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    opacity: 0 !important;
    pointer-events: none !important;
}

/* ── Custom hamburger toggle (always visible, fixed top-left) ────── */
.ca-toggle {
    position: fixed;
    top: 16px;
    left: 16px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--surface2);
    border: 1px solid var(--line);
    border-radius: 9px;
    box-shadow: var(--shadow);
    cursor: pointer;
    z-index: 999999;
    transition: border-color .15s, background .15s;
}
.ca-toggle:hover { border-color: var(--blue); background: var(--surface); }
.ca-toggle:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
.ca-toggle-bars {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 4px;
    width: 18px;
}
.ca-toggle-bars span {
    display: block;
    width: 100%;
    height: 2px;
    background: #FFFFFF;
    border-radius: 2px;
}

.sb-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 0 14px 0;
}
.sb-brand .cross {
    width: 38px; height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--orange), var(--blue));
    color: #0a0a0c;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 800;
    font-family: 'Sora', sans-serif;
    flex-shrink: 0;
}
.sb-brand .name {
    font-family: 'Sora', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.15;
}
.sb-brand .tag {
    font-size: 11px;
    color: var(--muted);
    margin-top: 2px;
}

.sb-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12.5px;
    color: var(--ink);
    padding: 4px 0;
}
.sb-row .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--muted);
}

.sb-hours {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    line-height: 2.0;
    color: var(--muted);
}
.sb-hours b { color: var(--ink); font-weight: 500; }

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: var(--surface2) !important;
    border: 1px solid var(--line) !important;
    color: var(--ink) !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: border-color .15s, background .15s;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: rgba(58,139,255,0.5) !important;
    color: #fff !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: var(--surface2) !important;
    border: 1px dashed var(--line) !important;
    border-radius: 10px;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
    color: var(--muted) !important;
    font-size: 12.5px;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    color: var(--ink) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: var(--green-bg) !important;
    border: 1px solid rgba(74,222,128,0.35) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] * {
    color: var(--green-ink) !important;
    font-size: 12.5px !important;
}

.sb-link {
    display: block;
    text-align: center;
    margin-top: 10px;
    background: var(--surface2);
    color: var(--muted) !important;
    padding: 9px 0;
    border-radius: 9px;
    text-decoration: none !important;
    font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
    border: 1px solid var(--line);
    transition: border-color .15s;
}
.sb-link:hover { border-color: var(--blue); color: #fff !important; }

/* ── Spinner ─────────────────────────────────────────────────────── */
[data-testid="stSpinner"] * { color: var(--teal-ink) !important; }


/* ── Footer ──────────────────────────────────────────────────────── */
.app-footer {
    text-align: center;
    color: var(--faint) !important;
    font-size: 11.5px;
    line-height: 1.8;
    padding: 18px 0 8px 0;
    border-top: 1px solid var(--line);
    margin-top: 22px;
}
.app-footer b { color: var(--muted); }
.app-footer .stack {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10.5px;
    letter-spacing: 0.06em;
    margin-top: 6px;
}

/* ── Responsive ──────────────────────────────────────────────────── */
@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"],
    [data-testid="block-container"] { padding: 1rem 0.9rem !important; }
    .masthead { padding: 22px 18px 20px 18px; }
    .masthead h1 { font-size: 22px; }
    .welcome { padding: 36px 16px; }
    div[data-testid="column"] .stButton > button {
        font-size: 12px !important;
        white-space: normal;
    }
}
@media (max-width: 480px) {
    [data-testid="stChatMessage"] { padding: 11px 12px !important; }
}

/* ── Accessibility ───────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; animation: none !important; }
}
</style>
"""
