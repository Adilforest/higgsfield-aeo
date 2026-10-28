# Откуда генеративные поверхности Google берут контекст и как выбирают источники

Дата исследования: 28.10.2026. Целевой интент: «What is the best AI tool for creating video ads?».

Обозначения: **[Факт]** проверено по первоисточнику или исследованию со ссылкой; **[Вывод]** наша интерпретация; уверенность указана там, где данных мало.

---

## TL;DR

- **Гипотеза «источники AIO = первые 5–10 результатов» для 2026 года неверна.** В июле 2025 года 76% цитат AI Overviews приходились на топ-10 ([Ahrefs](https://ahrefs.com/blog/search-rankings-ai-citations)). В марте 2026 года их стало 38%, причём 31% цитат взяты со страниц за пределами топ-100 ([Ahrefs](https://ahrefs.com/blog/ai-overview-citations-top-10/)). Причина в query fan-out и переводе AIO на Gemini 3 в январе 2026 года.
- **Лучший предиктор цитирования: ранжироваться и по основному запросу, и по fan-out подзапросам.** 51,2% цитируемых страниц ранжируются по основному запросу и хотя бы по одному fan-out, только 19,6% лишь по основному ([Surfer](https://surfer.ai/blog/query-fan-out/)).
- **AIO и AI Mode (с мая 2026 года это одна связка) цитируют разное.** Пересечение цитат всего 13,7%, хотя смысл ответов совпадает примерно в 86% случаев. AI Mode называет в среднем 3,3 сущности на ответ, AIO 1,3 ([Ahrefs](https://ahrefs.com/blog/ai-overviews-vs-ai-mode/)).
- **Для коммерческих запросов вида «best X tool» пул источников заполняют вендорские листиклы** (51% топ-3 цитат в SaaS-запросах), за ними идут Reddit и YouTube. G2 и Capterra почти не видны ([AUQ](https://auq.io/blog/ai-overview-citations-what-appears-for-best-product-searches-original-data/), [SE Ranking](https://seranking.com/blog/review-platforms-in-ai-overviews/)).
- **По нашему интенту Higgsfield почти не попадает в retrieval-пул.** Из 32 сторонних страниц, найденных по 7 вариантам запроса, Higgsfield упоминают только 7, а первым его ставит одна. Сторонние авторы описывают его как «cinematic / model aggregator», а не как инструмент для рекламы. Пул держат HeyGen и Cometly, у каждого по 6 листиклов.
- **Google-Extended не влияет на AIO и AI Mode.** Он управляет обучением Gemini и grounding в Gemini app и Vertex. Для Search есть свои рычаги: Googlebot, noindex, nosnippet, max-snippet, data-nosnippet и новый переключатель «Search generative AI» в Search Console (с 31.08.2026 доступен всем сайтам).
- **Gemini API:** рекомендуемая модель `gemini-3.8-flash`. Grounding на Gemini 3+ тарифицируется за каждый поисковый запрос: 5 000 бесплатно в месяц, затем $14 за 1 000. URI источников в `groundingChunks` приходят как редиректы `vertexaisearch.cloud.google.com/grounding-api-redirect/...`. Terms запрещают «analyze» и автоматический сбор Links, и это прямой юридический риск для мониторингового инструмента.

---

## 1. AI Overviews (Google Search)

**Как формируется контекст** [Факт]. Google официально описывает AIO как RAG поверх core ranking systems: «relying on our core Search ranking systems to retrieve relevant, up-to-date web pages from our Search index» ([Google, AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)). AIO может использовать query fan-out, то есть «issuing multiple related searches across subtopics and data sources». Во время генерации модели находят дополнительные страницы-подтверждения ([AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)).

**Условия попадания** [Факт]. Страница должна быть проиндексирована и иметь право показываться со сниппетом. С 2026 года к этому добавилось ещё одно условие: сайт должен быть включён в «Search generative AI features» в Search Console. По умолчанию все сайты включены ([guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), [Search Console Help](https://support.google.com/webmasters/answer/16908024?hl=en)).

**Модель и охват** [Факт]. С января 2026 года AIO работают на Gemini 3 ([SEJ](https://www.searchenginejournal.com/google-ai-overview-citations-from-top-ranking-pages-drop-sharply/568637/)). На I/O 2026 AIO и AI Mode объединили в единый поток «снимок, затем follow-up в AI Mode», у AIO больше 2,5 млрд пользователей в месяц ([Google I/O 2026](https://blog.google/innovation-and-ai/technology/ai/google-io-2026-all-our-announcements/), [Keywords Everywhere](https://keywordseverywhere.com/news/google-io-2026-search/)). По данным BrightEdge, в феврале 2026 года AIO показывались примерно на 48% отслеживаемых запросов ([BrightEdge](https://help.brightedge.com/resources/weekly-ai-search-insights/ai-overviews-one-year-presence-size-citing)).

**Какие домены цитируются** [Факт]. По доле среди топ-50 доменов: YouTube 22,9%, Reddit 18,5%, Facebook 10,1%, google.com 8,8%, Instagram 5,6%, Quora 4,7%, Wikipedia 4,0%, TikTok 3,3% ([Ahrefs, сентябрь 2026](https://ahrefs.com/blog/most-cited-domains-ai-overviews/)). Доля YouTube среди всех цитат AIO 5,6%, рост за полгода 34% ([Ahrefs](https://ahrefs.com/blog/ai-overview-citations-top-10/)).

## 2. AI Mode (query fan-out, Deep Search)

**Механика** [Факт]. «AI Mode uses our query fan-out technique, breaking down your question into subtopics and issuing a multitude of queries simultaneously». Deep Search «can issue hundreds of searches» ([Google, май 2025](https://blog.google/products/search/google-search-ai-mode-update/)). Помимо веба подключаются Shopping Graph, Finance и другие вертикальные данные ([Robby Stein, SEJ](https://www.searchenginejournal.com/query-fan-out-technique-in-ai-mode-new-details-from-google/)). С мая 2026 года модель по умолчанию Gemini 3.5 Flash, у AI Mode больше 1 млрд пользователей в месяц, Personal Intelligence доступен почти в 200 странах ([Google I/O 2026](https://blog.google/innovation-and-ai/technology/ai/google-io-2026-all-our-announcements/)).

**Патенты** [Факт о патентах, Вывод о продакшене]. iPullRank разобрал патенты, которые предположительно лежат в основе AI Mode: «Search with stateful chat» (US20240289407A1), «Query response from a custom corpus» (US20240362093A1), pairwise ranking prompting (US20250124067A1), user embeddings (WO2025102041A1). По этой схеме система собирает под пользователя временный корпус из fan-out выдач, сравнивает passages попарно и подбирает цитату к каждому утверждению независимо от ранга документа ([iPullRank](https://ipullrank.com/how-ai-mode-works)). Патент не доказывает, что механизм работает в продакшене. Уверенность средняя.

**Цитаты против органики** [Факт]. На 1 000 транзакционных запросов только 19% цитат AI Mode взяты из топ-20 органики. Пересечение с топ-10 есть лишь у 28% запросов. Страница на позиции 1 цитируется в 25% случаев, на позиции 2 в 21%, на позиции 3 в 16% ([seoClarity, окт. 2025](https://www.seoclarity.net/ai-mode-rankings-overlap)).

**Отличия от AIO** [Факт]. Совпадает 13,7% цитат (16,3% для топ-3). Quora в AI Mode цитируется в 3,5 раза чаще, Wikipedia на 10% чаще. Если бренд есть в AIO, с вероятностью 61% он будет и в AI Mode, но в окружении большего числа конкурентов ([Ahrefs](https://ahrefs.com/blog/ai-overviews-vs-ai-mode/)).

## 3. Gemini app (gemini.google.com)

- **Решение о поиске** [Факт для API, Вывод для app]. Модель сама определяет, «if a Google Search can improve the answer», и при необходимости генерирует один или несколько запросов ([Gemini API docs](https://ai.google.dev/gemini-api/docs/google-search)). Скорее всего, app работает по той же схеме, но с собственным системным промптом и персонализацией (история чатов, Personal Intelligence). Уверенность средняя.
- **Показ источников** [Факт]. «When sources are available, you can find the Sources button at the bottom of the response or in-line». «Not all responses include related links or sources» ([Gemini Help](https://support.google.com/gemini/answer/14143489?hl=en)). Если ответ собран из параметрической памяти, ссылок под ним нет.
- **Модели** [Факт]. Gemini 3 Flash стал моделью по умолчанию 17.12.2025, Gemini 3.6 Flash появился в выборе 21.07.2026, Gemini 4 Argon стал доступен подписчикам Pro и Ultra 13.10.2026 ([release notes](https://gemini.google/release-notes/)).
- **Google-Extended** [Факт]. Этот токен управляет «grounding ... in Gemini Apps». Если Google-Extended закрыт, страница не используется для grounding в app ([Google crawlers](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers)).

## 4. Gemini API: Grounding with Google Search

Модель решает, искать ли, сама формирует `webSearchQueries` и возвращает chunks и supports. Полный справочник в разделе 9. Вот факты, важные для интерпретации:

- **Fan-out нестабилен** [Факт]. На 1 600 прогонах с grounding только около 27% fan-out запросов повторялись от прогона к прогону, 66% встретились один раз. При этом 84% fan-out запросов делили хотя бы один URL из топ-20 с исходным запросом ([Surfer](https://surfer.ai/blog/query-fan-out/)). По данным Seer Interactive, которые приводит Surfer, Gemini 3 выполняет в среднем 10,7 fan-out запроса на промпт против 6,01 у Gemini 2.5 (диапазон от 3 до 28).
- **Google-Extended** [Факт для Vertex, Вывод для Developer API]. «Grounding with Google Search on [Vertex] does not use web pages ... that have disallowed Google-Extended» ([Vertex docs](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-google-search)). Для Gemini Developer API такой фразы в документации нет. Логично предположить то же поведение, уверенность средняя.

## 5. Сравнение поверхностей

| | AI Overviews | AI Mode | Gemini app | Gemini API grounding |
|---|---|---|---|---|
| Когда ищет | всегда RAG, показ только когда «additive» | всегда, fan-out, Deep Search до сотен запросов | решает модель | решает модель |
| Модель (окт. 2026) | Gemini 3 (с янв. 2026) | Gemini 3.5 Flash по умолчанию | 3 Flash, 3.6 Flash, 4 Argon | выбор разработчика |
| Цитат на ответ | мало, 1,3 сущности | больше, 3,3 сущности | только если был поиск | `groundingChunks` |
| Персонализация | частично | да (история, Personal Intelligence) | да | нет |
| Google-Extended | не влияет | не влияет | влияет на grounding | влияет (Vertex точно) |
| Отключение в Search Console | да | да | нет | нет |

---

## 6. Проверка гипотезы «топ-5–10 ссылок»

| Исследование | Дата | Выборка | Доля цитат из топ-10 |
|---|---|---|---|
| [Ahrefs](https://ahrefs.com/blog/search-rankings-ai-citations) | июл. 2025 | 1,9 млн цитат, топ-3 цитаты | **76,1%** (медианная позиция 3) |
| [Ahrefs](https://ahrefs.com/blog/ai-overview-citations-top-10/) | мар. 2026 | 863 тыс. SERP, 4 млн URL | **37,9%**; 31,2% из позиций 11–100; 31,0% вне топ-100 |
| [BrightEdge](https://help.brightedge.com/resources/weekly-ai-search-insights/ai-overviews-one-year-presence-size-citing) | фев. 2026 | 9 вертикалей | **~17%**, стабильно в течение года |
| [Surfer](https://surfer.ai/blog/query-fan-out/) | окт. 2026 | 10 тыс. ключей, 173 902 URL | 67,8% цитат **не** из топ-10 |
| [seoClarity](https://www.seoclarity.net/ai-mode-rankings-overlap) (AI Mode) | окт. 2025 | 1 000 запросов | 19% цитат из топ-20 |

**Вердикт** [Вывод, уверенность высокая]. В 2026 году гипотеза не подтверждается. Числа сильно расходятся (17–38%), потому что методики разные: одни берут все цитаты, другие только топ-3, одни учитывают SERP-фичи, другие только синие ссылки. Ahrefs также предупреждает, что его парсинг изменился. Направление при этом одно у всех. Позиция №1 по-прежнему даёт самый высокий шанс на цитату (25% в AI Mode), но гарантии не даёт.

**Как fan-out меняет набор страниц.** Цитаты собираются из объединения выдач по подзапросам, поэтому страница, которая ранжируется по нескольким соседним формулировкам, выигрывает у страницы с одним хорошим ранжированием. В исследовании Surfer страниц, которые ранжировались только по fan-out запросам, цитировали чаще (29,2%), чем страницы только по основному запросу (19,6%). Ahrefs объясняет падение доли топ-10 так: «AI Overviews are relying less on the direct search results and more on the sources showing up in fan out query SERPs».

---

## 7. Типы источников для коммерческих запросов «best X tool»

| Тип | Данные | Что это значит для нашего интента |
|---|---|---|
| Вендорские листиклы («Best … 2026») | 51% топ-3 цитат AIO в 100 SaaS-запросах ([AUQ, май 2026](https://auq.io/blog/ai-overview-citations-what-appears-for-best-product-searches-original-data/)); 70,8% цитат в B2B SaaS это подборки «best/top», больше половины с «2026» в title ([Overthink, июл. 2026](https://overthinkgroup.com/b2b-ai-citation-stats-2026-q2/)) | главный слой; сейчас его держат HeyGen и Cometly |
| YouTube | 22,9% доли топ-50 в AIO; 7,4% цитат AIO в B2B SaaS; YouTube-упоминания бренда сильнее всего коррелируют с AI-видимостью (r≈0,737) ([Ahrefs](https://ahrefs.com/blog/ai-brand-visibility-correlations/)) | для видеоинструментов, скорее всего, ещё важнее [Вывод] |
| Reddit, форумы | 18,5% доли топ-50; в топ-3 цитат у 38% SaaS-запросов (AUQ); в нишевом B2B всего 1,4% (Overthink) | разброс большой, уверенность средняя |
| Quora | 4,7% в AIO; в AI Mode в 3,5 раза больше | канал для AI Mode |
| G2, Capterra и др. | review-платформы есть в 17,1% AIO по «best/top» против 49% по «… reviews» ([SE Ranking](https://seranking.com/blog/review-platforms-in-ai-overviews/)); 3% топ-3 цитат (AUQ) | важны для запросов «Higgsfield reviews» и «X vs Y», а не для «best» |
| Wikipedia | 4,0% в AIO, в AI Mode на 10% больше | entity-сигнал |
| Сайты брендов | в поверхностях Google около 75% топ-доменов это вендоры, в ChatGPT и Perplexity около 25% (Overthink) | собственные страницы имеют шанс, если ранжируются по fan-out |

---

## 8. Сигналы отбора

- **Freshness** [Факт]. По 7 AI-платформам цитаты в среднем на 25,7% свежее органики. Но именно AIO почти не отдают предпочтения свежему контенту: 1 432 дня против 1 416 у органики. У Gemini 1 118 дней ([Ahrefs](https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/)). [Вывод] Год в title для запросов «best … 2026» работает скорее через CTR и ранжирование, чем как отдельный сигнал AI.
- **Structured data** [Факт]. «Structured data isn't required ... there's no special schema.org markup» ([guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)). Разметка полезна для rich results и должна совпадать с видимым текстом ([Google, май 2025](https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search)). Отдельного буста в AI она не даёт.
- **E-E-A-T / качество** [Факт]. Функции «rooted in our core Search ranking and quality systems». Google просит «non-commodity content», то есть first-hand review вместо пересказа. Создавать страницы под каждый fan-out подзапрос значит нарушать политику scaled content abuse (guide).
- **Passage-level** [Факт и Вывод]. Google: «no requirement to break your content into tiny pieces ... systems are able to understand the nuance of multiple topics on a page and show the relevant piece» (guide; [Danny Sullivan, янв. 2026](https://ppc.land/google-warns-against-breaking-content-into-chunks-for-ai/)). Извлечение идёт на уровне passages (патент pairwise ranking), но дробить контент искусственно не нужно.
- **Entity и упоминания** [Факт]. Корреляции с AI-видимостью на 75 тыс. брендов: YouTube-упоминания 0,737, branded web mentions 0,656, branded anchors 0,527, DR 0,326, backlinks около 0,21, объём контента около 0,19 ([Ahrefs, дек. 2025](https://ahrefs.com/blog/ai-brand-visibility-correlations/)). Google предупреждает: «seeking inauthentic "mentions" ... isn't as helpful», потому что спам-системы фильтруют такие упоминания (guide).

### Параметрическая память против retrieval

[Факт] В API и app модель сама решает, нужен ли поиск. В старом `google_search_retrieval` это решал `MODE_DYNAMIC` с `dynamicThreshold` ([API reference](https://ai.google.dev/api/generate-content)). Без поиска `groundingMetadata` пуст, и бренд называется из памяти без ссылки. В AIO и AI Mode retrieval есть всегда.

[Вывод, уверенность средняя] Бренд называется без цитаты в трёх ситуациях:
1. Поиска не было вовсе (app или API).
2. Бренд упомянут внутри процитированного листикла, и ссылка ведёт на листикл, а не на сайт бренда.
3. Модель «достраивает» список знакомыми сущностями.

На это влияют частота и контекст упоминаний в обучающих данных и в индексе, а также устойчивость связки «бренд ↔ категория». Сейчас веб связывает Higgsfield с «cinematic video», а не с «video ads», так что параметрическая память, скорее всего, тянет его в другой ответ. Это можно проверить: прогнать одни и те же промпты с `google_search` и без него и сравнить `mention_rate`.

---

## 9. Контроли

| Контроль | AIO / AI Mode | Gemini app | API / Vertex grounding | Обучение |
|---|---|---|---|---|
| `robots.txt` для Googlebot | блок = исключение из Search | косвенно | косвенно | нет |
| `noindex` | исключает | | | |
| `nosnippet` | не показывает и **не использует как input** | | | |
| `max-snippet:[n]` | ограничивает объём input | | | |
| `data-nosnippet` | исключает фрагмент из сниппета | | | |
| Google-Extended | **не влияет** («does not impact a site's inclusion in Google Search») | grounding | grounding (Vertex точно) | Gemini |
| Search Console → Search generative AI | Include/Exclude, без влияния на ранжирование | нет | нет | нет |

Источники: [robots meta tag](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) (обновлено 24.03.2026), [crawlers](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers), [Search Console Help](https://support.google.com/webmasters/answer/16908024?hl=en), [CMA и опт-аут](https://siliconangle.com/2026/06/03/uk-orders-google-provide-ai-overviews-opt-option-publishers/).

**Состояние higgsfield.ai** [Факт, проверено 28.10.2026]. В `robots.txt` разрешены `*` и явно `Google-Extended`. Локали `/es/ /ja/ /ko/ /de/ /zh/` закрыты, кроме allowlist-страниц. На блог-листикле нет meta robots с ограничениями, есть JSON-LD (BlogPosting, FAQPage, Organization). Технических блокеров для AI-поверхностей нет.

---

## 10. Что, скорее всего, произойдёт по запросу «best AI tool for creating video ads»

**Метод.** Мы выполнили 7 вариантов запроса через сторонний поисковый индекс (это не Google SERP, поэтому результат только прокси retrieval-пула), скачали 37 страниц из выдачи и поискали в HTML упоминания «Higgsfield».

| Запрос | Что в выдаче | Higgsfield |
|---|---|---|
| best AI tool for creating video ads | cometly ×5, venngage, heygen ×2, klap, adenslab | ни одна из 8 скачанных страниц его не упоминает |
| best AI video ad generator 2026 | **higgsfield.ai/blog/best-ai-ad-generators**, pixverse, heygen, segwise, cometly ×2, techbullion, ngram | свой блог в выдаче; упоминают pixverse, segwise, techbullion (там №1) |
| AI tool for UGC video ads | invideo, creatify, cometly, zeely, arcads ×2, ltx, nextify, ugcvideo | нет |
| AI video ads for ecommerce | heygen, cometly, zeely, shhots ×2, adsturbo, rewarx, vivideo | shhots (позиции №9 и №12) |
| сравнение Arcads/Creatify/HeyGen/Higgsfield | higgsfield ×2, **heygen.com/blog/higgsfield-alternatives**, heygen ×2, moda, reloop, adlibrary, alici | moda; HeyGen перехватывает брендовый спрос |
| G2/Zapier-вариант | heygen, g2 ×4, openart, cliploft, rankite | нет |
| Higgsfield AI video ads review | cybernews, unite.ai, promer, v4v, g2 и др. | «no purpose-built ad workflows» ([v4v](https://v4v.ai/blog/higgsfield-ai-review-2026/)) |

**Наблюдения** [Факт по нашей выборке]:
- Из 32 сторонних страниц Higgsfield упоминают 7 (около 22%), первым его ставит только TechBullion.
- Сторонние авторы называют его «cinematic short-form», «model aggregator with camera presets», «stylized camera-motion». Лидеры консенсуса в этих подборках: HeyGen, Creatify, Arcads, AdStellar, InVideo, Synthesia, Predis, AdCreative.ai.

**Прогноз** [Вывод, уверенность средняя, проверить в UI]. Ответ AIO или AI Mode на целевой запрос, скорее всего, первыми назовёт HeyGen, Creatify и Arcads. Higgsfield если и появится, то в нише «cinematic». Fan-out, вероятно, пойдёт в «AI UGC ad generator», «AI video ads ecommerce», «HeyGen vs Creatify», «AI ads for TikTok/Meta», то есть туда, где Higgsfield сейчас почти не виден.

---

## 11. Справочник по Gemini API (проверено 28.10.2026)

**Модели** ([models](https://ai.google.dev/gemini-api/docs/models), [grounding](https://ai.google.dev/gemini-api/docs/google-search)):
- `gemini-3.8-flash`: stable, рекомендуется для мониторинга.
- `gemini-3.5-flash-lite`: дешёвая.
- `gemini-4-argon`: флагман, на free tier недоступен.
- Также поддерживают grounding: `gemini-3.6-flash`, `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-2.5-pro/flash/flash-lite`, `gemini-2.0-flash`.
- Доступ к моделям 2.5 ограничен «users who have actively used them in the past». В `config/engines.yaml` сейчас стоит `gemini-2.5-flash`, его нужно заменить.

**generateContent (поддерживается полностью):**
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" -H "Content-Type: application/json" \
  -d '{"contents":[{"role":"user","parts":[{"text":"What is the best AI tool for creating video ads?"}]}],
       "tools":[{"google_search":{}}]}'
```
Опции `googleSearch`: `timeRangeFilter {startTime,endTime}` и `searchTypes`. `exclude_domains` есть только в Vertex.

**Ответ** `candidates[0].groundingMetadata` ([API reference](https://ai.google.dev/api/generate-content)):
- `webSearchQueries[]`: фактически выполненные fan-out запросы.
- `searchEntryPoint.renderedContent` (HTML-виджет) и `sdkBlob`.
- `groundingChunks[].web.uri` / `.title`. В `title` обычно домен. `uri` имеет вид `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`, поля с исходным URL нет ([migration guide](https://ai.google.dev/gemini-api/docs/migrate-to-interactions), [форум](https://discuss.ai.google.dev/t/feature-request-provide-actual-source-urls-in-grounding-metadata/107352)).
- `groundingSupports[]`: `segment{partIndex,startIndex,endIndex,text}`, `groundingChunkIndices[]`, `confidenceScores[]`.
- Также `imageSearchQueries[]` и `retrievalMetadata`.

**Interactions API (рекомендуется для новых проектов, новые функции будут выходить там):**
- Запрос: `POST /v1beta/interactions`, тело `{"model":"gemini-3.8-flash","input":"...","tools":[{"type":"google_search"}]}`.
- В `steps[]` приходят `google_search_call.arguments.queries`, `google_search_result.result[].search_suggestions` и `model_output.content[].annotations[]` с типом `url_citation {url,title,start_index,end_index}`.
- В примере документации URL прямые. Приходят ли редиректы в реальных ответах, нужно проверить.
- По умолчанию `store=true`, для мониторинга лучше ставить `store=false`.

**Цены** ([pricing](https://ai.google.dev/gemini-api/docs/pricing)):
- Gemini 3+: платится каждый выполненный поисковый запрос. 5 000 бесплатно в месяц на все модели 3+, затем $14 за 1 000. На free tier grounding для 3.x недоступен.
- 2.5 Flash: 500 RPD бесплатно, на paid tier 1 500 RPD бесплатно, затем $35 за 1 000 промптов.
- Токены `gemini-3.8-flash`: $0,75 / $3,75 за 1M до 31.12.2026, с 01.01.2027 $1,50 / $7,50.
- Оценка [Вывод]: 1 000 промптов × 10,7 запроса ≈ 10 700 запросов, то есть около $80 в месяц за поиск.

**Terms** ([Gemini API Terms](https://ai.google.dev/gemini-api/terms#grounding-with-google-search)):
- Grounded Results нужно показывать «with the associated Search Suggestion(s) to the end user who submitted the prompt».
- Запрещено «cache, frame, syndicate, resell, analyze, train on», а также «using programmatic or automated means to collect Links». Нельзя отслеживать клики по ссылкам и смешивать результат с другим контентом.
- Текст можно хранить до 2 лет, но только чтобы оценивать и улучшать его показ.
- В Vertex есть лимит 1 млн запросов в сутки, Search Suggestions обязательно показывать в продакшене.
- [Вывод] Логирование доменов, резолв редиректов и агрегированная аналитика противоречат букве Terms. Перед масштабированием трекера нужна юридическая проверка. Альтернативы: SERP-вендор или ручные проверки UI.

---

## 12. Что это значит для Higgsfield

1. **Захватить слой листиклов** (главный рычаг, уверенность высокая). Нужно попасть в топ-3 сторонних подборок, которые уже ранжируются по основному запросу и fan-out: cometly.com, venngage, invideo, cliploft, reloop, G2 Learn, openart. Аргументы для редакций: реальные тесты, цена за креатив, кейсы. Платные размещения нужно помечать, имитация независимости рискованна.
2. **Сменить ассоциацию «cinematic» на «video ads».** Везде использовать одну формулировку категории: «AI video ad generator» на главной, в `/ai-ad-generator`, `/ugc`, `/marketing-studio`, в профиле G2 и в описаниях YouTube. Закрыть или явно опровергнуть претензию «no purpose-built ad workflows», показав Ad Multiplier, link-to-ads и интеграции, если они есть.
3. **Собственные страницы под fan-out подинтенты** (UGC ads, ecommerce, TikTok/Meta ads, ad variations, URL-to-ad, «Higgsfield vs HeyGen/Creatify/Arcads»). Каждая должна быть с first-hand данными. Перед этим проверить около 1 050 programmatic-страниц `/marketing-studio/preset/*` на thin content: риск scaled content abuse [Вывод, уверенность средняя].
4. **YouTube в первую очередь.** Это самый цитируемый домен AIO и самая сильная корреляция с AI-видимостью. Нужны обзоры и туториалы «best AI tool for video ads» от креаторов и собственный канал с названиями роликов под fan-out запросы.
5. **Reddit и Quora (последняя особенно для AI Mode):** только аутентичное участие. Google прямо пишет, что неаутентичные упоминания фильтруются.
6. **Отзывы на G2/Capterra** с явным упоминанием сценария «video ads». Это работает на запросы «Higgsfield reviews» и «X vs Y», а не на «best».
7. **Техника:** сохранить доступ для Googlebot и Google-Extended, не ставить nosnippet и max-snippet, проверить в Search Console, что выбран Include. Обновлять листиклы с видимой датой и годом в title. Мониторить через Generative AI performance report ([Google, июн. 2026](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)).
8. **Entity:** разметка Organization с `sameAs`, согласованные данные в Wikidata. Wikipedia только при наличии независимых источников, у AI Mode к ней повышенный вес.
9. **Измерения:** перевести трекер на `gemini-3.8-flash`, сравнивать прогоны с поиском и без, раз в неделю проверять UI вручную и решить вопрос с Terms.

---

## Источники

- Google: [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) · [AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) · [Succeeding in AI search](https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search) · [Robots meta tag](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) · [Google crawlers / Google-Extended](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) · [Search generative AI control](https://support.google.com/webmasters/answer/16908024?hl=en) · [Gen AI performance reports](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports) · [AI Mode update, май 2025](https://blog.google/products/search/google-search-ai-mode-update/) · [I/O 2026](https://blog.google/innovation-and-ai/technology/ai/google-io-2026-all-our-announcements/) · [Gemini Help: sources](https://support.google.com/gemini/answer/14143489?hl=en) · [Gemini release notes](https://gemini.google/release-notes/)
- Gemini API: [Grounding](https://ai.google.dev/gemini-api/docs/google-search) · [Models](https://ai.google.dev/gemini-api/docs/models) · [Pricing](https://ai.google.dev/gemini-api/docs/pricing) · [API reference](https://ai.google.dev/api/generate-content) · [Migrate to Interactions](https://ai.google.dev/gemini-api/docs/migrate-to-interactions) · [Terms](https://ai.google.dev/gemini-api/terms) · [Vertex grounding](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-google-search) · [Форум: redirect URIs](https://discuss.ai.google.dev/t/feature-request-provide-actual-source-urls-in-grounding-metadata/107352)
- Исследования: [Ahrefs 76%](https://ahrefs.com/blog/search-rankings-ai-citations) · [Ahrefs 38%](https://ahrefs.com/blog/ai-overview-citations-top-10/) · [Ahrefs AIO vs AI Mode](https://ahrefs.com/blog/ai-overviews-vs-ai-mode/) · [Ahrefs most-cited domains](https://ahrefs.com/blog/most-cited-domains-ai-overviews/) · [Ahrefs brand correlations](https://ahrefs.com/blog/ai-brand-visibility-correlations/) · [Ahrefs freshness](https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/) · [Surfer fan-out](https://surfer.ai/blog/query-fan-out/) · [seoClarity AI Mode](https://www.seoclarity.net/ai-mode-rankings-overlap) · [BrightEdge](https://help.brightedge.com/resources/weekly-ai-search-insights/ai-overviews-one-year-presence-size-citing) · [SE Ranking review platforms](https://seranking.com/blog/review-platforms-in-ai-overviews/) · [AUQ best-product](https://auq.io/blog/ai-overview-citations-what-appears-for-best-product-searches-original-data/) · [Overthink B2B](https://overthinkgroup.com/b2b-ai-citation-stats-2026-q2/) · [iPullRank AI Mode](https://ipullrank.com/how-ai-mode-works) · [SEJ о 38%](https://www.searchenginejournal.com/google-ai-overview-citations-from-top-ranking-pages-drop-sharply/568637/) · [SEJ fan-out](https://www.searchenginejournal.com/query-fan-out-technique-in-ai-mode-new-details-from-google/) · [PPC Land, chunking](https://ppc.land/google-warns-against-breaking-content-into-chunks-for-ai/) · [SiliconANGLE, CMA](https://siliconangle.com/2026/06/03/uk-orders-google-provide-ai-overviews-opt-option-publishers/) · [Keywords Everywhere I/O](https://keywordseverywhere.com/news/google-io-2026-search/)
- Выдача по интенту: [cometly](https://www.cometly.com/post/best-ai-video-ad-generator) · [heygen](https://www.heygen.com/blog/best-ai-video-generator-for-ads) · [heygen: Higgsfield alternatives](https://www.heygen.com/blog/higgsfield-alternatives) · [higgsfield blog](https://higgsfield.ai/blog/best-ai-ad-generators) · [segwise](https://segwise.ai/blog/best-ai-video-ad-generators-2026) · [techbullion](https://techbullion.com/10-best-ai-video-ad-generators-for-businesses-in-2026/) · [pixverse](https://pixverse.ai/en/blog/best-ai-video-generator-for-ads) · [shhots](https://shhots.ai/blog/best-ai-ad-generator/) · [moda](https://moda.app/blog/best-ai-ad-generators) · [venngage](https://venngage.com/blog/best-ai-ad-generator/) · [invideo](https://invideo.io/blog/best-ai-ugc-tools/) · [v4v review](https://v4v.ai/blog/higgsfield-ai-review-2026/)
