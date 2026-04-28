import asyncio
import json
import logging
from typing import List, Dict, Optional

from pydantic import BaseModel, ValidationError

from app.services.llm.groq_service import generate_response

logger = logging.getLogger(__name__)


class VisualOutput(BaseModel):
    visual_type: str
    chart_data: Dict
    title: str


class PipelineOutput(BaseModel):
    answer: str
    visuals: List[VisualOutput]
    insights: List[str]
    summary: str
    root_causes: List[str]
    recommendations: List[str]
    news_context: List[str]
    anomalies: List[str]
    confidence: float


SYSTEM_PROMPT = """
You are an advanced data analyst AI.

IMPORTANT:
- Always return ONLY valid JSON
- No explanation outside JSON
- Follow this exact schema:

{
  "answer": "string",
  "visuals": [
    {
      "visual_type": "line_chart | bar_chart | pie_chart | kpi_card",
      "chart_data": {},
      "title": "string"
    }
  ],
  "insights": ["string"],
  "summary": "string",
  "root_causes": ["string"],
  "recommendations": ["string"],
  "news_context": ["string"],
  "anomalies": ["string"],
  "confidence": 0.0
}

Rules:
- If no visuals needed → return []
- Confidence must be between 0 and 1
- Keep answer concise but useful
"""


def extract_json(text: str) -> dict:
    """
    Extract JSON safely from LLM response
    """
    try:
        json.loads(text)
    except:
        start = text.find("{")
        end = text.find("}")

        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except:
                pass

    raise ValueError("Invalid JSON response from LLM")
