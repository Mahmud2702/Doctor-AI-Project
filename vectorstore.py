# ═══════════════════════════════════════════════════════════════════════════
# vectorstore.py — Vector-DB RAG for the Clinic Information agent
#
# Knowledge lives in knowledge/*.md (edit those files, not this one).
# On first run this module chunks + embeds them into a persistent Chroma
# collection. On later runs it just loads the existing index from disk —
# no re-embedding unless you call rebuild_index().
# ═══════════════════════════════════════════════════════════════════════════

# ── Cloud compatibility shim ──────────────────────────────────────────────
# Streamlit Community Cloud's Linux containers ship a system sqlite3 older
# than Chroma requires (needs >= 3.35.0). pysqlite3-binary provides a newer
# build; this swaps it in when present. Locally on Windows it's not
# installed (see requirements.txt's platform marker), so this is a silent
# no-op there — the built-in sqlite3 is already new enough on Windows.
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import os
import shutil
from pathlib import Path
from typing import Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

BASE_DIR      = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
PERSIST_DIR   = BASE_DIR / ".chroma_db"
COLLECTION    = "clinic_knowledge"

_embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
_vectorstore: Optional[Chroma] = None


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model          = "models/text-embedding-004",
            google_api_key = os.getenv("GEMINI_API_KEY"),
        )
    return _embeddings


def _load_and_chunk() -> list[Document]:
    """Read every .md file in knowledge/ and split it into retrievable chunks.
    Splitting prefers '## ' section boundaries first, so each doctor's
    schedule / test category / policy section stays intact as one chunk
    where possible, and only falls back to splitting mid-paragraph for
    sections longer than chunk_size."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size    = 500,
        chunk_overlap = 60,
        separators    = ["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )

    docs: list[Document] = []
    md_files = sorted(KNOWLEDGE_DIR.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(
            f"No .md files found in {KNOWLEDGE_DIR}. Add at least one "
            f"knowledge file (e.g. knowledge/clinic_info.md)."
        )

    for path in md_files:
        text   = path.read_text(encoding="utf-8")
        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            docs.append(Document(
                page_content = chunk.strip(),
                metadata     = {"source": path.name, "chunk": i},
            ))
    return docs


def _build_fresh_index() -> Chroma:
    docs = _load_and_chunk()
    return Chroma.from_documents(
        documents         = docs,
        embedding         = get_embeddings(),
        collection_name   = COLLECTION,
        persist_directory = str(PERSIST_DIR),
    )


def get_vectorstore() -> Chroma:
    """Returns the Chroma vectorstore, building it on first call and
    reusing the persisted index (and the in-memory singleton) after that."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    if PERSIST_DIR.exists() and any(PERSIST_DIR.iterdir()):
        _vectorstore = Chroma(
            collection_name   = COLLECTION,
            embedding_function= get_embeddings(),
            persist_directory = str(PERSIST_DIR),
        )
    else:
        _vectorstore = _build_fresh_index()

    return _vectorstore


def rebuild_index() -> Chroma:
    """Wipes the persisted index and re-embeds everything in knowledge/.
    Call this after editing/adding files in knowledge/ — either via
    `python rebuild_index.py` or by importing this function directly."""
    global _vectorstore
    if PERSIST_DIR.exists():
        shutil.rmtree(PERSIST_DIR)
    _vectorstore = _build_fresh_index()
    return _vectorstore


def retrieve_clinic_info(query: str, k: int = 4) -> str:
    """Semantic search over the clinic knowledge base. Returns the top-k
    most relevant chunks, formatted for direct inclusion in an LLM prompt."""
    vs      = get_vectorstore()
    results = vs.similarity_search(query, k=k)

    if not results:
        return "No relevant information found in the clinic knowledge base."

    blocks = []
    for doc in results:
        source = doc.metadata.get("source", "clinic_info.md")
        blocks.append(f"[Source: {source}]\n{doc.page_content}")

    return "\n\n---\n\n".join(blocks)
