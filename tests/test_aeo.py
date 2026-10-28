import json
import tempfile
import unittest
from pathlib import Path

import yaml

from aeo.analyze import Brand, aggregate, brand_order, domain_hubs, load_brands, score, wilson
from aeo.engines import build_engine
from aeo.intents import expand_taxonomy, load_intents
from aeo.models import Citation, EngineResult
from aeo.report import write_report

ROOT = Path(__file__).resolve().parent.parent
FIX = Path(__file__).resolve().parent / "fixtures"


def fixture(name: str) -> dict:
    return json.loads((FIX / f"{name}.json").read_text(encoding="utf-8"))


def engine(name: str, adapter: str, **cfg):
    return build_engine(name, {"adapter": adapter, "model": "m", "api_key_env": "NOPE", **cfg})


class ParserTests(unittest.TestCase):
    def test_gemini_orders_citations_by_first_supported_segment(self):
        text, cites, _, queries = engine("gemini", "gemini").parse(fixture("gemini"))
        self.assertIn("Higgsfield is a good pick", text)
        # reddit + zapier support the first sentence, higgsfield the second, g2 is uncited.
        self.assertEqual([c.domain for c in cites], ["reddit.com", "zapier.com", "higgsfield.ai", "g2.com"])
        self.assertEqual(queries, ["best AI tool for video ads 2026", "AI video ad generator comparison"])

    def test_gemini_request_enables_google_search_tool(self):
        url, headers, body = engine("gemini", "gemini").build_request("hi")
        self.assertTrue(url.endswith("/models/m:generateContent"))
        self.assertEqual(body["tools"], [{"google_search": {}}])
        self.assertIn("x-goog-api-key", headers)

    def test_gemini_without_search_is_memory_baseline(self):
        _, _, body = engine("gemini", "gemini", google_search=False).build_request("hi")
        self.assertNotIn("tools", body)

    def test_openai_dedupes_and_strips_utm(self):
        text, cites, retrieved, queries = engine("chatgpt", "openai").parse(fixture("openai"))
        self.assertTrue(text.startswith("Arcads and Creatify"))
        self.assertEqual([c.url for c in cites], ["https://zapier.com/blog/best-ai-video-generator/"])
        self.assertEqual([c.domain for c in retrieved], ["g2.com", "zapier.com"])
        self.assertEqual(queries, ["best AI video ad tools 2026"])

    def test_perplexity_agent_api_cites_by_marker_order(self):
        text, cites, retrieved, queries = engine("perplexity", "perplexity").parse(fixture("perplexity"))
        self.assertTrue(text.startswith("Top picks: Higgsfield"))
        self.assertEqual([c.domain for c in cites], ["higgsfield.ai", "example-review.com"])
        self.assertEqual(len(retrieved), 3)
        self.assertEqual(queries, ["best AI video ad tools 2026"])

    def test_perplexity_legacy_chat_completions(self):
        text, cites, retrieved, _ = engine("perplexity", "perplexity").parse(fixture("perplexity_legacy"))
        self.assertEqual([c.domain for c in cites], ["example-review.com", "higgsfield.ai"])
        self.assertEqual(cites[1].title, "AI video ads with Higgsfield")
        self.assertEqual(len(retrieved), 3)

    def test_anthropic_separates_cited_from_retrieved(self):
        text, cites, retrieved, queries = engine("claude", "anthropic").parse(fixture("anthropic"))
        self.assertEqual(text, "Based on reviews, Creatify is the most recommended tool for video ads, followed by Synthesia.")
        self.assertEqual([c.domain for c in cites], ["g2.com"])
        self.assertEqual([c.domain for c in retrieved], ["g2.com", "creatify.ai"])
        self.assertEqual(queries, ["best AI tool for video ads"])


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.target, self.comps = load_brands(yaml.safe_load((ROOT / "config/brand.yaml").read_text(encoding="utf-8")))

    def test_whole_word_matching(self):
        brands = [self.target, *self.comps]
        self.assertEqual(brand_order("Use Canvas and captions for subtitles.", brands), [])
        self.assertEqual(brand_order("Higgsfield's Click to Ad beats Canva.", brands), ["Higgsfield", "Canva"])
        self.assertEqual(brand_order("Try Veo 3, then HIGGSFIELD AI.", brands), ["Google Veo", "Higgsfield"])

    def test_score_rank_and_owned_citation(self):
        r = EngineResult("gemini", "m", "i", "p", 0, text="Arcads first, then Higgsfield.",
                         citations=[Citation("https://www.reddit.com/r/x"), Citation("https://higgsfield.ai/ads")])
        s = score(r, self.target, self.comps)
        self.assertEqual(s["rank"], 2)
        self.assertFalse(s["top1"])
        self.assertTrue(s["owned_cited"])
        self.assertEqual(s["first_owned_citation_pos"], 2)

    def test_aggregate(self):
        mk = lambda t, c: EngineResult("gemini", "m", "video-ads", "p", 0, text=t, citations=[Citation(u) for u in c])
        rows = [
            mk("Higgsfield is best. Creatify is fine.", ["https://higgsfield.ai/a", "https://g2.com/x"]),
            mk("Creatify, then Higgsfield.", ["https://g2.com/x"]),
            mk("Arcads.", []),
            mk("Creatify.", ["https://zapier.com/y"]),
            EngineResult("gemini", "m", "video-ads", "p", 1, error="HTTP 500"),
        ]
        m = aggregate(rows, self.target, self.comps)[("gemini", "video-ads")]
        self.assertEqual(m["n"], 4)
        self.assertAlmostEqual(m["mention_rate"], 0.5)
        self.assertAlmostEqual(m["top1_rate"], 0.25)
        self.assertAlmostEqual(m["avg_rank"], 1.5)
        self.assertAlmostEqual(m["owned_cite_rate"], 0.25)
        self.assertAlmostEqual(m["citation_share"], 0.25)
        self.assertAlmostEqual(m["share_of_voice"], 2 / 6)
        self.assertEqual(next(iter(m["brand_mention_rate"])), "Creatify")
        hubs = domain_hubs(rows)
        self.assertEqual(hubs[0]["domain"], "g2.com")

    def test_wilson(self):
        lo, hi = wilson(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=3)
        self.assertAlmostEqual(hi, 0.7634, places=3)
        self.assertEqual(wilson(0, 0), (0.0, 0.0))


class IntentTests(unittest.TestCase):
    def test_pilot_loads(self):
        intents = load_intents(ROOT / "config/intents/pilot.yaml")
        self.assertEqual(intents[0]["prompts"][0], "What is the best AI tool for creating video ads?")

    def test_taxonomy_expands_to_500_ranked(self):
        intents = expand_taxonomy(ROOT / "config/intents/taxonomy.yaml", limit=500)
        self.assertEqual(len(intents), 500)
        self.assertEqual(len({i["id"] for i in intents}), 500)
        self.assertEqual(intents[0]["priority"], 100.0)
        self.assertEqual(intents[0]["prompts"], ["What is the best AI tool for creating video ads?"])
        self.assertTrue(all(a["priority"] >= b["priority"] for a, b in zip(intents, intents[1:])))
        prompts = " ".join(p for i in intents for p in i["prompts"])
        self.assertNotIn("music videos for Amazon", prompts)

    def test_howto_template_keeps_use_case_cluster(self):
        intents = expand_taxonomy(ROOT / "config/intents/taxonomy.yaml")
        howto = [i for i in intents if i["template"] == "howto"]
        self.assertIn("video-ads", {i["cluster"] for i in howto})


class ReportTests(unittest.TestCase):
    def test_report_files(self):
        target = Brand("Higgsfield", [], ["higgsfield.ai"])
        r = EngineResult("gemini", "m", "video-ads", "p", 0, text="Higgsfield.",
                         citations=[Citation("https://higgsfield.ai/x")], search_queries=["ai video ads"])
        with tempfile.TemporaryDirectory() as d:
            path = write_report([r], target, [], Path(d))
            md = path.read_text(encoding="utf-8")
            self.assertIn("| gemini | 1 | 100%", md)
            self.assertIn("`ai video ads` × 1", md)
            self.assertTrue((Path(d) / "metrics.csv").exists())
            self.assertTrue((Path(d) / "domains.csv").exists())


if __name__ == "__main__":
    unittest.main()
