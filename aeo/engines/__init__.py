from .anthropic import AnthropicEngine
from .base import Engine, EngineError
from .gemini import GeminiEngine
from .openai import OpenAIEngine
from .perplexity import PerplexityEngine

ADAPTERS: dict[str, type[Engine]] = {
    "gemini": GeminiEngine,
    "openai": OpenAIEngine,
    "perplexity": PerplexityEngine,
    "anthropic": AnthropicEngine,
}


def build_engine(name: str, cfg: dict) -> Engine:
    adapter = cfg.get("adapter", name)
    if adapter not in ADAPTERS:
        raise ValueError(f"engine {name!r}: unknown adapter {adapter!r} (have {sorted(ADAPTERS)})")
    return ADAPTERS[adapter](name, cfg)


__all__ = ["ADAPTERS", "Engine", "EngineError", "build_engine"]
