"""API endpoint tests (Flask test client)."""

import pytest

from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    MAX_TEXT_LENGTH = 50  # validation test ke liye chhoti limit


@pytest.fixture
def client():
    app = create_app(TestConfig)
    # Asli translator ki jagah fake: network nahi lagegi
    class FakeTranslator:
        def translate(self, text, source, target):
            if text == "boom":
                from services.translator import TranslationError

                raise TranslationError("down")
            return f"[{source}->{target}] {text}"

    app.translator = FakeTranslator()
    return app.test_client()


def test_health(client):
    assert client.get("/health").status_code == 200


def test_languages_list(client):
    res = client.get("/api/languages")
    assert res.status_code == 200
    assert "ur-PK" in res.get_json()["languages"]


def test_translate_success(client):
    res = client.post(
        "/api/translate",
        json={"text": "hello", "source": "en-GB", "target": "ur-PK"},
    )
    assert res.status_code == 200
    assert res.get_json()["translation"] == "[en-GB->ur-PK] hello"


def test_translate_empty_text_400(client):
    res = client.post(
        "/api/translate", json={"text": "  ", "source": "en-GB", "target": "ur-PK"}
    )
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_translate_too_long_400(client):
    res = client.post(
        "/api/translate",
        json={"text": "x" * 100, "source": "en-GB", "target": "ur-PK"},
    )
    assert res.status_code == 400


def test_translate_bad_language_400(client):
    res = client.post(
        "/api/translate",
        json={"text": "hello", "source": "xx", "target": "ur-PK"},
    )
    assert res.status_code == 400


def test_translate_provider_down_502(client):
    res = client.post(
        "/api/translate", json={"text": "boom", "source": "en-GB", "target": "ur-PK"}
    )
    assert res.status_code == 502
    assert "error" in res.get_json()
