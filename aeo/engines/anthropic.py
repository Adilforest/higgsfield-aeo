from __future__ import annotations

from ..models import Citation
from .base import Engine, dedupe

API = "https://api.anthropic.com/v1/messages"


class AnthropicEngine(Engine):
    """Anthropic Messages API with the server-side web_search tool."""

    def _body(self, messages: list[dict]) -> dict:
        return {
            "model": self.model,
            "max_tokens": self.cfg.get("max_tokens", 2048),
            "messages": messages,
            "tools": [{
                "type": self.cfg.get("tool_type", "web_search_20250305"),
                "name": "web_search",
                "max_uses": self.cfg.get("max_uses", 5),
            }],
        }

    def _headers(self) -> dict:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def build_request(self, prompt: str) -> tuple[str, dict, dict]:
        return API, self._headers(), self._body([{"role": "user", "content": prompt}])

    def ask(self, prompt: str):
        messages = [{"role": "user", "content": prompt}]
        blocks: list[dict] = []
        # Long searches can end with stop_reason=pause_turn; resend to let the
        # server continue the same turn.
        for _ in range(3):
            data = self._post(API, self._headers(), self._body(messages))
            blocks += data.get("content", [])
            if data.get("stop_reason") != "pause_turn":
                break
            messages = [messages[0], {"role": "assistant", "content": blocks}]
        return self.parse({"content": blocks})

    def parse(self, data: dict) -> tuple[str, list[Citation], list[Citation], list[str]]:
        text, cited, retrieved, queries = "", [], [], []
        for b in data.get("content", []):
            t = b.get("type")
            if t == "text":
                text += b.get("text", "")
                for c in b.get("citations") or []:
                    if c.get("url"):
                        cited.append(Citation(url=c["url"], title=c.get("title", "")))
            elif t == "server_tool_use" and b.get("name") == "web_search":
                q = (b.get("input") or {}).get("query")
                if q:
                    queries.append(q)
            elif t == "web_search_tool_result" and isinstance(b.get("content"), list):
                for r in b["content"]:
                    if r.get("url"):
                        retrieved.append(Citation(url=r["url"], title=r.get("title", "")))
        return text, dedupe(cited), dedupe(retrieved), queries
