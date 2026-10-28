from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from ..models import Citation
from .base import Engine, dedupe

API = "https://api.openai.com/v1/responses"


class OpenAIEngine(Engine):
    """OpenAI Responses API with the web_search tool (proxy for ChatGPT search)."""

    def build_request(self, prompt: str) -> tuple[str, dict, dict]:
        body: dict = {
            "model": self.model,
            "input": prompt,
            "tools": [{"type": self.cfg.get("tool_type", "web_search")}],
            # Ask for the full list of consulted sources, not only inline citations.
            "include": ["web_search_call.action.sources"],
        }
        if "tool_choice" in self.cfg:
            body["tool_choice"] = self.cfg["tool_choice"]
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        return API, headers, body

    def parse(self, data: dict) -> tuple[str, list[Citation], list[Citation], list[str]]:
        text, cited, retrieved, queries = "", [], [], []
        for item in data.get("output", []):
            if item.get("type") == "web_search_call":
                action = item.get("action") or {}
                if action.get("query"):
                    queries.append(action["query"])
                queries.extend(action.get("queries") or [])
                for s in action.get("sources") or []:
                    if s.get("url"):
                        retrieved.append(Citation(url=_clean(s["url"]), title=s.get("title", "")))
            elif item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") != "output_text":
                        continue
                    text += c.get("text", "")
                    for a in c.get("annotations", []):
                        if a.get("type") == "url_citation" and a.get("url"):
                            cited.append(Citation(url=_clean(a["url"]), title=a.get("title", "")))
        return text, dedupe(cited), dedupe(retrieved), list(dict.fromkeys(queries))


def _clean(url: str) -> str:
    """Drop the utm_source=openai marker so URLs dedupe across engines."""
    p = urlparse(url)
    q = [(k, v) for k, v in parse_qsl(p.query) if not k.startswith("utm_")]
    return urlunparse(p._replace(query=urlencode(q)))
