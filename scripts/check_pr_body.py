"""Check a pull request body against the portfolio template.

Report-only switch
------------------
``REPORT_ONLY`` in this file is the enforce-vs-report switch.

* ``True`` (current): print every problem and exit 0. The build stays green.
* ``False``: print every problem and exit 1 when the body has any problem.

Leave ``REPORT_ONLY`` set to ``True`` until the template should be required.
``PR_BODY_CHECK_MODE=report`` or ``PR_BODY_CHECK_MODE=enforce`` overrides the
constant for a single run. The pull request workflow does not set that variable.

A missing body file or an unknown mode is a usage error and exits 2 in either mode.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


# Flip this to False when the check should fail the build.
REPORT_ONLY = True

REQUIRED_HEADINGS = (
    "TL;DR",
    "How it works",
    "Summary",
    "Files changed",
    "How to test",
    "Review",
)

_HEADING_RE = re.compile(r"^#{1,6}[ \t]+(.+?)\s*$", re.MULTILINE)
_MERMAID_RE = re.compile(
    r"(?ms)^(?:```|~~~)[ \t]*mermaid[ \t]*\n.*?^(?:```|~~~)[ \t]*$"
)
_FENCE_RE = re.compile(r"^(```+|~~~+)")
_MODEL_ID_RE = re.compile(
    r"\b(?:"
    r"cursor-grok-|muse-wonder-|claude-|grok-|gemini-|composer-|gpt-"
    r")[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*",
    re.IGNORECASE,
)
_BARE_MODEL_RE = re.compile(r"\b(ChatGPT|GPT|Claude|Grok|Gemini|Composer)\b")
_ATTRIBUTION_VERB_RE = re.compile(
    r"\b(?:generated|written|authored|co-authored|drafted|created|prepared|produced|assisted)\b",
    re.IGNORECASE,
)
_LEADING_PREPOSITION_RE = re.compile(
    r"\b(?:by|with|via):?\s+(?:(?:the|an?|ai|model)\s+){0,3}$",
    re.IGNORECASE,
)
_LABEL_RE = re.compile(
    r"\b(?:assistant|agent|model|attribution)\s*(?:name|id)?\s*[:=]\s*$",
    re.IGNORECASE,
)
_NEGATION_RE = re.compile(r"\b(?:not|without|no)\b", re.IGNORECASE)

_BANNED = (
    (
        "CURSOR_AGENT_PR_BODY",
        'Remove the Cursor footer marker "CURSOR_AGENT_PR_BODY".',
    ),
    ("Open in Cursor", 'Remove the text "Open in Cursor".'),
    ("Generated with", 'Remove the phrase "Generated with".'),
)


def _problem(fix: str) -> str:
    return f"pr-body: {fix}"


def _normalize(body: str) -> str:
    return body.replace("\r\n", "\n").replace("\r", "\n")


def _outside_fences(body: str) -> str:
    kept: list[str] = []
    fence: str | None = None
    for line in body.split("\n"):
        marker = _FENCE_RE.match(line)
        if marker:
            token = marker.group(1)[0]
            fence = None if fence == token else token if fence is None else fence
            continue
        if fence is None:
            kept.append(line)
    return "\n".join(kept)


def _heading_texts(body: str) -> list[str]:
    texts: list[str] = []
    for match in _HEADING_RE.finditer(_outside_fences(body)):
        text = re.sub(r"\s+#+\s*$", "", match.group(1).strip()).strip()
        texts.append(text)
    return texts


def _heading_problems(body: str) -> list[str]:
    found = _heading_texts(body)
    problems: list[str] = []
    indexes: list[int] = []
    for heading in REQUIRED_HEADINGS:
        if heading not in found:
            problems.append(_problem(f'Add a markdown heading "{heading}".'))
            continue
        indexes.append(found.index(heading))
    if len(indexes) == len(REQUIRED_HEADINGS) and indexes != sorted(indexes):
        order = ", ".join(REQUIRED_HEADINGS)
        problems.append(_problem(f"Reorder the required headings to: {order}."))
    return problems


def _mermaid_problems(body: str) -> list[str]:
    if _MERMAID_RE.search(body):
        return []
    return [_problem("Add a fenced code block that starts with ```mermaid.")]


def _banned_problems(body: str) -> list[str]:
    return [_problem(fix) for needle, fix in _BANNED if needle in body]


def _negated(line: str, start: int) -> bool:
    return _NEGATION_RE.search(line[max(0, start - 48) : start]) is not None


def _is_signature(line: str, token: str) -> bool:
    text = re.sub(r"^[\s>*+-]+", "", line.strip()).strip("`*_~")
    text = text.strip(" .—–-:\"'")
    return text.casefold() == token.casefold()


def _attribution_before(line: str, start: int, *, bare_name: bool) -> bool:
    if _negated(line, start):
        return False
    window = line[max(0, start - 80) : start]
    if _LABEL_RE.search(window):
        return True
    if bare_name:
        return bool(
            _ATTRIBUTION_VERB_RE.search(window)
            and _LEADING_PREPOSITION_RE.search(window)
        )
    return bool(
        _ATTRIBUTION_VERB_RE.search(window) or _LEADING_PREPOSITION_RE.search(window)
    )


def _model_problems(body: str) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    for line in body.split("\n"):
        spans = [
            (match.start(), match.end(), match.group(0))
            for match in _MODEL_ID_RE.finditer(line)
        ]
        spans = [
            span
            for span in spans
            if not any(
                other[0] <= span[0] and other[1] >= span[1] and other != span
                for other in spans
            )
        ]
        for start, end, token in spans:
            key = token.casefold()
            if key in seen:
                continue
            if _is_signature(line, token) or _attribution_before(
                line, start, bare_name=False
            ):
                seen.add(key)
                problems.append(_problem(f'Remove the model attribution "{token}".'))
        for match in _BARE_MODEL_RE.finditer(line):
            token = match.group(1)
            key = token.casefold()
            if key in seen:
                continue
            covered = any(
                start <= match.start() and end >= match.end() for start, end, _ in spans
            )
            if covered or not _attribution_before(line, match.start(), bare_name=True):
                continue
            seen.add(key)
            problems.append(_problem(f'Remove the model attribution "{token}".'))
    return problems


def check_pr_body(body: str) -> list[str]:
    """Return one fix-oriented problem line per template violation."""
    text = _normalize(body or "")
    return [
        *_heading_problems(text),
        *_mermaid_problems(text),
        *_banned_problems(text),
        *_model_problems(text),
    ]


def report_only() -> bool:
    """Return the active mode, honoring ``PR_BODY_CHECK_MODE`` when it is set."""
    override = os.environ.get("PR_BODY_CHECK_MODE")
    if override is None or override.strip() == "":
        return REPORT_ONLY
    value = override.strip().lower()
    if value == "report":
        return True
    if value == "enforce":
        return False
    raise ValueError(override)


def _read_body(path: str | None, body_env: str | None, use_stdin: bool) -> str:
    sources = (path is not None, body_env is not None, use_stdin)
    if sum(sources) != 1:
        raise ValueError("pr-body: Pass a body file, --stdin, or --body-env NAME.")
    if use_stdin:
        return sys.stdin.read()
    if body_env is not None:
        if body_env not in os.environ:
            raise ValueError(
                f"pr-body: Set the {body_env} environment variable to the pull request body."
            )
        return os.environ.get(body_env) or ""
    body_path = Path(path or "")
    if not body_path.is_file():
        raise ValueError(
            f"pr-body: Pass an existing pull request body file. Missing: {body_path}"
        )
    return body_path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a pull request body against the template."
    )
    parser.add_argument(
        "path", nargs="?", help="Markdown file containing the pull request body"
    )
    parser.add_argument(
        "--body-env", help="Environment variable that holds the pull request body"
    )
    parser.add_argument(
        "--stdin", action="store_true", help="Read the pull request body from stdin"
    )
    args = parser.parse_args(argv)
    try:
        checking_is_report_only = report_only()
        body = _read_body(args.path, args.body_env, args.stdin)
    except ValueError as exc:
        message = str(exc)
        if message.startswith("pr-body:"):
            print(message)
        else:
            print(
                'pr-body: Set PR_BODY_CHECK_MODE to "report" or "enforce", '
                "or unset it to use REPORT_ONLY in scripts/check_pr_body.py."
            )
        return 2
    problems = check_pr_body(body)
    print("\n".join(problems) if problems else "pr-body: no problems.")
    if checking_is_report_only or not problems:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
