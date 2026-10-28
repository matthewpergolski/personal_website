from pathlib import Path

from scripts.check_pr_body import REPORT_ONLY, check_pr_body, main


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "pr_bodies"
REQUIRED_HEADINGS = (
    "TL;DR",
    "How it works",
    "Summary",
    "Files changed",
    "How to test",
    "Review",
)


def _good() -> str:
    return (FIXTURES / "good.md").read_text(encoding="utf-8")


def test_report_only_constant_stays_on():
    assert REPORT_ONLY is True


def test_missing_sections_names_each_heading_to_add():
    body = (FIXTURES / "missing_sections.md").read_text(encoding="utf-8")

    problems = check_pr_body(body)

    for heading in REQUIRED_HEADINGS:
        assert f'pr-body: Add a markdown heading "{heading}".' in problems
    assert "pr-body: Add a fenced code block that starts with ```mermaid." in problems


def test_report_only_cli_exits_zero_for_bad_fixture(capsys):
    exit_code = main([str(FIXTURES / "missing_sections.md")])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert 'pr-body: Add a markdown heading "TL;DR".' in output
    assert "pr-body: Add a fenced code block that starts with ```mermaid." in output


def test_good_fixture_has_no_problems():
    assert check_pr_body(_good()) == []


def test_good_fixture_cli_reports_no_problems(capsys):
    exit_code = main([str(FIXTURES / "good.md")])

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == "pr-body: no problems."


def test_enforce_mode_exits_nonzero_for_bad_fixture(monkeypatch):
    monkeypatch.setenv("PR_BODY_CHECK_MODE", "enforce")

    assert main([str(FIXTURES / "missing_sections.md")]) == 1


def test_missing_file_is_a_usage_error(tmp_path):
    assert main([str(tmp_path / "missing.md")]) == 2


def test_headings_out_of_order_names_the_required_order():
    body = """## Review

## TL;DR

## How it works

```mermaid
flowchart TD
  A --> B
```

## Summary

## Files changed

## How to test
"""

    assert check_pr_body(body) == [
        "pr-body: Reorder the required headings to: "
        "TL;DR, How it works, Summary, Files changed, How to test, Review."
    ]


def test_missing_mermaid_names_the_fence_to_add():
    body = _good().replace(
        "```mermaid\nflowchart TD\n  body[Pull request body] --> check[Body check]\n"
        "  check --> report[Print each fix]\n```\n",
        "",
    )

    assert check_pr_body(body) == [
        "pr-body: Add a fenced code block that starts with ```mermaid."
    ]


def test_footer_markers_name_the_removal():
    body = (
        _good()
        + "\n<!-- CURSOR_AGENT_PR_BODY_BEGIN -->\nOpen in Cursor\nGenerated with a footer\n"
    )

    problems = check_pr_body(body)

    assert (
        'pr-body: Remove the Cursor footer marker "CURSOR_AGENT_PR_BODY".' in problems
    )
    assert 'pr-body: Remove the text "Open in Cursor".' in problems
    assert 'pr-body: Remove the phrase "Generated with".' in problems


def test_model_attribution_names_the_token_to_remove():
    problems = check_pr_body(_good() + "\nDrafted by claude-sonnet-5-5-high.\n")

    assert problems == [
        'pr-body: Remove the model attribution "claude-sonnet-5-5-high".'
    ]


def test_standalone_model_slug_is_attribution():
    problems = check_pr_body(_good() + "\ncursor-grok-4.6-high\n")

    assert problems == ['pr-body: Remove the model attribution "cursor-grok-4.6-high".']


def test_bare_model_name_with_attribution_verb():
    problems = check_pr_body(_good() + "\nWritten by Claude.\n")

    assert 'pr-body: Remove the model attribution "Claude".' in problems


def test_generated_with_is_a_word_not_a_prefix():
    within = check_pr_body(_good() + "\nGenerated within the fixture.\n")
    without = check_pr_body(_good() + "\nGenerated without a footer.\n")
    lowered = check_pr_body(_good() + "\nThis note was generated with a footer.\n")

    assert not any(
        'Remove the phrase "Generated with".' in problem for problem in within
    )
    assert not any(
        'Remove the phrase "Generated with".' in problem for problem in without
    )
    assert 'pr-body: Remove the phrase "Generated with".' in lowered


def test_model_id_near_an_attribution_verb_is_not_attribution():
    body = "\n".join(
        [
            _good(),
            "Files created for the smoke test include gpt-4o fixtures.",
            "Compare results with gpt-4o.",
            "Packages are installed with gpt-4o-mini.",
        ]
    )

    assert check_pr_body(body) == []


def test_written_by_lowercase_name_is_attribution():
    problems = check_pr_body(_good() + "\nwritten by claude.\n")

    assert 'pr-body: Remove the model attribution "claude".' in problems


def test_drafted_by_name_is_attribution():
    problems = check_pr_body(_good() + "\nDrafted by Sonnet.\n")

    assert 'pr-body: Remove the model attribution "Sonnet".' in problems


def test_technical_model_mention_is_not_attribution():
    body = "\n".join(
        [
            _good(),
            "",
            "The smoke test does not call gpt-4o-mini.",
            "Frontend assets come from a local script.",
            "Dependencies are installed with Composer in the PHP example.",
        ]
    )

    assert check_pr_body(body) == []
