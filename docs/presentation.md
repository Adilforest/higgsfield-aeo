# Presentation: 5 slides

Text version of the deck (5 minutes + 5 minutes Q&A). Numbers and sources are in `docs/research/`.

## 1. Landscape — Making Higgsfield the #1 answer for AI video ads

AI answers are a consensus of listicles, reviews and videos. In the 29 ad and UGC lists that feed them, Creatify, HeyGen and Arcads dominate. Higgsfield appears in 8, mostly at #6–#9, and is described as "cinematic", not as an ad tool.

| Named in 29 ad/UGC lists | |
|---|---|
| Creatify | 27 |
| HeyGen | 24 |
| Arcads | 23 |
| Synthesia | 16 |
| InVideo | 12 |
| Captions | 12 |
| **Higgsfield** | **8** (#1 only on a list that sells top positions) |

## 2. Diagnosis — The product exists. Machines can't see it.

User asks → fan-out into many sub-queries → retrieval pool (listicles, YouTube, G2, Reddit) → Higgsfield signal: 8 of 29 lists, "cinematic" → answer: Creatify, HeyGen, Arcads.

Only 37.9% of AI Overview citations come from the organic top 10. The answer is a consensus of many pages, and Higgsfield is not in it.

1. **Wrong entity:** homepage and schema never say "ads"; OG still says "camera control".
2. **No consensus:** Creatify is in 27 of 29 lists; Higgsfield in 8, mostly #6–#9.
3. **Self-claims only:** own "#1" lists and ~50 geo-subdomain pages, no third-party proof.
4. **Trust drag:** Feb 2026 press, Wikipedia deleted, 79 G2 reviews vs 1,511.

Not the cause: crawling or rendering. All AI bots are allowed and the ad landing pages are server-rendered.

## 3. Opportunities — Ten opportunities to close the gap

| # | What | Why it matters | Impact | Effort |
|---|---|---|---|---|
| 1 | /ai-video-ads hub, merge 9 pages | One entity instead of nine URLs | High | Low |
| 2 | Entity signals: title, schema, OG | Machines stop reading "camera control" | High | Low |
| 3 | Prices in HTML + facts page | Ends conflicting third-party prices | Med–High | Low |
| 4 | Public benchmark: 120 ads, 6 tools | Stats and quotes lift citation 28–41% | High | Med |
| 5 | Outreach to the listicles | Builds the consensus AI answers reuse | High | Med |
| 6 | Honest vs pages: Creatify, Arcads | Wins "X vs Y" fan-out sub-queries | Med–High | Low |
| 7 | YouTube "tested" series + 2 creators | YouTube is the top cited domain in AIO | High | Med |
| 8 | G2 / Capterra review program | 79 reviews vs Creatify's 1,511 | Med | Med |
| 9 | Trust page: what we changed | Less hedging after Feb 2026 press | Med–High | Low–Med |
| 10 | Hygiene: geo subdomain, Wikidata | Removes spam-policy and trust risks | Med | Low–Med |

## 4. Bets — Three bets for the first 8 weeks

1. **One entity: the video ads hub** (weeks 1–2, $0). Merge 9 landing pages into /ai-video-ads; say "video ads" in title, schema, OG and llms.txt; put prices in HTML.
2. **Benchmark + listicle outreach** (weeks 2–8, $1,850). 120 ads, 6 tools, a blind panel of 5 media buyers, raw data public. Pitch it to the lists that feed AI answers.
3. **YouTube tests + G2 reviews** (weeks 3–8, $2,250). 6 "tested" videos, 2 creators with paid-partnership labels, G2 reviews through the official program.

Budget: benchmark $1,500 · PR $350 · YouTube $1,500 · G2 $750 · tracking $400 · reserve $500 = $5,000.

Week-12 target: Higgsfield named in ≥ 60% of answers, top-3 in ≥ 30%, measured weekly.

## 5. Design for scale — 500 intents: measure clusters, act on hubs

Intent registry (500 intents × 3 phrasings) → tiered sampling (top-100 weekly, rest biweekly) → engine runners (4 APIs + AIO via SERP vendor) → metrics with CI (mention, top-1, citation share) → hub backlog (content, PR, reviews, Reddit).

| Breaks | Fix |
|---|---|
| Manual checks: 35k answers per cycle | API runners + monthly UI calibration |
| One prompt: same brand list twice under 1 in 100 | Clusters × paraphrases × samples |
| Page per intent: scaled content risk | Win the few domains cited everywhere |
| Attribution: models, PR and content move at once | Test vs control clusters, diff-in-diff |
