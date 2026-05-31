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
