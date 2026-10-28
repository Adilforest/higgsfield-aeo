from __future__ import annotations

from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse


def domain_of(url: str) -> str:
    """Registrable-ish host without www. and port: https://www.g2.com/x -> g2.com"""
    host = urlparse(url).netloc.lower().split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


@dataclass
class Citation:
    url: str
    title: str = ""
    domain: str = ""

    def __post_init__(self) -> None:
        if not self.domain:
            self.domain = domain_of(self.url)


@dataclass
class EngineResult:
    """One answer from one engine for one prompt (one sample)."""

    engine: str
    model: str
    intent_id: str
    prompt: str
    sample: int
    text: str = ""
    # Sources the engine shows to the user as citations (in display order).
    citations: list[Citation] = field(default_factory=list)
    # Sources the engine retrieved but did not necessarily cite (when the API exposes them).
    retrieved: list[Citation] = field(default_factory=list)
    # Search queries the engine issued (Gemini webSearchQueries = query fan-out).
    search_queries: list[str] = field(default_factory=list)
    error: str | None = None
    latency_ms: int = 0
    ts: str = ""

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.text)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EngineResult":
        d = dict(d)
        d["citations"] = [Citation(**c) for c in d.get("citations", [])]
        d["retrieved"] = [Citation(**c) for c in d.get("retrieved", [])]
        return cls(**d)
