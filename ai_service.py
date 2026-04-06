import json
import os
import re
from typing import Any, Dict, List

import httpx


INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
MODEL = os.getenv("DO_INFERENCE_MODEL", "anthropic-claude-4.6-sonnet")
API_KEY = os.getenv("GRADIENT_MODEL_ACCESS_KEY", os.getenv("DIGITALOCEAN_INFERENCE_KEY", ""))


def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _coerce_unstructured_payload(raw_text: str) -> dict[str, object]:
    compact = raw_text.strip()
    normalized = compact.replace("\n", ",")
    tags = [part.strip(" -•\t") for part in normalized.split(",") if part.strip(" -•\t")]
    if not tags:
        tags = ["guided plan", "saved output", "shareable insight"]
    headline = tags[0].title()
    items = []
    for index, tag in enumerate(tags[:3], start=1):
        items.append({
            "title": f"Stage {index}: {tag.title()}",
            "detail": f"Use {tag} to move the request toward a demo-ready outcome.",
            "score": min(96, 80 + index * 4),
        })
    highlights = [tag.title() for tag in tags[:3]]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact or f"{headline} fallback is ready for review.",
        "tags": tags[:6],
        "items": items,
        "score": 88,
        "insights": [f"Lead with {headline} on the first screen.", "Keep one clear action visible throughout the flow."],
        "next_actions": ["Review the generated plan.", "Save the strongest output for the demo finale."],
        "highlights": highlights,
    }

def _normalize_inference_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return _coerce_unstructured_payload(str(payload))
    normalized = dict(payload)
    summary = str(normalized.get("summary") or normalized.get("note") or "AI-generated plan ready")
    raw_items = normalized.get("items")
    items: list[dict[str, object]] = []
    if isinstance(raw_items, list):
        for index, entry in enumerate(raw_items[:3], start=1):
            if isinstance(entry, dict):
                title = str(entry.get("title") or f"Stage {index}")
                detail = str(entry.get("detail") or entry.get("description") or title)
                score = float(entry.get("score") or min(96, 80 + index * 4))
            else:
                label = str(entry).strip() or f"Stage {index}"
                title = f"Stage {index}: {label.title()}"
                detail = f"Use {label} to move the request toward a demo-ready outcome."
                score = float(min(96, 80 + index * 4))
            items.append({"title": title, "detail": detail, "score": score})
    if not items:
        items = _coerce_unstructured_payload(summary).get("items", [])
    raw_insights = normalized.get("insights")
    if isinstance(raw_insights, list):
        insights = [str(entry) for entry in raw_insights if str(entry).strip()]
    elif isinstance(raw_insights, str) and raw_insights.strip():
        insights = [raw_insights.strip()]
    else:
        insights = []
    next_actions = normalized.get("next_actions")
    if isinstance(next_actions, list):
        next_actions = [str(entry) for entry in next_actions if str(entry).strip()]
    else:
        next_actions = []
    highlights = normalized.get("highlights")
    if isinstance(highlights, list):
        highlights = [str(entry) for entry in highlights if str(entry).strip()]
    else:
        highlights = []
    if not insights and not next_actions and not highlights:
        fallback = _coerce_unstructured_payload(summary)
        insights = fallback.get("insights", [])
        next_actions = fallback.get("next_actions", [])
        highlights = fallback.get("highlights", [])
    return {
        **normalized,
        "summary": summary,
        "items": items,
        "score": float(normalized.get("score") or 88),
        "insights": insights,
        "next_actions": next_actions,
        "highlights": highlights,
    }


async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    try:
        if not API_KEY:
            return {"note": "AI temporarily unavailable: missing inference key.", "ok": False}

        payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_completion_tokens": max(256, max_tokens),
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(INFERENCE_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        content = ""
        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "") or ""

        if not content:
            return {"note": "AI temporarily unavailable: empty model response.", "ok": False}

        cleaned = _extract_json(content)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            parsed.setdefault("ok", True)
            return parsed
        return {"ok": True, "data": parsed}
    except Exception:
        return {"note": "AI is temporarily unavailable. Returned a deterministic fallback.", "ok": False}


async def generate_fitness_blueprint(query: str, preferences: str) -> Dict[str, Any]:
    prompt = {
        "role": "system",
        "content": "You are a fitness program architect. Return strict JSON with keys: summary (string), items (array of workout blocks), score (number 0-100), brief (object), rationale (array of strings), clarifying_questions (array max 2). Each workout block item must include day, focus, duration_minutes, intensity, recovery_note, exercises(array).",
    }
    user = {
        "role": "user",
        "content": f"Messy input: {query}\nPreferences: {preferences}",
    }
    result = await _call_inference([prompt, user], max_tokens=512)
    if result.get("ok"):
        return result

    return {
        "summary": "Generated fallback blueprint from rules because AI is temporarily unavailable.",
        "items": [
            {
                "day": "Mon",
                "focus": "Full Body Strength",
                "duration_minutes": 45,
                "intensity": "moderate",
                "recovery_note": "24h recovery before next lift.",
                "exercises": ["Goblet Squat", "Push-up", "One-arm Row", "Plank"],
            },
            {
                "day": "Wed",
                "focus": "Lower + Core",
                "duration_minutes": 40,
                "intensity": "moderate",
                "recovery_note": "Low-impact finisher.",
                "exercises": ["RDL", "Split Squat", "Glute Bridge", "Dead Bug"],
            },
            {
                "day": "Fri",
                "focus": "Upper + Conditioning",
                "duration_minutes": 45,
                "intensity": "moderate-high",
                "recovery_note": "Weekend active recovery walk.",
                "exercises": ["DB Bench", "Row", "Overhead Press", "Bike Intervals"],
            },
        ],
        "score": 78,
        "brief": {
            "primary_goal": "general fitness with consistency",
            "frequency_per_week": 3,
            "session_minutes": 45,
            "equipment": "adjustable",
            "injury_notes": "none specified",
            "training_level": "beginner-intermediate",
            "style_preference": "balanced",
            "assumptions": "Progressive overload and recovery adherence.",
        },
        "rationale": [
            "Frequency is achievable for adherence.",
            "Sessions fit typical schedule constraints.",
            "Recovery spacing supports consistency.",
        ],
        "clarifying_questions": ["Any specific injury limitations?", "Preferred equipment access?"],
        "note": result.get("note", "AI is temporarily unavailable."),
    }


async def generate_plan_insights(selection: str, context: str) -> Dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": "Return strict JSON with keys: insights (array of strings), next_actions (array of strings), highlights (array of strings). Focus on fitness plan viability and practical coaching steps.",
        },
        {"role": "user", "content": f"Selection: {selection}\nContext: {context}"},
    ]
    result = await _call_inference(messages, max_tokens=512)
    if result.get("ok"):
        return result

    return {
        "insights": [
            "Current split has decent recovery spacing but may need lower-body intensity tuning.",
            "Exercise selection should reflect available equipment to keep adherence high.",
        ],
        "next_actions": [
            "Swap one bilateral knee-dominant movement for hip-dominant alternative.",
            "Reduce one session by 10 minutes if schedule consistency drops.",
        ],
        "highlights": [
            "Recovery logic is preserved.",
            "Plan still aligns with primary goal direction.",
        ],
        "note": result.get("note", "AI is temporarily unavailable."),
    }
