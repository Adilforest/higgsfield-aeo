from __future__ import annotations

import csv
from pathlib import Path

from .analyze import Brand, aggregate, domain_hubs, fanout_queries
from .models import EngineResult


def _pct(x: float | None) -> str:
    return "–" if x is None else f"{x * 100:.0f}%"


def write_report(results: list[EngineResult], target: Brand, competitors: list[Brand],
                 out_dir: Path, top: int = 25) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    by_intent = aggregate(results, target, competitors)
    by_engine = aggregate(results, target, competitors, key=lambda r: r.engine)
    hubs = domain_hubs(results)
    queries = fanout_queries(results)
    errors = [r for r in results if not r.ok]

    lines = [f"# AEO visibility report: {target.name}", ""]
    lines += [f"Answers: {sum(r.ok for r in results)} ok, {len(errors)} failed. "
              f"Engines: {', '.join(sorted({r.engine for r in results}))}.", ""]

    lines += ["## By engine", "",
              "| engine | n | mention rate (95% CI) | top-1 | avg rank | cites owned domain | citation share | share of voice |",
              "|---|---|---|---|---|---|---|---|"]
    for eng, m in by_engine.items():
        lo, hi = m["mention_ci95"]
        rank = f"{m['avg_rank']:.1f}" if m["avg_rank"] else "–"
        lines.append(f"| {eng} | {m['n']} | {_pct(m['mention_rate'])} ({_pct(lo)}–{_pct(hi)}) | "
                     f"{_pct(m['top1_rate'])} | {rank} | {_pct(m['owned_cite_rate'])} | "
                     f"{_pct(m['citation_share'])} | {_pct(m['share_of_voice'])} |")

    lines += ["", "## By engine × intent", "",
              "| engine | intent | n | mention | top-1 | avg rank | cites owned | leader |",
              "|---|---|---|---|---|---|---|---|"]
    for (eng, intent), m in by_intent.items():
        leader = next(iter(m["brand_mention_rate"]), "–")
        rank = f"{m['avg_rank']:.1f}" if m["avg_rank"] else "–"
        lines.append(f"| {eng} | {intent} | {m['n']} | {_pct(m['mention_rate'])} | {_pct(m['top1_rate'])} | "
                     f"{rank} | {_pct(m['owned_cite_rate'])} | {leader} |")

    lines += ["", "## Brand leaderboard (share of answers naming the brand)", ""]
    for eng, m in by_engine.items():
        lines.append(f"**{eng}:** " + ", ".join(
            f"{b} {_pct(v)}" for b, v in list(m["brand_mention_rate"].items())[:12]))
        lines.append("")

    lines += ["## Citation hubs (domains cited across most intents)", "",
              "| domain | intents | answers | engines |", "|---|---|---|---|"]
    for h in hubs[:top]:
        lines.append(f"| {h['domain']} | {h['intents']} | {h['answers']} | {', '.join(h['engines'])} |")

    if queries:
        lines += ["", "## Fan-out search queries issued by the engines", "",
                  "These are the queries the engine actually ran. Ranking for them puts pages into the retrieval pool.", ""]
        lines += [f"- `{q}` × {c}" for q, c in queries.most_common(top)]

    if errors:
        lines += ["", "## Errors", ""]
        lines += [f"- {r.engine} / {r.intent_id} #{r.sample}: {(r.error or 'empty answer')[:200]}" for r in errors[:20]]

    report = out_dir / "report.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with open(out_dir / "domains.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["domain", "intents", "answers", "engines"])
        for h in hubs:
            w.writerow([h["domain"], h["intents"], h["answers"], " ".join(h["engines"])])

    with open(out_dir / "metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["engine", "intent", "n", "mention_rate", "ci_low", "ci_high", "top1_rate",
                    "avg_rank", "owned_cite_rate", "citation_share", "share_of_voice"])
        for (eng, intent), m in by_intent.items():
            w.writerow([eng, intent, m["n"], round(m["mention_rate"], 4), round(m["mention_ci95"][0], 4),
                        round(m["mention_ci95"][1], 4), round(m["top1_rate"], 4),
                        round(m["avg_rank"], 2) if m["avg_rank"] else "", round(m["owned_cite_rate"], 4),
                        round(m["citation_share"], 4), round(m["share_of_voice"], 4)])
    return report
