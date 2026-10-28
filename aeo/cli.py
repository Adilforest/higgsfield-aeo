from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .analyze import load_brands
from .engines import build_engine
from .intents import dump_intents, expand_taxonomy, load_intents
from .models import EngineResult
from .report import write_report


def _yaml(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _engines(cfg_path: str, names: str | None):
    cfg = _yaml(cfg_path)["engines"]
    wanted = names.split(",") if names else [n for n, c in cfg.items() if c.get("enabled")]
    engines = []
    for n in wanted:
        if n not in cfg:
            sys.exit(f"unknown engine {n!r}; configured: {', '.join(cfg)}")
        eng = build_engine(n, cfg[n])
        if eng.available():
            engines.append(eng)
        else:
            print(f"skip {n}: env var {cfg[n].get('api_key_env')} is not set", file=sys.stderr)
    return engines


def cmd_engines(args) -> None:
    for name, c in _yaml(args.engines_config)["engines"].items():
        eng = build_engine(name, c)
        state = "ready" if eng.available() else f"no key ({c.get('api_key_env')})"
        print(f"{name:14} {c.get('adapter', name):11} {c['model']:28} enabled={c.get('enabled', False)!s:5} {state}")


def cmd_run(args) -> None:
    engines = _engines(args.engines_config, args.engines)
    if not engines:
        sys.exit("no engines available: set API keys (see config/engines.yaml)")
    intents = load_intents(args.intents)
    if args.cluster:
        intents = [i for i in intents if i["cluster"] in args.cluster.split(",")]
    intents = sorted(intents, key=lambda i: -i["priority"])[: args.limit or None]

    jobs = []
    for it in intents:
        prompts = it["prompts"] if args.prompts == "all" else it["prompts"][:1]
        for p in prompts:
            for eng in engines:
                for s in range(args.samples):
                    jobs.append((eng, it["id"], p, s))

    out_dir = Path(args.out) / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "results.jsonl"
    print(f"{len(jobs)} calls -> {raw_path}", file=sys.stderr)

    lock = threading.Lock()
    results: list[EngineResult] = []

    def run(job) -> EngineResult:
        eng, iid, prompt, s = job
        res = EngineResult(engine=eng.name, model=eng.model, intent_id=iid, prompt=prompt, sample=s,
                           ts=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        t0 = time.monotonic()
        try:
            res.text, res.citations, res.retrieved, res.search_queries = eng.ask(prompt)
        except Exception as e:  # keep the run going; failures are reported
            res.error = f"{type(e).__name__}: {e}"
        res.latency_ms = int((time.monotonic() - t0) * 1000)
        return res

    with ThreadPoolExecutor(max_workers=args.workers) as pool, open(raw_path, "a", encoding="utf-8") as f:
        for i, fut in enumerate(as_completed(pool.submit(run, j) for j in jobs), 1):
            res = fut.result()
            with lock:
                results.append(res)
                f.write(json.dumps(res.to_dict(), ensure_ascii=False) + "\n")
                f.flush()
            mark = "ok" if res.ok else "ERR"
            print(f"[{i}/{len(jobs)}] {res.engine} {res.intent_id} #{res.sample} {mark}", file=sys.stderr)

    target, competitors = load_brands(_yaml(args.brand))
    print(write_report(results, target, competitors, out_dir))


def cmd_report(args) -> None:
    run_dir = Path(args.run_dir)
    results = [EngineResult.from_dict(json.loads(line))
               for line in (run_dir / "results.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    target, competitors = load_brands(_yaml(args.brand))
    print(write_report(results, target, competitors, run_dir))


def cmd_expand(args) -> None:
    intents = expand_taxonomy(args.taxonomy, args.limit)
    text = dump_intents(intents, args.out)
    if args.out:
        print(f"{len(intents)} intents -> {args.out}", file=sys.stderr)
    else:
        print(text)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="aeo", description="Multi-engine AI answer visibility tracker")
    p.add_argument("--engines-config", default="config/engines.yaml")
    p.add_argument("--brand", default="config/brand.yaml")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("engines", help="list configured engines and key status").set_defaults(func=cmd_engines)

    r = sub.add_parser("run", help="ask engines, store raw answers, build report")
    r.add_argument("--intents", default="config/intents/pilot.yaml")
    r.add_argument("--engines", help="comma list; default = enabled in engines config")
    r.add_argument("--samples", type=int, default=5, help="repeats per prompt (answers are non-deterministic)")
    r.add_argument("--prompts", choices=["canonical", "all"], default="all")
    r.add_argument("--cluster", help="comma list of clusters to include")
    r.add_argument("--limit", type=int, default=0, help="top-N intents by priority")
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--out", default="runs")
    r.set_defaults(func=cmd_run)

    rep = sub.add_parser("report", help="rebuild report from a run directory")
    rep.add_argument("run_dir")
    rep.set_defaults(func=cmd_report)

    e = sub.add_parser("expand", help="expand an intent taxonomy into an intent panel")
    e.add_argument("taxonomy")
    e.add_argument("--limit", type=int, default=500)
    e.add_argument("--out")
    e.set_defaults(func=cmd_expand)

    args = p.parse_args(argv)
    args.func(args)
