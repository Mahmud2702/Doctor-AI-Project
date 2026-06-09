# ═══════════════════════════════════════════════════════════════════════════
# ClinicAssist AI — backend.py
# All Gemini — no torch, no chromadb crash
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
CLINIC_KNOWLEDGE = """
# ClinicAssist Medical Center — Knowledge Base

## General Information
Name:     ClinicAssist Medical Center
Address:  House 12, Road 5, Dhanmondi, Dhaka-1205, Bangladesh
Phone:    +880-2-9612345
Hotline:  +880-1700-000000  (9 AM – 8 PM daily)
Email:    info@clinicassist.com.bd

## Clinic Hours
Saturday – Thursday : 8:00 AM – 9:00 PM
Friday              : 4:00 PM – 9:00 PM
Emergency Dept.     : 24 hours / 7 days

## Doctors & Schedules

MEDICINE / GENERAL PRACTICE
  Dr. Mahfuzur Rahman   MBBS, FCPS (Medicine)
    Days: Saturday, Monday, Wednesday | Time: 10:00 AM – 2:00 PM | Fee: 800 BDT
  Dr. Sharmin Akter     MBBS, MD (General Practice)
    Days: Sunday, Tuesday, Thursday   | Time: 9:00 AM  – 1:00 PM | Fee: 800 BDT

CARDIOLOGY
  Dr. Aminul Islam      MBBS, MD (Cardiology)
    Days: Saturday, Tuesday, Thursday | Time: 3:00 PM  – 7:00 PM | Fee: 1500 BDT

GYNECOLOGY
  Dr. Nasrin Begum      MBBS, FCPS (Gynecology)
    Days: Sunday, Wednesday           | Time: 11:00 AM – 3:00 PM | Fee: 1200 BDT

PEDIATRICS
  Dr. Rafiqul Hassan    MBBS, MD (Pediatrics)
    Days: Monday, Thursday            | Time: 4:00 PM  – 8:00 PM | Fee: 1000 BDT

ORTHOPEDICS
  Dr. Zahirul Kabir     MBBS, MS (Orthopedics)
    Days: Tuesday, Saturday           | Time: 5:00 PM  – 8:00 PM | Fee: 1500 BDT

NEUROLOGY
  Dr. Farhana Haque     MBBS, MD (Neurology)
    Days: Wednesday, Thursday         | Time: 2:00 PM  – 6:00 PM | Fee: 2000 BDT

DERMATOLOGY
  Dr. Shirin Sultana    MBBS, DDV (Dermatology)
    Days: Sunday, Thursday            | Time: 5:00 PM  – 8:00 PM | Fee: 1000 BDT

## Laboratory Tests & Prices

BLOOD TESTS
  Complete Blood Count (CBC)                        400 BDT
  Blood Sugar – Fasting                             150 BDT
  Blood Sugar – Random / PP                         150 BDT
  HbA1c                                             800 BDT
  Lipid Profile                                     900 BDT
  Liver Function Tests (LFT)                       1200 BDT
  Kidney Function Tests (KFT)                      1000 BDT
  Thyroid Profile (TSH, T3, T4)                    1500 BDT
  Serum Creatinine                                   300 BDT
  Uric Acid                                          350 BDT
  CRP                                                600 BDT

DENGUE TESTS
  Dengue NS1 Antigen                                 700 BDT
  Dengue IgG / IgM Antibody                          700 BDT
  Dengue Combo (NS1 + IgG/IgM)                      1200 BDT

INFECTION TESTS
  Malaria RDT                                        500 BDT
  COVID-19 RT-PCR                                   2500 BDT
  COVID-19 Rapid Antigen                             800 BDT
  Hepatitis B (HBsAg)                                500 BDT
  HIV Screening (confidential)                       600 BDT

URINE TESTS
  Urine Routine Examination (R/E)                    200 BDT
  Urine Culture & Sensitivity (C/S)                  800 BDT

IMAGING
  X-Ray Chest PA                                     600 BDT
  ECG (12-lead)                                      500 BDT
  Echocardiogram                                    3000 BDT
  Ultrasound – Abdomen                              1500 BDT
  Ultrasound – Pelvis / TVS                         1800 BDT

## Health Packages
  Basic Health Checkup      2500 BDT  (CBC, Blood Sugar, Urine R/E, ECG)
  Standard Health Checkup   5000 BDT  (CBC, Lipid, HbA1c, Sugar, KFT, LFT, X-Ray, ECG)
  Cardiac Package           7000 BDT  (ECG, Echo, Lipid, Sugar, CRP)
  Diabetes Package          3500 BDT  (Sugar F+PP, HbA1c, KFT, Creatinine, Urine R/E)
  Women's Health Package    6000 BDT  (CBC, Thyroid, Sugar, Ultrasound Pelvis, Pap Smear)
  Senior Citizen Package    8000 BDT  (Full panel + ECG + Echo + X-Ray)

## Appointments
  Online: www.clinicassist.com.bd/appointment
  Phone:  +880-1700-000000  (9 AM – 8 PM)
  Walk-in available; report ready in 24 hrs (Culture: 3–5 days)

## Payment
  Cash, bKash, Nagad, Rocket, Visa/Mastercard
  Insurance: Delta Life, MetLife, Guardian Life

## Emergency
  24/7 Emergency Room | ICU: 8 beds | Ambulance: +880-1700-111111
  Emergency Fee: 1500 BDT
"""

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
    """RAG Agent — retrieves from clinic knowledge base using Gemini context window."""
    try:
        response = llm.invoke([
            SystemMessage(content=RAG_PROMPT),
            HumanMessage(content=(
                f"User Question: {state['user_input']}\n\n"
                f"Clinic Knowledge Base:\n{CLINIC_KNOWLEDGE}"
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
