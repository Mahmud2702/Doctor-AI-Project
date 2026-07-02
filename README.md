<div align="center">

# ClinicAssist AI

**An AI-powered multi-agent healthcare assistant, built for a real clinic workflow.**

Supports English, বাংলা, and Banglish — routes every question to the right specialist agent automatically.

[**🌐 Live App**](https://clinicassist-doctor-ai.streamlit.app) · [Report an issue](https://github.com/Mahmud2702/Doctor-AI-Project/issues)

</div>

---

## Overview

ClinicAssist AI is a Streamlit chatbot backed by a LangGraph multi-agent pipeline. A supervisor agent reads each message and routes it to one of four specialists, which respond in whichever language the user wrote in — English, Bengali script, or Banglish.

| Agent | Handles | How |
|---|---|---|
| 📄 **Document Analysis** | Reading uploaded lab reports / prescriptions (JPG, PNG, PDF) | Gemini Vision |
| 📚 **Clinic Information** | Hours, doctor schedules, test prices, services | **Vector-DB RAG** (ChromaDB + Gemini embeddings) |
| 🌐 **Medical Search** | Disease outbreaks, current health news | Live web search (Tavily) |
| 🩺 **General Health** | Symptom questions, general medical guidance | Gemini, direct |

---

## Features

- **Real RAG, not prompt-stuffing** — the clinic knowledge base is chunked, embedded, and semantically retrieved from a local vector database, not pasted whole into every prompt.
- **Trilingual by default** — replies in whichever language/style the user asked in.
- **Document upload & analysis** — attach a medical report and ask questions about it directly in chat.
- **Conversation memory** — keeps the last 20 messages for follow-up questions.
- **Full observability** — every request traced end-to-end via LangSmith.
- **Clean, responsive UI** — a dark "Aurora Console" theme built for clinical/industrial use, with a custom always-visible sidebar toggle and mobile-responsive layout.
- **Cloud-ready** — deployed on Streamlit Community Cloud with a sqlite3 compatibility patch for Chroma.

---

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) |
| Orchestration | [LangGraph](https://langchain-ai.github.io/langgraph/) + [LangChain](https://www.langchain.com/) |
| LLM | Google Gemini 2.5 Flash (`langchain-google-genai`) |
| Vector database | [ChromaDB](https://www.trychroma.com/) — local, embedded, no external service |
| Embeddings | Gemini `text-embedding-004` |
| Web search | [Tavily](https://tavily.com) |
| Document parsing | PyMuPDF (PDF), Gemini Vision (images) |
| Tracing | LangSmith |
| Hosting | Streamlit Community Cloud |

---

## Project structure

```
Doctor-AI-Project/
├── app.py                 # Streamlit entry point — session state & chat logic only
├── backend.py               # LangGraph multi-agent pipeline (routing, agents, process_query)
├── vectorstore.py            # Vector-DB RAG: chunking, embedding, retrieval (Chroma + Gemini)
├── rebuild_index.py           # CLI: re-embed knowledge/ after editing it
├── requirements.txt
├── .env.example                # Copy to .env and fill in your keys
├── .streamlit/
│   └── config.toml              # Dark theme lock, hides Streamlit dev chrome
├── knowledge/
│   └── clinic_info.md            # Clinic knowledge base source (edit this, not the code)
├── .chroma_db/                  # Auto-generated vector index (gitignored)
└── ui/
    ├── theme.py                  # All CSS for the app
    └── components.py             # Reusable UI building blocks (masthead, sidebar, chat, etc.)
```

`app.py` holds no HTML/CSS — all presentation logic lives in `ui/`. `backend.py` holds no raw knowledge text — that lives in `knowledge/` and is retrieved through `vectorstore.py`. Each concern stays swappable on its own.

---

## Vector database (RAG)

The Clinic Information agent doesn't paste the whole knowledge base into every prompt — it retrieves only what's relevant:

1. **Source:** `knowledge/*.md` — plain Markdown, edit without touching code.
2. **Chunking:** splits on `## ` section boundaries first (so a doctor's schedule or test category stays intact as one chunk), falling back to paragraph/sentence splits for longer sections.
3. **Embedding:** each chunk embedded with Gemini's `text-embedding-004`.
4. **Storage:** a local, embedded **ChromaDB** collection at `.chroma_db/` — no server, no account, no external service beyond the Gemini embeddings call (same `GEMINI_API_KEY` used for chat).
5. **Retrieval:** each query runs a similarity search and returns the top-4 most relevant chunks — that's what actually reaches the LLM.

The index builds automatically on the first clinic-info question and persists after that. After editing `knowledge/*.md`, re-embed with:
```bash
python rebuild_index.py
```

**Why Chroma over FAISS / Pinecone / Weaviate?** FAISS has no built-in persistence (you'd hand-roll save/load). Pinecone and Weaviate are managed/production databases meant for large, multi-user deployments and need an account or a running server. Chroma needs neither — a drop-in fit for a project that runs entirely locally or on a single Streamlit Cloud instance.

---

## Running locally

```bash
git clone https://github.com/Mahmud2702/Doctor-AI-Project.git
cd Doctor-AI-Project

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:
```
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key   # optional, for tracing
```

Run it:
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`. The vector index builds on the first clinic-info question.

---

## Configuration

| Env var | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Powers all four agents + RAG embeddings |
| `TAVILY_API_KEY` | ✅ | Live web search for the Medical Search agent |
| `LANGCHAIN_API_KEY` | Optional | Enables LangSmith tracing |
| `LANGCHAIN_PROJECT` | Optional | LangSmith project name (defaults to `ClinicAssist-AI`) |

The sidebar's **System Status** panel shows which of these are active in real time.

---

## Deployment

Live on **[Streamlit Community Cloud](https://clinicassist-doctor-ai.streamlit.app)**, deployed directly from this repository's `main` branch. API keys are set via Community Cloud's Secrets manager, not committed to the repo.

To deploy your own copy:
1. Fork this repo.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Sign in with GitHub**.
3. **Create app** → select your fork, branch `main`, main file `app.py`.
4. Under **Advanced settings → Secrets**, paste your keys in TOML format:
   ```toml
   GEMINI_API_KEY = "your_key"
   TAVILY_API_KEY = "your_key"
   LANGCHAIN_API_KEY = "your_key"
   ```
5. **Deploy**.

`requirements.txt` includes a Linux-only `pysqlite3-binary` dependency that patches Chroma's sqlite3 requirement for Streamlit Cloud's containers — no action needed, it's skipped automatically on Windows/macOS local dev.

---

## Updating the knowledge base

1. Edit or add `.md` files in `knowledge/`.
2. Rebuild the index:
   ```bash
   python rebuild_index.py
   ```
3. Restart the app (or push to `main` if deployed — Streamlit Cloud picks up the change and the index rebuilds on the next clinic-info query).

---

## Disclaimer

ClinicAssist AI is an **information assistant only** — it is not a substitute for a licensed physician. Always consult a qualified healthcare provider for clinical decisions.

---

## License

Add your license of choice here (e.g. MIT).
