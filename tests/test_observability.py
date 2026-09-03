import os

from app.observability import project_name, tracing_enabled


def test_tracing_off_without_langsmith_key(monkeypatch):
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
    assert tracing_enabled() is False


def test_default_project_name():
    name = project_name()
    assert name
    assert name.strip('"') == name
