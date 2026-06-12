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

GREETING_PATTERNS = {
    "hello",
    "hello!",
    "hey",
    "hey!",
    "hi",
    "hi!",
    "yo",
}

FOLLOW_UP_MARKERS = {
    "also",
    "compare",
    "elaborate",
    "expand",
    "more",
    "same",
    "that",
    "those",
    "this",
}

COMPANY_SUMMARY_TOKENS = {
    "career",
    "experience",
    "history",
    "lockheed",
    "martin",
    "summarize",
    "summary",
}

PROJECT_INTENT_TOKENS = {
    "built",
    "build",
    "created",
    "developed",
    "done",
    "project",
    "projects",
    "used",
    "work",
}

ROLE_FIT_TOKENS = {
    "fit",
    "hire",
    "job",
    "jobs",
    "role",
    "roles",
    "target",
    "targeting",
}

SKILL_INTENT_TOKENS = {
    "skill",
    "skills",
    "software",
    "stack",
    "tech",
    "tool",
    "tools",
}

TECH_FOCUS_TOKENS = {
    "aws",
    "docker",
    "python",
    "sql",
    "rust",
    "tableau",
}


@dataclass(frozen=True)
class ChatSource:
    label: str
    text: str
    score: float = 0.0


def _source_payload(source: ChatSource) -> dict[str, str]:
    snippet = re.sub(r"\s+", " ", source.text).strip()
    if len(snippet) > 180:
        snippet = snippet[:177].rstrip() + "..."
    return {"label": source.label, "snippet": snippet}


def _tokens(text: str) -> set[str]:
    return {
        tok
        for tok in re.findall(r"[a-z0-9+#.]+", text.lower())
        if len(tok) > 1 and tok not in STOPWORDS
    }


def _is_greeting(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return normalized in GREETING_PATTERNS


def _should_use_history(query: str) -> bool:
    lowered = query.lower()
    query_tokens = _tokens(query)
    return (
        "what about" in lowered
        or "how about" in lowered
        or "tell me more" in lowered
        or bool(query_tokens & FOLLOW_UP_MARKERS)
    )


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


def _experience_label(role: dict[str, Any]) -> str:
    title = re.sub(r"\s*\([^)]*\)\s*", " ", str(role.get("title") or "Role")).strip()
    return f"Experience: {title or role.get('company', 'Company')}"


def _experience_sources() -> list[ChatSource]:
    data = load_experience(ROOT_DIR) or {}
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
        sources.append(ChatSource(_experience_label(role), text))

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

    return sources


def retrieve_sources(query: str, *, limit: int = 4) -> list[ChatSource]:
    query_tokens = _tokens(query)
    company_summary_intent = bool({"lockheed", "martin"} & query_tokens) and bool(
        COMPANY_SUMMARY_TOKENS & query_tokens
    )
    project_intent = bool(query_tokens & PROJECT_INTENT_TOKENS)
    role_fit_intent = bool(query_tokens & ROLE_FIT_TOKENS)
    skill_intent = bool(query_tokens & SKILL_INTENT_TOKENS)
    tech_focus = query_tokens & TECH_FOCUS_TOKENS
    scored: list[ChatSource] = []
    for index, source in enumerate(_experience_sources()):
        source_tokens = _tokens(f"{source.label} {source.text}")
        overlap = len(query_tokens & source_tokens)
        density = overlap / math.sqrt(max(len(source_tokens), 1))
        if tech_focus and not (tech_focus & source_tokens):
            density *= 0.25
        if source.label.startswith("Experience"):
            if company_summary_intent:
                density *= 1.25 + max(0, 10 - index) * 0.04
                density += max(0, 16 - index) * 0.25
            density *= 1.45 if project_intent else 1.2
        elif source.label in {"Highlights", "Professional summary"}:
            if role_fit_intent:
                density *= 1.35
            density *= 1.25 if project_intent else 1.1
        elif source.label.startswith("Skills"):
            if skill_intent:
                density *= 1.2
            elif project_intent:
                density *= 0.35
            else:
                density *= 0.6
        elif source.label.startswith("Resume text"):
            density *= 0.65
        scored.append(ChatSource(source.label, source.text, density))

    scored.sort(key=lambda source: source.score, reverse=True)
    matches = [source for source in scored if source.score > 0]
    return (matches or scored)[:limit]


def _history_search_text(history: Any) -> str:
    if not isinstance(history, list):
        return ""

    user_messages: list[str] = []
    for item in history[-8:]:
        if not isinstance(item, dict) or item.get("role") != "user":
            continue
        content = str(item.get("content") or "").strip()
        if content:
            user_messages.append(content[:240])
    return "\n".join(user_messages[-3:])


def sanitized_chat_history(history: Any) -> list[dict[str, str]]:
    """Return a small, server-owned history shape safe for retrieval context."""
    if not isinstance(history, list):
        return []

    messages: list[dict[str, str]] = []
    for item in history[-8:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip()
        if role not in {"user", "assistant"}:
            continue
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        messages.append({"role": role, "content": content[:240]})
    return messages[-8:]


def _best_source_points(query: str, sources: list[ChatSource]) -> list[str]:
    query_tokens = _tokens(query)
    candidates: list[tuple[int, int, str]] = []

    for source_index, source in enumerate(sources[:3]):
        raw_lines = [line.strip() for line in source.text.splitlines() if line.strip()]
        lines = [line for line in raw_lines if line.startswith("- ")]
        if not lines:
            # Summaries and compact sources usually have sentence-shaped text.
            lines = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", source.text.strip())
                if sentence.strip()
            ][:2]

        for line_index, line in enumerate(lines[:5]):
            point = line.removeprefix("- ").strip()
            if not point:
                continue
            overlap = len(query_tokens & _tokens(point))
            candidates.append((overlap, source_index * 10 + line_index, point))

    candidates.sort(key=lambda item: (item[1] // 10, -item[0], item[1]))
    points: list[str] = []
    seen: set[str] = set()
    for overlap, _index, point in candidates:
        if overlap == 0 and points:
            continue
        key = point.lower()
        if key in seen:
            continue
        seen.add(key)
        points.append(point)
        if len(points) >= 5:
            break
    return points


def _tech_focus_points(query: str, sources: list[ChatSource]) -> list[str]:
    tech_focus = _tokens(query) & TECH_FOCUS_TOKENS
    if not tech_focus:
        return []

    points: list[str] = []
    seen: set[str] = set()
    for source in sources:
        source_tokens = _tokens(f"{source.label} {source.text}")
        if not tech_focus & source_tokens:
            continue
        for raw_line in source.text.splitlines():
            line = raw_line.strip()
            if source.label.startswith("Experience") and not line.startswith("- "):
                continue
            point = line.removeprefix("- ").strip()
            if not point or point.lower() in seen:
                continue
            if tech_focus & _tokens(point) or (
                source.label.startswith("Experience") and points
            ):
                seen.add(point.lower())
                points.append(point)
            if len(points) >= 3:
                return points
    return points


def _greeting_answer() -> str:
    cfg = get_config()
    first_name = cfg.owner_name.split()[0] if cfg.owner_name else "this portfolio"
    return (
        f"Hi, I can answer questions about {first_name}'s experience, AI/ML work, "
        "projects, skills, education, and fit for technical roles. Try asking about "
        "AI platforms, Python projects, Lockheed Martin experience, or role fit."
    )


def _is_company_summary_query(query: str) -> bool:
    query_tokens = _tokens(query)
    return bool({"lockheed", "martin"} & query_tokens) and bool(
        COMPANY_SUMMARY_TOKENS & query_tokens
    )


def _is_role_fit_query(query: str) -> bool:
    return bool(_tokens(query) & ROLE_FIT_TOKENS)


def _lockheed_summary_answer() -> str | None:
    data = load_experience(ROOT_DIR) or {}
    roles = [
        role
        for role in data.get("experience") or []
        if "lockheed" in str(role.get("company") or "").lower()
    ]
    if not roles:
        return None

    current_roles = roles[:3]
    lines = [
        "Matthew's Lockheed Martin experience spans operations, data science, and AI/ML engineering:",
        "",
    ]
    for role in current_roles:
        title = re.sub(
            r"\s*\([^)]*\)\s*", " ", str(role.get("title") or "Role")
        ).strip()
        period = str(role.get("period") or "").strip()
        bullets = [
            str(item).strip() for item in role.get("bullets") or [] if str(item).strip()
        ]
        detail = (
            bullets[0]
            if bullets
            else "Contributed to technical and operational delivery."
        )
        prefix = f"{title}"
        if period:
            prefix = f"{prefix} ({period})"
        lines.append(f"- {prefix}: {detail}")

    if len(roles) > len(current_roles):
        lines.append(
            "- Earlier manufacturing planning roles add operations, supply-chain, and process-improvement context."
        )

    lines.append("")
    lines.append(
        "The through-line is practical automation: using data, ML, and platform engineering to improve technical and business workflows."
    )
    return "\n".join(lines)


def _role_fit_answer() -> str:
    cfg = get_config()
    data = load_experience(ROOT_DIR) or {}
    summary = str(data.get("summary") or cfg.site_description).strip()
    current_role = ((data.get("experience") or [{}])[0]) or {}
    title = re.sub(
        r"\s*\([^)]*\)\s*", " ", str(current_role.get("title") or "AI/ML Engineer")
    ).strip()
    bullets = [
        str(item).strip()
        for item in current_role.get("bullets") or []
        if str(item).strip()
    ][:3]

    lines = [
        "The strongest role fit is practical AI/ML engineering where data science, automation, and software delivery overlap:",
        "",
        f"- Current positioning: {title}.",
    ]
    if summary:
        lines.append(f"- Portfolio summary: {summary}")
    lines.extend(f"- Evidence: {bullet}" for bullet in bullets)
    lines.append("")
    lines.append(
        "Good target roles include AI/ML engineer, applied machine learning engineer, data science engineer, AI platform engineer, and automation-focused technical lead roles."
    )
    return "\n".join(lines)


def _fallback_answer(query: str, sources: list[ChatSource]) -> str:
    cfg = get_config()
    if not sources:
        return (
            "I do not have enough portfolio context to answer that yet, but I can discuss "
            f"{cfg.owner_name}'s AI/ML, data science, Python, automation, and project experience."
        )

    if _is_company_summary_query(query):
        answer = _lockheed_summary_answer()
        if answer:
            return answer

    if _is_role_fit_query(query):
        return _role_fit_answer()

    points = _tech_focus_points(query, sources) or _best_source_points(query, sources)
    if points:
        lines = ["Here are the strongest matches from the portfolio context:", ""]
        lines.extend(f"- {point}" for point in points)
        lines.append("")
        lines.append(
            "I can narrow this to a specific role, project, toolset, leadership example, or company fit."
        )
        return "\n".join(lines)

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


async def answer_chat(query: str, *, history: Any = None) -> dict[str, Any]:
    started = time.time()
    cleaned = query.strip()
    if _is_greeting(cleaned):
        return {
            "success": True,
            "response": _greeting_answer(),
            "sources": [],
            "provider": "local",
            "provider_label": "Local portfolio retrieval",
            "model_note": None,
            "elapsed_ms": int((time.time() - started) * 1000),
        }

    history_text = _history_search_text(history) if _should_use_history(cleaned) else ""
    retrieval_query = f"{history_text}\n{cleaned}".strip() if history_text else cleaned
    sources = retrieve_sources(retrieval_query)
    response, model_note = await _call_hugging_face(cleaned, sources)
    provider = "huggingface" if response else "local"
    provider_label = "AI-polished answer" if response else "Local portfolio retrieval"
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
        "sources": [_source_payload(source) for source in sources[:3]],
        "provider": provider,
        "provider_label": provider_label,
        "model_note": model_note,
        "elapsed_ms": int((time.time() - started) * 1000),
    }


async def handle_chat_payload(
    payload: dict[str, Any], *, history: Any = None
) -> dict[str, Any]:
    message = str(payload.get("message") or "").strip()
    if not message:
        return {"success": False, "error": "Message is required."}
    if len(message) > 700:
        return {"success": False, "error": "Message is too long."}
    return await answer_chat(message, history=sanitized_chat_history(history))
