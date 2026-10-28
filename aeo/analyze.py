"""Turn raw answers into AEO metrics.

Definitions (per engine x intent group, n = successful answers):
  mention_rate        answers that name the target brand / n          (+ Wilson 95% CI)
  top1_rate           answers where the target is the first brand named / n
  avg_rank            mean position of the target among named brands (when named)
  owned_cite_rate     answers that cite an owned domain (higgsfield.ai) / n
  citation_share      owned citations / all citations
  share_of_voice      target mentions / all tracked-brand mentions (each brand once per answer)
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .models import EngineResult


@dataclass
class Brand:
    name: str
    aliases: list[str]
    domains: list[str] = field(default_factory=list)
    patterns: list[re.Pattern] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.patterns = [
            re.compile(r"(?<![\w-])" + re.escape(a) + r"(?![\w-])", re.IGNORECASE)
            for a in sorted(set(self.aliases) or {self.name}, key=len, reverse=True)
        ]

    def first_pos(self, text: str) -> int | None:
        hits = [m.start() for p in self.patterns if (m := p.search(text))]
        return min(hits) if hits else None

    def owns(self, domain: str) -> bool:
        return any(domain == d or domain.endswith("." + d) for d in self.domains)


def load_brands(cfg: dict) -> tuple[Brand, list[Brand]]:
    def mk(b: dict) -> Brand:
        return Brand(b["name"], b.get("aliases", []), b.get("domains", []))

    return mk(cfg["target"]), [mk(c) for c in cfg.get("competitors", [])]


def brand_order(text: str, brands: list[Brand]) -> list[str]:
    """Brands in order of first mention: a proxy for recommendation rank."""
    hits = [(pos, b.name) for b in brands if (pos := b.first_pos(text)) is not None]
    return [name for _, name in sorted(hits)]


def score(res: EngineResult, target: Brand, competitors: list[Brand]) -> dict:
    order = brand_order(res.text, [target, *competitors])
    owned = [c for c in res.citations if target.owns(c.domain)]
    return {
        "mentioned": target.name in order,
        "rank": order.index(target.name) + 1 if target.name in order else None,
        "top1": bool(order) and order[0] == target.name,
        "brands": order,
        "owned_cited": bool(owned),
        "owned_citations": len(owned),
        "citations": len(res.citations),
        "first_owned_citation_pos": next(
            (i + 1 for i, c in enumerate(res.citations) if target.owns(c.domain)), None),
    }


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def aggregate(results: list[EngineResult], target: Brand, competitors: list[Brand],
              key=lambda r: (r.engine, r.intent_id)) -> dict:
    groups: dict = defaultdict(list)
    for r in results:
        if r.ok:
            groups[key(r)].append((r, score(r, target, competitors)))

    out = {}
    for k, rows in sorted(groups.items()):
        n = len(rows)
        mentioned = sum(s["mentioned"] for _, s in rows)
        ranks = [s["rank"] for _, s in rows if s["rank"]]
        all_cites = sum(s["citations"] for _, s in rows)
        brand_counts = Counter(b for _, s in rows for b in s["brands"])
        total_brand_mentions = sum(brand_counts.values())
        out[k] = {
            "n": n,
            "mention_rate": mentioned / n,
            "mention_ci95": wilson(mentioned, n),
            "top1_rate": sum(s["top1"] for _, s in rows) / n,
            "avg_rank": sum(ranks) / len(ranks) if ranks else None,
            "owned_cite_rate": sum(s["owned_cited"] for _, s in rows) / n,
            "citation_share": (sum(s["owned_citations"] for _, s in rows) / all_cites) if all_cites else 0.0,
            "share_of_voice": (brand_counts[target.name] / total_brand_mentions) if total_brand_mentions else 0.0,
            "brand_mention_rate": {b: c / n for b, c in brand_counts.most_common()},
        }
    return out


def domain_hubs(results: list[EngineResult]) -> list[dict]:
    """Domains ranked by how many distinct intents (and answers) cite them.

    A domain cited across many intents is a "citation hub": one placement there
    moves many intents at once.
    """
    intents: dict[str, set] = defaultdict(set)
    engines: dict[str, set] = defaultdict(set)
    answers: Counter = Counter()
    for r in results:
        if not r.ok:
            continue
        for d in {c.domain for c in r.citations}:
            intents[d].add(r.intent_id)
            engines[d].add(r.engine)
            answers[d] += 1
    rows = [
        {"domain": d, "intents": len(intents[d]), "answers": answers[d], "engines": sorted(engines[d])}
        for d in answers
    ]
    return sorted(rows, key=lambda x: (-x["intents"], -x["answers"], x["domain"]))


def fanout_queries(results: list[EngineResult]) -> Counter:
    """Search queries the engines issued: the real keyword set to rank for."""
    return Counter(q.strip().lower() for r in results if r.ok for q in r.search_queries if q.strip())
