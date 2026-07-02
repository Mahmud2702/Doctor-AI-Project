# ═══════════════════════════════════════════════════════════════════════════
# ClinicAssist AI — backend.py
# All Gemini — chat + embeddings. Clinic info is retrieved via ChromaDB.
# ═══════════════════════════════════════════════════════════════════════════

import os
import json
import base64
from pathlib import Path
from typing import TypedDict, Annotated, Literal, Optional

from dotenv import load_dotenv
load_dotenv()

# ── LangSmith Tracing ──────────────────────────────────────────────────────
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"]   = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "ClinicAssist-AI")

# ── Imports ────────────────────────────────────────────────────────────────
from langchain_google_genai                  import ChatGoogleGenerativeAI
from langchain_core.messages                 import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph                         import StateGraph, END
from langgraph.graph.message                 import add_messages

import pymupdf

# ── LLM Setup ─────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model          = "gemini-2.5-flash",
    google_api_key = os.getenv("GEMINI_API_KEY"),
    temperature    = 0.3,
)

llm_vision = ChatGoogleGenerativeAI(
    model          = "gemini-2.5-flash",
    google_api_key = os.getenv("GEMINI_API_KEY"),
    temperature    = 0.1,
    max_tokens     = 4000,
)

# ── System Prompts ─────────────────────────────────────────────────────────

_LANGUAGE_BLOCK = """
LANGUAGE HANDLING — MANDATORY:
• Understand English, Bengali (বাংলা), and Banglish (e.g. "Dengue test er dam koto?",
  "Amar jor hoise ki korbo?", "Doctor kobe achen?").
• ALWAYS reply in the EXACT same language/style as the user.
  – Banglish → natural Banglish reply
  – Bengali  → Bengali script reply
  – English  → English reply

SAFETY DISCLAIMER:
You are an information assistant ONLY — NOT a replacement for a licensed doctor.
Always remind users to consult a qualified physician for clinical decisions.
"""

SUPERVISOR_PROMPT = f"""You are the Supervisor/Router Agent for ClinicAssist AI.
{_LANGUAGE_BLOCK}

Route the user message to the correct agent.

ROUTING RULES:
  "ocr"     → user uploaded a file or mentions analyzing a report/lab result/document
  "rag"     → questions about THIS clinic: hours, doctors, test prices, appointments, services
  "search"  → disease outbreaks, current health news, epidemics (dengue, flu, covid)
  "general" → general medical questions, symptoms, advice, greetings

Respond with ONLY valid JSON, no extra text:
{{"route": "<ocr|rag|search|general>", "reason": "<one sentence>"}}"""

OCR_PROMPT = f"""You are the Document Analysis Agent for ClinicAssist AI.
{_LANGUAGE_BLOCK}

You will be given one or more images of a medical document.
Carefully read ALL text visible and produce a structured report.

REQUIRED FORMAT:
## 🏥 Document Type
[Identified report type]

## 📊 Test Results
| Parameter | Value | Unit | Reference Range | Status |
|-----------|-------|------|-----------------|--------|
[✅ Normal / ⚠️ High / 🔴 Low]

## 📝 Plain Language Summary
[Simple explanation for non-medical readers]

## ⚕️ Medical Disclaimer
Always consult your doctor for proper interpretation."""

RAG_PROMPT = f"""You are the Clinic Information Agent for ClinicAssist AI.
{_LANGUAGE_BLOCK}

Answer questions about THIS clinic using ONLY the knowledge base provided.
Be precise with prices (BDT), timings, and doctor schedules.
If info is not in the knowledge base, say so and suggest calling +880-1700-000000."""

SEARCH_PROMPT = f"""You are the Medical Search Agent for ClinicAssist AI.
{_LANGUAGE_BLOCK}

Provide accurate, up-to-date information using the search results provided.
Focus on Bangladesh context. Cite sources naturally.
Give actionable prevention advice for disease outbreaks."""

GENERAL_PROMPT = f"""You are ClinicAssist AI — a knowledgeable healthcare assistant for a clinic in Dhaka.
{_LANGUAGE_BLOCK}

Answer general health questions warmly and clearly.
Do NOT diagnose or prescribe. Recommend doctor consultation for serious symptoms."""

# ── Clinic Knowledge Base (RAG source) ────────────────────────────────────
# The actual knowledge content now lives in knowledge/*.md and is chunked,
# embedded, and retrieved via vectorstore.py — see rag_node() below.
from vectorstore import retrieve_clinic_info

# ── State ──────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages       : Annotated[list, add_messages]
    user_input     : str
    route          : str
    file_path      : Optional[str]
    file_type      : Optional[str]
    final_response : str

# ── Singletons ─────────────────────────────────────────────────────────────
_search_tool : Optional[object] = None


def get_search_tool():
    global _search_tool
    if _search_tool is None:
        _search_tool = TavilySearchResults(
            max_results    = 4,
            tavily_api_key = os.getenv("TAVILY_API_KEY"),
        )
    return _search_tool

# ── Helpers ────────────────────────────────────────────────────────────────

def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _image_block(image_path: str, media_type: str = "image/png") -> dict:
    return {
        "type"      : "image_url",
        "image_url" : {
            "url"   : f"data:{media_type};base64,{_encode_image(image_path)}",
            "detail": "high",
        },
    }


def pdf_to_image_blocks(file_path: str, max_pages: int = 6) -> list:
    """Convert each PDF page to PNG → Gemini Vision image blocks."""
    doc       = pymupdf.open(file_path)
    blocks    = []
    tmp_files = []

    for page_num, page in enumerate(doc):
        if page_num >= max_pages:
            break
        pix      = page.get_pixmap(dpi=200)
        img_path = f"{file_path}_page{page_num}.png"
        pix.save(img_path)
        tmp_files.append(img_path)
        blocks.append(_image_block(img_path, "image/png"))

    doc.close()

    for p in tmp_files:
        try:
            os.remove(p)
        except Exception:
            pass

    return blocks

# ── Nodes ──────────────────────────────────────────────────────────────────

def supervisor_node(state: AgentState) -> dict:
    if state.get("file_path") and state.get("file_type"):
        return {"route": "ocr"}
    try:
        response = llm.invoke([
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=f"Route this message:\n\n{state['user_input']}"),
        ])
        content = response.content.strip()
        if "```" in content:
            content = content.split("```")[1].lstrip("json").strip()
        data  = json.loads(content)
        route = data.get("route", "general")
        if route not in ("ocr", "rag", "search", "general"):
            route = "general"
    except Exception:
        route = "general"
    return {"route": route}


def ocr_node(state: AgentState) -> dict:
    file_path  = state.get("file_path")
    file_type  = state.get("file_type")
    user_instr = state.get("user_input") or "Please analyse this medical document."

    if not file_path:
        return {"final_response": "⚠️ No file uploaded. Please attach an image or PDF."}

    try:
        if file_type == "pdf":
            image_blocks = pdf_to_image_blocks(file_path, max_pages=6)
            if not image_blocks:
                return {"final_response": "❌ Could not read PDF pages. Please try again."}
            content = image_blocks + [{
                "type": "text",
                "text": f"User instruction: {user_instr}\n\nAnalyse ALL pages of this medical document.",
            }]
        else:
            ext_map    = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
            media_type = ext_map.get(Path(file_path).suffix.lower(), "image/jpeg")
            content = [
                _image_block(file_path, media_type),
                {"type": "text", "text": f"User instruction: {user_instr}\n\nAnalyse this medical document."},
            ]

        response = llm_vision.invoke([
            SystemMessage(content=OCR_PROMPT),
            HumanMessage(content=content),
        ])
        return {"final_response": response.content}

    except Exception as exc:
        return {"final_response": f"❌ Document processing error: {exc}"}


def rag_node(state: AgentState) -> dict:
    """RAG Agent — retrieves the most relevant chunks from the clinic
    knowledge base via vector similarity search (Chroma + Gemini
    embeddings), then answers using only that retrieved context."""
    try:
        context = retrieve_clinic_info(state["user_input"], k=4)
        response = llm.invoke([
            SystemMessage(content=RAG_PROMPT),
            HumanMessage(content=(
                f"User Question: {state['user_input']}\n\n"
                f"Relevant Clinic Information (retrieved):\n{context}"
            )),
        ])
        return {"final_response": response.content}
    except Exception as exc:
        return {"final_response": f"❌ Clinic info error: {exc}\n\nCall: +880-1700-000000"}


def search_node(state: AgentState) -> dict:
    try:
        results   = get_search_tool().invoke(state["user_input"])
        formatted = ""
        for i, r in enumerate(results, 1):
            formatted += (
                f"\n**[{i}] {r.get('title','No Title')}**\n"
                f"URL: {r.get('url','N/A')}\n"
                f"{r.get('content','N/A')}\n"
            )
        response = llm.invoke([
            SystemMessage(content=SEARCH_PROMPT),
            HumanMessage(content=f"User Query: {state['user_input']}\n\nSearch Results:\n{formatted}"),
        ])
        return {"final_response": response.content}
    except Exception as exc:
        return {"final_response": f"❌ Search error: {exc}\n\nCheck TAVILY_API_KEY in .env"}


def general_node(state: AgentState) -> dict:
    try:
        messages = [SystemMessage(content=GENERAL_PROMPT)]
        messages.extend(state.get("messages", [])[-6:])
        messages.append(HumanMessage(content=state["user_input"]))
        response = llm.invoke(messages)
        return {"final_response": response.content}
    except Exception as exc:
        return {"final_response": f"❌ Error: {exc}. Please try again."}

# ── Router ─────────────────────────────────────────────────────────────────

def route_decision(state: AgentState) -> Literal["ocr_agent","rag_agent","search_agent","general_agent"]:
    return {
        "ocr"    : "ocr_agent",
        "rag"    : "rag_agent",
        "search" : "search_agent",
        "general": "general_agent",
    }.get(state.get("route", "general"), "general_agent")

# ── Graph ──────────────────────────────────────────────────────────────────
_graph = None

def get_graph():
    global _graph
    if _graph is not None:
        return _graph
    builder = StateGraph(AgentState)
    builder.add_node("supervisor",    supervisor_node)
    builder.add_node("ocr_agent",     ocr_node)
    builder.add_node("rag_agent",     rag_node)
    builder.add_node("search_agent",  search_node)
    builder.add_node("general_agent", general_node)
    builder.set_entry_point("supervisor")
    builder.add_conditional_edges("supervisor", route_decision, {
        "ocr_agent"    : "ocr_agent",
        "rag_agent"    : "rag_agent",
        "search_agent" : "search_agent",
        "general_agent": "general_agent",
    })
    builder.add_edge("ocr_agent",     END)
    builder.add_edge("rag_agent",     END)
    builder.add_edge("search_agent",  END)
    builder.add_edge("general_agent", END)
    _graph = builder.compile()
    return _graph

# ── Public API ─────────────────────────────────────────────────────────────

def process_query(
    user_input   : str,
    file_path    : Optional[str] = None,
    file_type    : Optional[str] = None,
    chat_history : Optional[list] = None,
) -> dict:
    graph  = get_graph()
    result = graph.invoke({
        "messages"      : chat_history or [],
        "user_input"    : user_input,
        "route"         : "",
        "file_path"     : file_path,
        "file_type"     : file_type,
        "final_response": "",
    })
    return {
        "response": result.get("final_response", "Could not process request. Please try again."),
        "route"   : result.get("route", "general"),
    }
