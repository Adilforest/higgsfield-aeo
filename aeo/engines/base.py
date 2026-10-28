from __future__ import annotations

import os
import time

import requests

from ..models import Citation

RETRY_STATUS = {429, 500, 502, 503, 504}


class EngineError(RuntimeError):
    pass


class Engine:
    """Adapter for one answer engine.

    Subclasses implement build_request() and parse() only, so parsing can be
    tested against saved API responses without network access.
    """

    def __init__(self, name: str, cfg: dict):
        self.name = name
        self.cfg = cfg
        self.model = cfg["model"]
        self.timeout = cfg.get("timeout", 120)

    @property
    def api_key(self) -> str:
        return os.environ.get(self.cfg.get("api_key_env", ""), "")

    def available(self) -> bool:
        return bool(self.api_key)

    def build_request(self, prompt: str) -> tuple[str, dict, dict]:
        """Return (url, headers, json_body)."""
        raise NotImplementedError

    def parse(self, data: dict) -> tuple[str, list[Citation], list[Citation], list[str]]:
        """Return (text, citations, retrieved, search_queries)."""
        raise NotImplementedError

    def postprocess(self, citations: list[Citation]) -> list[Citation]:
        return citations

    def ask(self, prompt: str) -> tuple[str, list[Citation], list[Citation], list[str]]:
        url, headers, body = self.build_request(prompt)
        data = self._post(url, headers, body)
        text, citations, retrieved, queries = self.parse(data)
        return text, self.postprocess(citations), retrieved, queries

    def _post(self, url: str, headers: dict, body: dict, attempts: int = 4) -> dict:
        for attempt in range(attempts):
            resp = requests.post(url, headers=headers, json=body, timeout=self.timeout)
            if resp.status_code in RETRY_STATUS and attempt < attempts - 1:
                time.sleep(2 ** attempt * 2)
                continue
            if resp.status_code >= 400:
                raise EngineError(f"{self.name}: HTTP {resp.status_code}: {resp.text[:500]}")
            return resp.json()
        raise EngineError(f"{self.name}: retries exhausted")


def dedupe(citations: list[Citation]) -> list[Citation]:
    seen: set[str] = set()
    out = []
    for c in citations:
        if c.url and c.url not in seen:
            seen.add(c.url)
            out.append(c)
    return out
