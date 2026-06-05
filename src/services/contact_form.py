from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from email.utils import parseaddr
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class ContactSubmission:
    name: str
    email: str
    message: str
    company: str
    submitted_at: int
    captcha: str


@dataclass(frozen=True)
class ContactThresholds:
    min_message_length: int
    min_submit_seconds: float


def parse_contact_submission(form) -> ContactSubmission:
    try:
        submitted_at = int(form.get("t0") or 0)
    except Exception:
        submitted_at = 0

    return ContactSubmission(
        name=(form.get("name") or "").strip(),
        email=(form.get("email") or "").strip(),
        message=(form.get("message") or "").strip(),
        company=(form.get("company") or "").strip(),
        submitted_at=submitted_at,
        captcha=(form.get("captcha") or "").strip().upper(),
    )


def get_contact_thresholds() -> ContactThresholds:
    try:
        min_message_length = int(os.getenv("CONTACT_MIN_MSG_LEN", "10"))
    except Exception:
        min_message_length = 10
    try:
        min_submit_seconds = float(os.getenv("CONTACT_MIN_SECONDS", "2.5"))
    except Exception:
        min_submit_seconds = 2.5

    debug = os.getenv("DEBUG", "").lower() in ("1", "true", "yes", "on")
    if debug:
        min_message_length = min(min_message_length, 3)
        min_submit_seconds = 0.0

    return ContactThresholds(min_message_length, min_submit_seconds)


def _has_header_break(value: str) -> bool:
    return "\r" in value or "\n" in value


def _valid_email_address(value: str) -> bool:
    if _has_header_break(value):
        return False
    display_name, address = parseaddr(value)
    if display_name:
        return False
    if not address or address != value:
        return False
    local, separator, domain = address.partition("@")
    if separator != "@" or not local or not domain or "." not in domain:
        return False
    return not any(char.isspace() for char in address)


def validate_contact_fields(
    submission: ContactSubmission,
    thresholds: ContactThresholds,
    *,
    now: float | None = None,
) -> list[str]:
    now = time.time() if now is None else now
    errors: list[str] = []

    if submission.submitted_at and thresholds.min_submit_seconds > 0:
        if now - submission.submitted_at < thresholds.min_submit_seconds:
            errors.append("Submission was too fast; please try again.")
    if _has_header_break(submission.name) or _has_header_break(submission.email):
        errors.append("Please remove line breaks from your name and email.")
    if len(submission.name) < 2:
        errors.append("Please enter your name.")
    if not _valid_email_address(submission.email):
        errors.append("Please enter a valid email address.")
    if len(submission.message) < thresholds.min_message_length:
        errors.append("Please write a slightly longer message.")

    return errors


def consume_matching_captcha(
    session,
    submitted_answer: str,
    answer_hash: Callable[[str], str],
    *,
    now: float | None = None,
) -> bool:
    submitted_hash = answer_hash(submitted_answer)
    now = time.time() if now is None else now
    answers = session.get("captcha_answers", [])

    valid_answers = []
    matched = False
    for item in answers:
        if now - item.get("ts", 0) > 600:
            continue
        stored_hash = item.get("answer_hash")
        if not stored_hash:
            continue
        if not matched and stored_hash == submitted_hash:
            matched = True
            continue
        valid_answers.append(item)

    session["captcha_answers"] = valid_answers
    return matched


def add_captcha_answer(session, answer_hash: str, *, now: float | None = None) -> None:
    now = time.time() if now is None else now
    answers = session.get("captcha_answers", [])
    answers = [
        item
        for item in answers
        if item.get("answer_hash") and now - item.get("ts", 0) < 600
    ][-4:]
    answers.append({"answer_hash": answer_hash, "ts": now})
    session["captcha_answers"] = answers


def contact_error_code(errors: list[str]) -> str:
    if any("verification" in error.lower() for error in errors):
        return "verify"
    if any("many" in error.lower() for error in errors):
        return "ratelimit"
    return "invalid"


def save_local_message(base_data_dir: Path, submission: ContactSubmission) -> None:
    message_dir = base_data_dir / "messages"
    message_dir.mkdir(parents=True, exist_ok=True)
    (message_dir / f"{int(time.time())}.json").write_text(
        json.dumps(
            {
                "name": submission.name,
                "email": submission.email,
                "message": submission.message,
            }
        )
    )
