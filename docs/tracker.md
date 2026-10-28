# AEO tracker: как работает и как запускать

Трекер задаёт одни и те же вопросы нескольким answer engines через их официальные API с включённым веб-поиском. Ответы и источники он сохраняет в сыром виде и считает метрики видимости Higgsfield.

## Быстрый старт

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...            # https://aistudio.google.com/apikey, нужен включённый биллинг
python -m aeo engines                # какие движки готовы
python -m aeo run --engines gemini --samples 5          # пилотная панель, ~70 вызовов
python -m aeo run --engines gemini,gemini-memory --samples 5   # с поиском и без: память против retrieval
python -m aeo run --engines gemini --prompts canonical --samples 1 --limit 5   # дешёвый smoke test
python -m aeo report runs/<timestamp>                    # пересобрать отчёт из сырых данных
python -m aeo expand config/intents/taxonomy.yaml --limit 500 --out config/intents/generated.yaml
python -m unittest discover -s tests -t .
```

Результат прогона лежит в `runs/<UTC-timestamp>/`:

| файл | что внутри |
|---|---|
| `results.jsonl` | сырые ответы: текст, цитаты, retrieved-источники, fan-out запросы, ошибки |
| `report.md` | сводка по движкам и интентам, лидерборд брендов, citation hubs, fan-out запросы |
| `metrics.csv` | метрики engine × intent для дашборда |
| `domains.csv` | домены-источники: сколько интентов и ответов их цитируют |

## Движки

| ключ | API | что проксирует | ключ окружения |
|---|---|---|---|
| `gemini` | Gemini API + `google_search` grounding | Gemini app, AI Mode | `GEMINI_API_KEY` |
| `gemini-memory` | тот же Gemini без поиска | параметрическая память модели | `GEMINI_API_KEY` |
| `chatgpt` | OpenAI Responses API + `web_search` | ChatGPT search | `OPENAI_API_KEY` |
| `perplexity` | Perplexity Agent API (`/v1/agent`) | Perplexity | `PERPLEXITY_API_KEY` |
| `claude` | Anthropic Messages API + `web_search` tool | Claude.ai с поиском | `ANTHROPIC_API_KEY` |

Модели и включённые движки задаются в `config/engines.yaml`. Новый движок добавляется так: класс в `aeo/engines/` с методами `build_request()` и `parse()`, затем строка в `ADAPTERS` и фикстура в `tests/fixtures/`.

**Ограничение.** Ответ из API не равен ответу в потребительском интерфейсе: там другой системный промпт, персонализация и иногда другая версия модели. API служит стабильной и воспроизводимой панелью для трендов и экспериментов. Раз в неделю реальный UI (AI Overviews, AI Mode, Gemini app, ChatGPT) проверяется вручную, скриншоты кладутся в `evidence/`.

## Метрики

Считаются для каждой пары engine × intent; n означает число успешных ответов.

| метрика | формула | зачем |
|---|---|---|
| `mention_rate` | ответы, где назван Higgsfield / n, плюс Wilson 95% CI | главный KPI: попадаем ли в ответ вообще |
| `top1_rate` | ответы, где Higgsfield назван первым из брендов / n | цель кейса: рекомендация №1 |
| `avg_rank` | средняя позиция Higgsfield среди названных брендов | динамика между 0 и top-1 |
| `owned_cite_rate` | ответы, цитирующие higgsfield.ai / n | работает ли собственный контент |
| `citation_share` | цитаты higgsfield.ai / все цитаты | доля в источниках |
| `share_of_voice` | упоминания Higgsfield / все упоминания отслеживаемых брендов | позиция против конкурентов |
| citation hubs | домены, ранжированные по числу интентов, где их цитируют | куда инвестировать earned media |
| fan-out queries | поисковые запросы, которые движок реально выполнил | семантика для SEO под retrieval |

Ответы LLM недетерминированы, поэтому каждый промпт прогоняется N раз (по умолчанию 5). При n = 25 на интент 95% доверительный интервал для доли 50% составляет примерно ±19 п.п. Чтобы уверенно увидеть рост на 15 п.п., нужно около 40 ответов в каждом срезе, то есть 8 формулировок × 5 сэмплов.

Позиция бренда определяется по порядку первого упоминания. Это прокси: оно корректно для списков «1. X, 2. Y» и для текстов, где лидер назван первым. Спорные случаи проверяются в `results.jsonl`.

## Почему Gemini даёт больше всех данных

Gemini API возвращает `groundingMetadata.webSearchQueries`, то есть те запросы, которые модель сама отправила в Google (query fan-out). Если агрегировать их по сотням прогонов, получится реальная семантика, по которой нужно ранжироваться, чтобы попасть в retrieval pool Gemini. Отчёт выводит её отдельной секцией.

`groundingChunks` приходят как редиректы `vertexaisearch.cloud.google.com/grounding-api-redirect/...`. Домен трекер берёт из `title` чанка. Порядок цитат восстанавливается по `groundingSupports`, то есть по первому сегменту ответа, который опирается на источник.

Сравнение `gemini` и `gemini-memory` показывает, откуда берётся упоминание. Если Higgsfield появляется только при поиске, работает retrieval. Если бренд не появляется и без поиска, модель не связывает его с категорией «video ads» в собственной памяти.

## Стоимость и условия Gemini API

- Модель `gemini-3.8-flash`. Grounding на моделях Gemini 3+ доступен только на платном тарифе: 5 000 поисковых запросов в месяц бесплатно, затем $14 за 1 000. Один промпт в среднем порождает около 10 поисковых запросов, поэтому пилотная панель (13 формулировок × 5 прогонов) укладывается в бесплатный лимит.
- Gemini API Terms запрещают программно собирать и анализировать Links из grounding и требуют показывать Search Suggestions конечному пользователю. Поэтому раскрытие редиректов выключено (`resolve_redirects: false`). Перед масштабированием API-трекера нужна юридическая проверка. Альтернативы: SERP-вендор (риск ToS несёт вендор) или ручная UI-панель.
