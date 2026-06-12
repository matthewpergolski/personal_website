from src.services.email import (
    _clean_config_address,
    _clean_header,
    _clean_reply_address,
)


def test_clean_header_removes_line_breaks():
    assert (
        _clean_header("Hello\r\nBcc: bad@example.com") == "Hello  Bcc: bad@example.com"
    )


def test_clean_reply_address_rejects_header_injection():
    assert _clean_reply_address("user@example.com\r\nBcc: bad@example.com") == ""


def test_clean_reply_address_rejects_display_name():
    assert _clean_reply_address("User <user@example.com>") == ""


def test_clean_config_address_allows_display_name():
    assert _clean_config_address("Portfolio <noreply@example.com>") == (
        "Portfolio <noreply@example.com>"
    )
