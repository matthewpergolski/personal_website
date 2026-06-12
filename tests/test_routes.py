from types import SimpleNamespace

from starlette.testclient import TestClient

import main as main_mod


def _profile():
    return {
        "name": "Matthew L. Pergolski",
        "bio": "AI/ML engineer and data scientist",
        "avatar_url": "https://example.com/avatar.png",
        "html_url": "https://github.com/matthewpergolski",
        "public_repos": 17,
        "followers": 1,
    }


def _projects():
    return [
        {
            "name": "portfolio_app",
            "language": "Python",
            "description": "Portfolio application",
            "topics": ["fasthtml"],
            "url": "https://github.com/matthewpergolski/portfolio_app",
            "stars": 3,
            "updated": "2026-05-01",
        }
    ]


def test_public_routes_render(monkeypatch):
    async def fake_profile():
        return _profile()

    async def fake_projects():
        return _projects()

    async def fake_language_bytes():
        return {"Python": 1200, "HTML": 600}

    monkeypatch.setattr(main_mod, "fetch_github_profile", fake_profile)
    monkeypatch.setattr(main_mod, "fetch_github_projects", fake_projects)
    monkeypatch.setattr(main_mod, "fetch_language_bytes_aggregate", fake_language_bytes)
    monkeypatch.setattr(
        main_mod, "generate_captcha", lambda: ("data:image/png;base64,AA==", "ABCDE")
    )

    client = TestClient(main_mod.app)

    expectations = {
        "/": ["Matthew L. Pergolski", "Tech Stack Snapshot"],
        "/projects": ["Featured Projects", "portfolio_app"],
        "/about": ["About Me", "Professional Background"],
        "/resume": ["Professional Resume", "Download Resume"],
        "/contact": ["Get In Touch", "Send a Message"],
        "/chat": ["Experience Chat"],
    }

    for path, expected_text in expectations.items():
        response = client.get(path)
        assert response.status_code == 200, path
        for text in expected_text:
            assert text in response.text, path


def test_resume_download_redirect(monkeypatch):
    monkeypatch.setenv("RESUME_URL", "https://example.com/resume.pdf")

    response = TestClient(main_mod.app).get("/resume/download", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/resume.pdf"


def test_resume_download_uses_public_site_config(monkeypatch):
    monkeypatch.delenv("RESUME_URL", raising=False)
    monkeypatch.setattr(
        main_mod,
        "get_config",
        lambda: SimpleNamespace(resume_url="https://example.com/from-site-json.pdf"),
    )

    response = TestClient(main_mod.app).get("/resume/download", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/from-site-json.pdf"


def test_resume_download_rejects_non_https_external_url(monkeypatch):
    monkeypatch.setenv("RESUME_URL", "http://example.com/resume.pdf")

    response = TestClient(main_mod.app).get("/resume/download", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/resume.pdf"


def test_resume_download_respects_allowed_host(monkeypatch):
    monkeypatch.setenv("RESUME_URL", "https://evil.example/resume.pdf")
    monkeypatch.setenv("RESUME_URL_ALLOWED_HOSTS", "docs.google.com")

    response = TestClient(main_mod.app).get("/resume/download", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/resume.pdf"


def test_navigation_orders_about_before_projects():
    response = TestClient(main_mod.app).get("/resume")

    assert response.status_code == 200
    assert response.text.index(">About<") < response.text.index(">Projects<")


def test_chat_endpoint_rate_limited(monkeypatch):
    monkeypatch.setattr(main_mod, "is_rate_limited", lambda ip, config=None: True)

    response = TestClient(main_mod.app).post(
        "/api/rag/chat", json={"message": "What AI work have you done?"}
    )

    assert response.status_code == 429
    assert "too many" in response.json()["error"].lower()


def test_chat_endpoint_uses_server_session_history(monkeypatch):
    captured_history = []

    async def fake_handle_chat_payload(payload, *, history=None):
        captured_history.append(history or [])
        return {
            "success": True,
            "response": f"answer to {payload['message']}",
            "sources": [],
            "provider": "local",
        }

    monkeypatch.setattr(main_mod, "is_rate_limited", lambda ip, config=None: False)
    monkeypatch.setattr(main_mod, "handle_chat_payload", fake_handle_chat_payload)
    client = TestClient(main_mod.app)

    first = client.post("/api/rag/chat", json={"message": "First question"})
    second = client.post(
        "/api/rag/chat",
        json={
            "message": "What about that?",
            "history": [{"role": "user", "content": "spoofed client history"}],
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert captured_history[0] == []
    assert captured_history[1][0]["content"] == "First question"
    assert "spoofed client history" not in str(captured_history[1])


def test_chat_reset_clears_server_session_history(monkeypatch):
    captured_history = []

    async def fake_handle_chat_payload(payload, *, history=None):
        captured_history.append(history or [])
        return {"success": True, "response": "ok", "sources": [], "provider": "local"}

    monkeypatch.setattr(main_mod, "is_rate_limited", lambda ip, config=None: False)
    monkeypatch.setattr(main_mod, "handle_chat_payload", fake_handle_chat_payload)
    client = TestClient(main_mod.app)

    client.post("/api/rag/chat", json={"message": "First question"})
    reset = client.post("/api/rag/chat/reset")
    client.post("/api/rag/chat", json={"message": "New first question"})

    assert reset.status_code == 200
    assert captured_history[-1] == []


def test_debug_cannot_be_enabled_on_vercel(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("DEBUG", "true")

    try:
        main_mod.assert_debug_disabled_on_vercel()
    except RuntimeError as exc:
        assert "DEBUG must be disabled" in str(exc)
    else:
        raise AssertionError("expected DEBUG on Vercel to fail")
