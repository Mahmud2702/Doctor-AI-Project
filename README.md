# ClinicAssist AI

**AI-powered multi-agent healthcare assistant** — built for a real clinic workflow, supporting English, বাংলা, and Banglish.

ClinicAssist AI routes patient questions to the right specialist agent — document analysis, clinic information (via vector search), live medical search, or general health guidance — and responds in whichever language the user asked in.

---

## Features

- **Multi-agent routing** — a supervisor agent classifies each query and hands it off to the right specialist:
  | Agent | Handles |
  |---|---|
  | 📄 Document Analysis (`ocr`) | Reading and summarizing uploaded lab reports / prescriptions (JPG, PNG, PDF) |
  | 📚 Clinic Information (`rag`) | Clinic hours, doctor schedules, test prices, services — via **vector-DB retrieval** |
  | 🌐 Medical Search (`search`) | Live web search for disease outbreaks and current health news (via Tavily) |
  | 🩺 General Health (`general`) | Symptom questions, general medical guidance |
- **Real RAG, not prompt-stuffing** — clinic info is chunked, embedded, and semantically retrieved from a vector database, not pasted whole into every prompt.
- **Trilingual by default** — understands and replies in English, Bengali, or Banglish, matching the user's own language automatically.
- **Document upload & analysis** — attach a medical report (PDF/image) and ask questions about it directly in chat.
- **Conversation memory** — keeps the last 20 messages of context for follow-up questions.
- **Full observability** — every request is traced end-to-end via LangSmith.
- **Clean, responsive UI** — a dark "Aurora Console" theme built for clinical/industrial use, with a custom always-visible sidebar toggle and mobile-responsive layout.

---

## Tech stack

- **Frontend:** [Streamlit](https://streamlit.io)
- **Orchestration:** [LangGraph](https://langchain-ai.github.io/langgraph/) + [LangChain](https://www.langchain.com/)
- **LLM:** Google Gemini 2.5 Flash (`langchain-google-genai`)
- **Vector database:** [ChromaDB](https://www.trychroma.com/) — local, embedded, no external service or account required
- **Embeddings:** Gemini `text-embedding-004`
- **Web search:** [Tavily](https://tavily.com)
- **Document parsing:** PyMuPDF (PDF), Gemini Vision (images)
- **Tracing:** LangSmith

---

## Project structure

```
Doctor AI-Project/
├── app.py                 # Streamlit entry point — session state & chat logic only
├── backend.py               # LangGraph multi-agent pipeline (routing, agents, process_query)
├── vectorstore.py            # Vector-DB RAG: chunking, embedding, retrieval (Chroma + Gemini)
├── rebuild_index.py           # CLI: re-embed knowledge/ after editing it
├── requirements.txt
├── .env.example                # Copy to .env and fill in your keys
├── .streamlit/
│   └── config.toml              # Locks the app to the dark theme, hides dev chrome
├── knowledge/
│   └── clinic_info.md            # Clinic knowledge base source (edit this, not the code)
├── .chroma_db/                  # Auto-generated vector index (gitignored, rebuilds locally)
└── ui/
    ├── theme.py                  # All CSS for the app
    └── components.py             # Reusable UI building blocks (masthead, sidebar, chat, etc.)
```

`app.py` never contains raw HTML/CSS — all presentation logic lives in `ui/`. `backend.py` never contains raw knowledge text — that lives in `knowledge/` and is retrieved through `vectorstore.py`.

---

## Vector database (RAG)

The Clinic Information agent doesn't paste the whole knowledge base into every prompt. Instead:

1. **Source of truth:** `knowledge/*.md` — plain Markdown files, easy to edit without touching code.
2. **Chunking:** `RecursiveCharacterTextSplitter` splits each file on `## ` section boundaries first (so a doctor's schedule or a test category stays intact as one chunk), falling back to paragraph/sentence splits for longer sections.
3. **Embedding:** each chunk is embedded with Gemini's `text-embedding-004` model.
4. **Storage:** embeddings are stored in a **local, embedded ChromaDB** collection at `.chroma_db/` — no server, no account, no external service. The only network call is to the Gemini embeddings API, using the same `GEMINI_API_KEY` already used for chat.
5. **Retrieval:** on each clinic-info query, `retrieve_clinic_info()` runs a similarity search and returns only the top-k (default 4) most relevant chunks — that's what actually gets sent to the LLM.

**First run:** the index builds automatically the first time a clinic-info question is asked (slightly slower, one-time cost). Later runs load the persisted index from disk instantly.

**After editing `knowledge/*.md`:** the index does *not* auto-update. Re-embed with:
```bash
python rebuild_index.py
```

**Why Chroma and not FAISS / Pinecone / Weaviate?**
- **FAISS** — a pure vector-search library with no built-in persistence layer; you'd have to hand-roll save/load. Chroma gives the same local, no-server experience with persistence built in.
- **Pinecone / Weaviate** — managed/production vector databases meant for large-scale, multi-user deployments. They need an account (Pinecone) or a running server (Weaviate self-hosted), which this project doesn't need at its current scale.

Chroma was chosen because it needs zero external infrastructure, requires no login/API key of its own, and is a drop-in fit for a project already running entirely locally.

---

## Setup

### 1. Clone and enter the project
```bash
git clone https://github.com/Mahmud2702/Doctor-AI-Project.git
cd Doctor-AI-Project
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your keys:
```
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key   # optional, for tracing
```

### 5. Run the app
```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`. The vector index builds automatically on the first clinic-info question.

---

## Configuration

| Env var | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Powers all four agents + the embeddings used for RAG |
| `TAVILY_API_KEY` | ✅ | Live web search for the Medical Search agent |
| `LANGCHAIN_API_KEY` | Optional | Enables LangSmith tracing |
| `LANGCHAIN_PROJECT` | Optional | LangSmith project name (defaults to `ClinicAssist-AI`) |

The sidebar's **System Status** panel shows which of these are active in real time.

---

## Updating the knowledge base

1. Edit or add `.md` files in `knowledge/`.
2. Rebuild the index:
   ```bash
   python rebuild_index.py
   ```
3. Restart the app.

---

## Disclaimer

ClinicAssist AI is an **information assistant only** — it is not a substitute for a licensed physician. Always consult a qualified healthcare provider for clinical decisions.

---

## License

Add your license of choice here (e.g. MIT).
