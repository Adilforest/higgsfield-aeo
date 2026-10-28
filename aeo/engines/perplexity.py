from __future__ import annotations

import re

from ..models import Citation
from .base import Engine, dedupe

API = "https://api.perplexity.ai/v1/agent"
MARKER = re.compile(r"\[(\d+)\]")


class PerplexityEngine(Engine):
    """Perplexity Agent API with web_search (Sonar chat completions were retired 2026-09-27).

    parse() also accepts the legacy chat-completions shape (top-level
    `citations` / `search_results`) so old raw runs can still be re-reported.
    """

    def build_request(self, prompt: str) -> tuple[str, dict, dict]:
        body = {"model": self.model, "input": prompt, "tools": [{"type": "web_search"}]}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        return self.cfg.get("endpoint", API), headers, body

    def parse(self, data: dict) -> tuple[str, list[Citation], list[Citation], list[str]]:
        if "choices" in data:
            return _parse_legacy(data)
        text, queries, results = "", [], []
        for item in data.get("output", []):
            if item.get("type") == "search_results":
                queries.extend(item.get("queries") or [])
                results.extend(item.get("results") or [])
            elif item.get("type") == "message":
                text += "".join(c.get("text", "") for c in item.get("content", []))
        by_id = {str(r.get("id")): r for r in results if r.get("url")}
        # Citations = results referenced by [n] markers, in order of first appearance.
        cited = [Citation(url=by_id[n]["url"], title=by_id[n].get("title", ""))
                 for n in dict.fromkeys(MARKER.findall(text)) if n in by_id]
        retrieved = [Citation(url=r["url"], title=r.get("title", "")) for r in results if r.get("url")]
        return text, dedupe(cited), dedupe(retrieved), list(dict.fromkeys(queries))


def _parse_legacy(data: dict) -> tuple[str, list[Citation], list[Citation], list[str]]:
    choice = (data.get("choices") or [{}])[0]
    text = (choice.get("message") or {}).get("content", "")
    results = data.get("search_results") or []
    titles = {r.get("url"): r.get("title", "") for r in results}
    urls = data.get("citations") or [r.get("url") for r in results]
    cited = [Citation(url=u, title=titles.get(u, "")) for u in urls if u]
    retrieved = [Citation(url=r["url"], title=r.get("title", "")) for r in results if r.get("url")]
    return text, dedupe(cited), dedupe(retrieved), []
