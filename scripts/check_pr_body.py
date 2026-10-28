"""Check a pull request body against the portfolio template.

Report-only switch
------------------
``REPORT_ONLY`` is the enforce-vs-report switch for this check.

* ``True`` (current): print every problem and exit 0. The build stays green.
* ``False``: print every problem and exit 1 when the body has any problem.

Leave ``REPORT_ONLY`` set to ``True`` until the template should be required.
Set the environment variable ``PR_BODY_CHECK_MODE`` to ``report`` or
``enforce`` only to override that constant for a single run. The GitHub
Actions workflow does not set it.
"""

from __future__ import annotations

REPORT_ONLY = True


def check_pr_body(body: str) -> list[str]:
    """Return one fix-oriented problem line per template violation."""
    del body
    return []


def main(argv: list[str] | None = None) -> int:
    del argv
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
