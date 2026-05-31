from __future__ import annotations

import json
import math
import os
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx

from src.config import ROOT_DIR, get_config
from src.services.content import load_experience


STOPWORDS = {
    "a",
    "about",
    "and",
    "are",
    "as",
    "at",
    "be",
    "can",
    "do",
    "for",
    "have",
    "how",
    "i",
    "in",
    "is",
    "me",
    "my",
    "of",
    "on",
    "or",
    "tell",
    "the",
    "to",
    "what",
    "with",
    "you",
    "your",
}


@dataclass(frozen=True)
class ChatSource:
    label: str
    text: str
    score: float = 0.0


def _tokens(text: str) -> set[str]:
    return {
        tok
        for tok in re.findall(r"[a-z0-9+#.]+", text.lower())
        if len(tok) > 1 and tok not in STOPWORDS
    }


def _load_site_json() -> dict[str, Any]:
    for name in (
        "site.json",
        "site.config.json",
        "site_content.json",
    ):
        path = ROOT_DIR / "data" / name
        if path.exists():
            try:
                return json.loads(path.read_text()) or {}
            except Exception:
                return {}
    return {}


def _chunk_text(text: str, *, max_chars: int = 1200) -> list[str]:
    paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = paragraph[:max_chars]
    if current:
        chunks.append(current)
    return chunks


def _experience_sources() -> list[ChatSource]:
    data = load_experience(ROOT_DIR) or {}
    site = _load_site_json()
    cfg = get_config()
    sources: list[ChatSource] = []

    summary = data.get("summary") or cfg.site_description
    if summary:
        sources.append(ChatSource("Professional summary", str(summary)))

    highlights = data.get("highlights") or []
    if highlights:
        sources.append(
            ChatSource("Highlights", "\n".join(f"- {h}" for h in highlights))
        )

    for role in data.get("experience") or []:
        text = "\n".join(
            [
                f"{role.get('title', 'Role')} at {role.get('company', 'Company')} ({role.get('period', '')})",
                *[f"- {b}" for b in role.get("bullets") or []],
            ]
        )
        sources.append(
            ChatSource(f"Experience: {role.get('company', 'Company')}", text)
        )

    for school in data.get("education") or []:
        text = f"{school.get('degree', 'Degree')} - {school.get('institution', 'Institution')} ({school.get('period', '')})"
        sources.append(ChatSource("Education", text))

    skills = data.get("skills") or {}
    for category, items in skills.items():
        sources.append(
            ChatSource(f"Skills: {category}", ", ".join(str(i) for i in items))
        )

    snapshot = data.get("snapshot") or {}
    if snapshot:
        sources.append(
            ChatSource(
                "Snapshot",
                ", ".join(f"{key}: {value}" for key, value in snapshot.items()),
            )
        )

    resume_text = str(data.get("resume_text") or "").strip()
    for index, chunk in enumerate(_chunk_text(resume_text)[:6], start=1):
        label = "Resume text" if index == 1 else f"Resume text {index}"
        sources.append(ChatSource(label, chunk))

    if site:
        public_bits = [
            f"{key}: {value}"
            for key, value in site.items()
            if key not in {"github_token", "smtp_password"} and value
        ]
        if public_bits:
            sources.append(ChatSource("Site profile", "\n".join(public_bits)))

    return sources


def retrieve_sources(query: str, *, limit: int = 4) -> list[ChatSource]:
    query_tokens = _tokens(query)
    scored: list[ChatSource] = []
    for source in _experience_sources():
        source_tokens = _tokens(f"{source.label} {source.text}")
        overlap = len(query_tokens & source_tokens)
        density = overlap / math.sqrt(max(len(source_tokens), 1))
        scored.append(ChatSource(source.label, source.text, density))

    scored.sort(key=lambda source: source.score, reverse=True)
    matches = [source for source in scored if source.score > 0]
    return (matches or scored)[:limit]


def _fallback_answer(query: str, sources: list[ChatSource]) -> str:
    cfg = get_config()
    if not sources:
        return (
            "I do not have enough portfolio context to answer that yet, but I can discuss "
            f"{cfg.owner_name}'s AI/ML, data science, Python, automation, and project experience."
        )

    lines = [
        "Based on the portfolio context I have, here is the most relevant information:",
        "",
    ]
    for source in sources[:3]:
        text = source.text.strip()
        if len(text) > 420:
            text = text[:417].rstrip() + "..."
        lines.append(f"{source.label}: {text}")
    lines.append("")
    lines.append(
        "Ask a more specific follow-up if you want this narrowed to a role, project, skill, or company fit."
    )
    return "\n".join(lines)


async def _call_hugging_face(
    query: str, sources: list[ChatSource]
) -> tuple[str | None, str | None]:
    token = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
    if not token:
        return None, None

    model = os.getenv("HUGGINGFACE_CHAT_MODEL", "HuggingFaceTB/SmolLM2-1.7B-Instruct")
    cfg = get_config()
    context = "\n\n".join(f"{source.label}:\n{source.text}" for source in sources)
    prompt = f"""You are {cfg.owner_name}'s portfolio assistant.
Answer only from the context. Be concise, specific, and helpful.
If the context does not answer the question, say what you can answer from the portfolio.

Context:
{context}

Question: {query}
Answer:"""

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": int(
                            os.getenv("RAG_MAX_RESPONSE_TOKENS", "220")
                        ),
                        "temperature": float(os.getenv("RAG_TEMPERATURE", "0.3")),
                        "return_full_text": False,
                    },
                    "options": {"wait_for_model": True},
                },
            )
            if response.status_code >= 400:
                retry_after = response.headers.get("retry-after")
                if response.status_code == 429:
                    note = "Hugging Face free inference is temporarily rate-limited"
                    if retry_after:
                        note = f"{note}; retry after {retry_after} seconds"
                    print(f"{note}: {response.text[:300]}")
                    return None, note
                print(
                    f"Hugging Face chat error: {response.status_code} {response.text[:300]}"
                )
                return None, "Hugging Face inference is temporarily unavailable"
            data = response.json()
    except Exception as exc:
        print(f"Hugging Face chat request failed: {exc}")
        return None, "Hugging Face inference is temporarily unavailable"

    generated = ""
    if isinstance(data, list) and data:
        generated = str(data[0].get("generated_text") or "").strip()
    elif isinstance(data, dict):
        generated = str(
            data.get("generated_text") or data.get("summary_text") or ""
        ).strip()

    if not generated or len(generated) < 20:
        return None, "Hugging Face returned an empty response"
    return generated, None


async def answer_chat(query: str) -> dict[str, Any]:
    started = time.time()
    cleaned = query.strip()
    sources = retrieve_sources(cleaned)
    response, model_note = await _call_hugging_face(cleaned, sources)
    provider = "huggingface" if response else "local"
    if not response:
        response = _fallback_answer(cleaned, sources)
        if model_note:
            cfg = get_config()
            response = (
                f"{model_note}. I can still answer from {cfg.owner_name}'s portfolio context.\n\n"
                f"{response}"
            )

    return {
        "success": True,
        "response": response,
        "sources": [source.label for source in sources[:3]],
        "provider": provider,
        "model_note": model_note,
        "elapsed_ms": int((time.time() - started) * 1000),
    }


async def handle_chat_payload(payload: dict[str, Any]) -> dict[str, Any]:
    message = str(payload.get("message") or "").strip()
    if not message:
        return {"success": False, "error": "Message is required."}
    if len(message) > 700:
        return {"success": False, "error": "Message is too long."}
    return await answer_chat(message)
