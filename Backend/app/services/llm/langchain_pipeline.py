import json
import logging
from typing import List, Dict

from pydantic import BaseModel, ValidationError
from app.services.llm.groq_service import generate_response

logger = logging.getLogger(__name__)


class VisualOutput(BaseModel):
    visual_type: str  # line_chart | bar_chart | pie_chart | kpi_card | heatmap | funnel_chart | india_map | anomaly_chart | ai_summary
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
You are an advanced business intelligence AI analyst.

Your job:
1. Analyze the provided business data
2. Answer the user query with deep reasoning
3. Detect anomalies and explain WHY they happened
4. Suggest relevant visuals from the allowed list
5. Provide actionable recommendations

Allowed visual types:
- line_chart      → trends over time
- bar_chart       → comparisons
- pie_chart       → distribution
- kpi_card        → single metric with % change
- heatmap         → region x time performance
- funnel_chart    → sales pipeline / conversion
- india_map       → region wise performance
- anomaly_chart   → spike or drop with explanation
- ai_summary      → top level business summary card

STRICT RULES:
- Return ONLY valid JSON - no explanation outside JSON
- Never guess data - only use what is provided
- If data is insufficient → say so in answer
- Confidence must be between 0.0 and 1.0
- If no visual fits → return empty visuals []

Return this exact JSON schema:
{
  "answer": "detailed answer to user query",
  "visuals": [
    {
      "visual_type": "one of the allowed types above",
      "chart_data": {
        "labels": [],
        "datasets": [],
        "meta": {}
      },
      "title": "chart title"
    }
  ],
  "insights": [
    "insight 1",
    "insight 2"
  ],
  "summary": "one paragraph business health summary",
  "root_causes": [
    "reason 1 why something happened",
    "reason 2"
  ],
  "recommendations": [
    "action 1",
    "action 2"
  ],
  "news_context": [
    "relevant news impact 1"
  ],
  "anomalies": [
    "anomaly description with explanation"
  ],
  "confidence": 0.85
}
"""


def build_prompt(
    user_query: str,
    db_data: dict,
    news_context: list,
    include_news: bool,
) -> str:
    news_section = (
        "\n".join(news_context)
        if include_news and news_context
        else "User did not request news context."
    )

    return f"""
User Query:
{user_query}

Business Data (from database):
{json.dumps(db_data, indent=2, default=str)}

News Context:
{news_section}

Based on the above data, respond strictly in the JSON schema provided.
"""


def extract_json(text: str) -> dict:
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from LLM response: {text[:200]}")


def fallback_output(reason: str, confidence: float = 0.0) -> PipelineOutput:
    return PipelineOutput(
        answer=reason,
        visuals=[],
        insights=[],
        summary="",
        root_causes=[],
        recommendations=[],
        news_context=[],
        anomalies=[],
        confidence=confidence,
    )


async def run_pipeline(
    user_query: str,
    db_data: dict,
    news_context: list = [],
    include_news: bool = False,
) -> PipelineOutput:
    try:
        prompt = build_prompt(user_query, db_data, news_context, include_news)

        result = await generate_response(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=2000,
        )

        raw_output = result["content"]
        logger.info(f"LLM source used: {result.get('source', 'unknown')}")

        parsed = extract_json(raw_output)

        output = PipelineOutput(**parsed)

        return output

    except ValidationError as ve:
        logger.error(f"Schema validation failed: {ve}")
        return fallback_output(
            reason="Sorry, I could not process your request properly. Please try again.",
            confidence=0.0,
        )

    except ValueError as ve:
        logger.error(f"JSON extraction failed: {ve}")
        return fallback_output(
            reason="I had trouble understanding the data. Please rephrase your query.",
            confidence=0.0,
        )

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return fallback_output(
            reason="Something went wrong. Please try again.",
            confidence=0.0,
        )
