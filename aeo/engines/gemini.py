from __future__ import annotations

import requests

from ..models import Citation, domain_of
from .base import Engine, dedupe

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
REDIRECT_HOST = "vertexaisearch.cloud.google.com"


class GeminiEngine(Engine):
    """Gemini API with Grounding with Google Search.

    Closest programmatic proxy for the Gemini app / AI Mode: the model decides
    whether to search, issues its own fan-out queries (webSearchQueries) and
    returns the sources it grounded on (groundingChunks).
    """

    def build_request(self, prompt: str) -> tuple[str, dict, dict]:
        body: dict = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        # google_search: false gives the parametric-memory baseline (no retrieval).
        if self.cfg.get("google_search", True):
            body["tools"] = [{"google_search": {}}]
        if "temperature" in self.cfg:
            body["generationConfig"] = {"temperature": self.cfg["temperature"]}
        headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}
        return API.format(model=self.model), headers, body

    def parse(self, data: dict) -> tuple[str, list[Citation], list[Citation], list[str]]:
        cand = (data.get("candidates") or [{}])[0]
        parts = (cand.get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        gm = cand.get("groundingMetadata") or {}
        chunks = [ch.get("web") or {} for ch in gm.get("groundingChunks", [])]

        # Order citations by first use in the answer (groundingSupports), then
        # append chunks that were retrieved but never attached to a segment.
        order: list[int] = []
        for sup in sorted(gm.get("groundingSupports", []),
                          key=lambda s: (s.get("segment") or {}).get("startIndex", 0)):
            for i in sup.get("groundingChunkIndices", []):
                if i not in order and i < len(chunks):
                    order.append(i)
        cited = [_citation(chunks[i]) for i in order if chunks[i].get("uri")]
        uncited = [_citation(w) for i, w in enumerate(chunks) if i not in order and w.get("uri")]
        return text, cited + uncited, [], list(gm.get("webSearchQueries", []))

    def postprocess(self, citations: list[Citation]) -> list[Citation]:
        if not self.cfg.get("resolve_redirects", False):
            return citations
        return dedupe([_resolve(c, self.timeout) for c in citations])


def _citation(web: dict) -> Citation:
    title = web.get("title", "")
    # Grounding chunk URIs are opaque redirects; the title usually carries the
    # source domain (e.g. "zapier.com"), which is all we need for domain stats.
    domain = title.lower() if "." in title and " " not in title else domain_of(web["uri"])
    return Citation(url=web["uri"], title=title, domain=domain.removeprefix("www."))


def _resolve(c: Citation, timeout: int) -> Citation:
    if REDIRECT_HOST not in c.url:
        return c
    try:
        r = requests.head(c.url, allow_redirects=False, timeout=min(timeout, 15))
        loc = r.headers.get("Location")
        if not loc:
            r = requests.get(c.url, allow_redirects=False, timeout=min(timeout, 15), stream=True)
            loc = r.headers.get("Location")
        if loc:
            return Citation(url=loc, title=c.title, domain=domain_of(loc))
    except requests.RequestException:
        pass
    return c
