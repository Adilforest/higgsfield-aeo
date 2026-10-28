"""Intent panels: load hand-written intents and expand a taxonomy into hundreds."""
from __future__ import annotations

import itertools
import re
from pathlib import Path

import yaml

PLACEHOLDER = re.compile(r"\{(\w+)\}")


def load_intents(path: str | Path) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    intents = data.get("intents", [])
    for it in intents:
        if not it.get("prompts"):
            raise ValueError(f"intent {it.get('id')!r} has no prompts")
        it.setdefault("cluster", it["id"])
        it.setdefault("priority", 0)
    return intents


def expand_taxonomy(path: str | Path, limit: int | None = None) -> list[dict]:
    """Cartesian product of template placeholders x dimension values, ranked by weight.

    priority = template.weight x product(dimension value weights), scaled to 0..100.
    """
    tax = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    dims: dict[str, list[dict]] = tax["dimensions"]
    out: dict[str, dict] = {}
    for tpl in tax["templates"]:
        names = list(dict.fromkeys(PLACEHOLDER.findall(tpl["text"])))
        unknown = [n for n in names if n not in dims]
        if unknown:
            raise ValueError(f"template {tpl['id']!r}: unknown dimensions {unknown}")
        for combo in itertools.product(*(dims[n] for n in names)):
            values = dict(zip(names, combo))
            if _excluded(values, tax.get("exclude", [])):
                continue
            weight = tpl.get("weight", 1.0)
            for v in combo:
                weight *= v.get("weight", 1.0)
            cluster = next((v["id"] for n, v in values.items() if n.startswith("use_case")), tpl["id"])
            iid = "--".join([cluster, tpl["id"],
                             *(v["id"] for n, v in values.items() if not n.startswith("use_case"))])
            out[iid] = {
                "id": iid,
                "cluster": cluster,
                "template": tpl["id"],
                "funnel": tpl.get("funnel", "consideration"),
                "dims": {n: v["id"] for n, v in values.items()},
                "priority": weight,
                "prompts": [tpl["text"].format(**{n: v["text"] for n, v in values.items()})],
            }
    ranked = sorted(out.values(), key=lambda x: (-x["priority"], x["id"]))
    top = max((x["priority"] for x in ranked), default=1.0) or 1.0
    for x in ranked:
        x["priority"] = round(100 * x["priority"] / top, 1)
    return ranked[:limit] if limit else ranked


def _excluded(values: dict, rules: list[dict]) -> bool:
    """A rule like {use_case: music-video, platform: amazon} drops that combination."""
    return any(all(values.get(k, {}).get("id") == v for k, v in rule.items()) for rule in rules)


def dump_intents(intents: list[dict], path: str | Path | None) -> str:
    text = yaml.safe_dump({"intents": intents}, sort_keys=False, allow_unicode=True, width=120)
    if path:
        Path(path).write_text(text, encoding="utf-8")
    return text
