import logging
import os
import time
from functools import wraps
from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("stock_research")

DEFAULT_PROJECT = "Agentic Stock Assistant"
DEFAULT_ENDPOINT = "https://api.smith.langchain.com"


def _clean_env(value: str | None) -> str:
    return (value or "").strip().strip('"').strip("'")


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _falsy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"0", "false", "no", "off"}


def configure_observability() -> None:
    """Set LangSmith/LangChain tracing env vars before the graph is imported."""
    load_dotenv()
    api_key = _clean_env(os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY"))
    project = _clean_env(
        os.getenv("LANGSMITH_PROJECT")
        or os.getenv("LANGCHAIN_PROJECT")
        or DEFAULT_PROJECT
    )
    endpoint = _clean_env(os.getenv("LANGSMITH_ENDPOINT") or DEFAULT_ENDPOINT)

    os.environ["LANGCHAIN_PROJECT"] = project
    os.environ["LANGSMITH_PROJECT"] = project
    os.environ["LANGSMITH_ENDPOINT"] = endpoint

    if api_key:
        os.environ["LANGSMITH_API_KEY"] = api_key
        os.environ["LANGCHAIN_API_KEY"] = api_key
        explicit = os.getenv("LANGSMITH_TRACING") or os.getenv("LANGCHAIN_TRACING_V2")
        if not _falsy(explicit):
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGCHAIN_TRACING_V2"] = "true"

    logger.info(
        "LangSmith tracing=%s project=%s",
        tracing_enabled(),
        project,
    )


def tracing_enabled() -> bool:
    has_key = bool(_clean_env(os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")))
    return has_key and (
        _truthy(os.getenv("LANGSMITH_TRACING")) or _truthy(os.getenv("LANGCHAIN_TRACING_V2"))
    )


def project_name() -> str:
    return _clean_env(os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT") or DEFAULT_PROJECT)


def current_trace_url() -> str | None:
    """Return the LangSmith URL for the active run, if tracing is on."""
    if not tracing_enabled():
        return None
    try:
        from langsmith.run_helpers import get_current_run_tree

        tree = get_current_run_tree()
        if tree is None:
            return None
        if hasattr(tree, "get_url"):
            return tree.get_url()
        run_id = getattr(tree, "id", None)
        if run_id:
            return f"https://smith.langchain.com/o/default/projects/p/{project_name()}?peek={run_id}"
    except Exception:
        logger.debug("Could not resolve LangSmith trace URL", exc_info=True)
    return None


def _trace_event(node: str, status: str, started: float, error: str | None = None) -> dict[str, Any]:
    event: dict[str, Any] = {
        "node": node,
        "status": status,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
    }
    if error:
        event["error"] = error
    return event


def instrumented(node_name: str, output_key: str | None = None) -> Callable:
    """Time a graph node, log failures, and append a run_trace event."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(state: dict) -> dict:
            started = time.perf_counter()
            ticker = state.get("ticker")
            try:
                result = fn(state)
                logger.info("node=%s ticker=%s status=ok", node_name, ticker)
                return {**result, "run_trace": [_trace_event(node_name, "ok", started)]}
            except Exception as exc:
                logger.exception("node=%s ticker=%s status=error", node_name, ticker)
                payload: dict[str, Any] = {
                    "errors": [f"{node_name}: {exc}"],
                    "run_trace": [_trace_event(node_name, "error", started, str(exc))],
                }
                if output_key:
                    payload[output_key] = {"error": str(exc)}
                return payload

        return wrapper

    return decorator


configure_observability()
