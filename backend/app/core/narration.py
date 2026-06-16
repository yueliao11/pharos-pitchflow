from __future__ import annotations

import json
import os
from typing import List, Dict, Optional

import requests

from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


STYLE_TEMPLATES = {
    "business": {
        "en": "Let's look at '{title}'. {bullets}",
        "zh": "接下来看'{title}'。{bullets}",
    },
    "education": {
        "en": "In this section, we explore '{title}'. {bullets}",
        "zh": "在这一节，我们来了解'{title}'。{bullets}",
    },
    "crypto_pitch": {
        "en": (
            "Moving to '{title}'. {bullets} "
            "This is a key part of the value we are building onchain."
        ),
        "zh": "进入'{title}'。{bullets} 这是我们在链上构建价值的关键部分。",
    },
    "product_demo": {
        "en": "Now, '{title}'. {bullets}",
        "zh": "现在来看'{title}'。{bullets}",
    },
}


def _fallback_narration(
    slides: List[Dict],
    style: str,
    language: str,
) -> List[str]:
    """Generate deterministic narration when no LLM is available."""
    template = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["business"]).get(
        language, STYLE_TEMPLATES["business"]["en"]
    )
    narrations = []
    for slide in slides:
        title = slide.get("title") or "this slide"
        bullets = slide.get("bullets") or []
        bullet_text = " ".join(bullets) if bullets else ""
        text = template.format(title=title, bullets=bullet_text)
        narrations.append(text)
    return narrations


def _call_openai(slides: List[Dict], style: str, language: str) -> Optional[List[str]]:
    if not OPENAI_API_KEY:
        return None

    system_prompt = (
        "You are a professional video narrator for AI-generated presentations. "
        "Given slide content, write concise, natural narration for each slide. "
        "Output valid JSON with a single key 'slides' containing an array of strings. "
        "One narration string per slide, in the requested language."
    )

    user_prompt = {
        "style": style,
        "language": language,
        "slides": [
            {
                "title": s.get("title", ""),
                "bullets": s.get("bullets", []),
                "notes": s.get("notes", ""),
            }
            for s in slides
        ],
    }

    try:
        resp = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return parsed.get("slides")
    except Exception as exc:
        print(f"[narration] OpenAI call failed, using fallback template: {exc}")
        return None


def generate_narration(
    slides: List[Dict],
    mode: str = "auto_from_slide_text",
    style: str = "business",
    language: str = "en",
    custom_script: Optional[str] = None,
) -> List[str]:
    """
    Generate per-slide narration.

    Modes:
      - auto_from_slide_text: synthesize from title + bullets.
      - speaker_notes: prefer speaker notes, fallback to auto.
      - custom_script: use user-supplied script (split by '---' per slide).
    """
    if mode == "custom_script" and custom_script:
        parts = [p.strip() for p in custom_script.split("---") if p.strip()]
        if len(parts) == len(slides):
            return parts
        # If count mismatch, repeat the single script for every slide.
        return [custom_script.strip() for _ in slides]

    if mode == "speaker_notes":
        if all(s.get("notes") for s in slides):
            return [s["notes"] for s in slides]

    # Try LLM first for richer narration.
    llm_result = _call_openai(slides, style, language)
    if llm_result and len(llm_result) == len(slides):
        return llm_result

    return _fallback_narration(slides, style, language)
