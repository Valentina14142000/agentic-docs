import os

from config.settings import Settings


def test_settings_use_supported_default_model(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GOOGLE_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_MODEL_NAME", raising=False)
    monkeypatch.delenv("GOOGLE_MODEL_NAME", raising=False)

    settings = Settings()

    assert settings.model_name == "gemini-2.0-flash"


def test_settings_allow_model_override(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
    monkeypatch.delenv("GOOGLE_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_MODEL_NAME", raising=False)
    monkeypatch.delenv("GOOGLE_MODEL_NAME", raising=False)

    settings = Settings()

    assert settings.model_name == "gemini-2.0-flash-lite"
