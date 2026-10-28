# Spec: /ai-video-ads hub

One canonical page for the entity "Higgsfield Marketing Studio = AI video ad generator".
Server-rendered, ~2,500 words, visible "Last updated" and a named author.
Values in JSON-LD (`site/jsonld-ai-video-ads.json`) must match the visible text.

1. **H1:** "AI Video Ad Generator: from product link to tested video ads".
   Under it, a 50-word answer-first paragraph: what it is, who it is for, "paste a URL → 9 formats → ready ad in about 2 minutes".
2. **Best for / not best for.** Be honest: multilingual corporate presenters are better served by HeyGen or Synthesia.
3. **Table of the 9 modes:** format, platform (TikTok, Reels, Meta, YouTube), length, avatar yes/no.
4. **Numbers from the benchmark:** time to first ad, cost per ad in credits and $, share of ads that passed QA, blind-panel score.
5. **Prices:** the same server-rendered table as /pricing, plus "what one ad costs".
6. **Comparison table** with Creatify, Arcads, HeyGen, Topview, MakeUGC: links to their public prices and the date checked.
7. **Customer cases** with CTR / CPA / ROAS and named quotes (with permission).
8. **Compliance:** TikTok and Meta AI labels, Content Credentials (C2PA), avatar rights.
9. **FAQ** of 8–10 questions that match the visible text.

The other ad landing pages either 301 to this hub, carry `rel=canonical` to it, or stay as narrow sub-pages (product video, UGC, static ads) that link here. The homepage gets a "Video Ads" block linking to the hub. See `config/campaigns/shared.yaml` → `entity.consolidate`.
