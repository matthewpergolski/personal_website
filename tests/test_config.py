from src import config


def test_site_config_prefers_public_email_over_smtp_to(monkeypatch):
    monkeypatch.setattr(
        config,
        "_read_site_json",
        lambda: {
            "owner_name": "Example Owner",
            "public_email": "public@example.com",
            "resume_url": "https://example.com/from-json.pdf",
        },
    )
    monkeypatch.setenv("SMTP_TO", "private@example.com")
    monkeypatch.delenv("PUBLIC_EMAIL", raising=False)
    monkeypatch.delenv("CONTACT_EMAIL", raising=False)
    monkeypatch.delenv("RESUME_URL", raising=False)

    site_config = config.get_config()

    assert site_config.owner_name == "Example Owner"
    assert site_config.public_email == "public@example.com"
    assert site_config.resume_url == "https://example.com/from-json.pdf"


def test_site_config_loads_public_content_copy(monkeypatch):
    monkeypatch.setattr(
        config,
        "_read_site_json",
        lambda: {
            "content": {
                "projects": {"title": "Selected Work"},
                "chat": {"suggestions": ["Ask about leadership"]},
            },
        },
    )

    site_config = config.get_config()

    assert site_config.text("projects", "title", "Featured Projects") == "Selected Work"
    assert site_config.text("projects", "missing", "Fallback") == "Fallback"
    assert site_config.text_list("chat", "suggestions", []) == ["Ask about leadership"]
    assert site_config.text_list("chat", "missing", ["Fallback"]) == ["Fallback"]
