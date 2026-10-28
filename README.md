# Higgsfield AEO

Как сделать Higgsfield рекомендацией №1 в ответах AI-ассистентов на вопрос *"What is the best AI tool for creating video ads?"*. Сначала Gemini и поверхности Google, затем ChatGPT, Perplexity, Claude, Copilot и 500 интентов.

Репозиторий содержит три вещи. Исследование объясняет, как answer engines собирают контекст и почему Higgsfield сейчас проигрывает. Конфигурация и roadmap описывают, что и в каком порядке менять. Трекер видимости измеряет результат.

> **EN summary.** AEO case for Higgsfield. Research on how Gemini / AI Overviews / AI Mode pick sources, a diagnosis of why Higgsfield is not recommended for "best AI tool for video ads", a Gemini-first campaign config and roadmap that extends to ChatGPT, Perplexity, Claude and Copilot, and a multi-engine visibility tracker (`python -m aeo`) that scales to 500 intents.

## Главное

1. **Ответ строится из консенсуса, а не из топ-10.** Gemini разбивает вопрос на подзапросы (query fan-out) и собирает пул страниц. Только 37.9% цитат AI Overviews взяты из органического топ-10 (Ahrefs, 03.2026), 31% из-за пределов топ-100.
2. **Интент принадлежит Creatify, HeyGen и Arcads.** Мы разобрали 29 рейтингов по ad- и UGC-запросам. Creatify есть в 27 из них, HeyGen в 24, Arcads в 23. Higgsfield есть в 8, в основном на местах #6–#9, и описан как «cinematic», а не как рекламный инструмент.
3. **Продукт есть, машины его не видят.** Marketing Studio делает рекламу по ссылке на товар примерно за 2 минуты: 9 форматов, 40+ аватаров. При этом главная и schema не говорят о рекламе, OG-тексты до сих пор про «camera control», цены не отдаются в HTML, сигнал размазан по 9+ лендингам.
4. **Доверие тормозит рекомендацию.** В феврале 2026 о бренде писали Forbes и The Register, Википедия удалена, на G2 79 отзывов против 1 511 у Creatify, конкуренты пишут свои «Higgsfield review».
5. **Три ставки на $5 000:** (1) единая сущность и хаб `/ai-video-ads`, $0; (2) открытый бенчмарк «120 роликов, 6 инструментов» и аутрич в рейтинги, $1 850; (3) YouTube-тесты и отзывы на G2, $2 250.

## Карта репозитория

| Путь | Что внутри |
|---|---|
| [`ROADMAP.md`](ROADMAP.md) | фазы, gates, бюджет, перенос на другие движки и 500 интентов |
| [`config/campaigns/gemini.yaml`](config/campaigns/gemini.yaml) | **конфигурация Gemini-кампании**: поверхности, fan-out цели, хабы, техника, эксперименты, KPI |
| [`config/campaigns/shared.yaml`](config/campaigns/shared.yaml) | общая для всех движков сущность, активы и запрещённые тактики |
| `config/campaigns/{chatgpt,perplexity,claude,copilot}.yaml` | что добавить к Gemini-кампании для каждого движка |
| [`config/brand_facts.yaml`](config/brand_facts.yaml) | единый источник фактов о продукте (заполняет product marketing) |
| [`config/intents/`](config/intents/) | пилотная панель, таксономия и сгенерированные 500 интентов |
| [`config/engines.yaml`](config/engines.yaml) | модели и ключи для трекера |
| [`site/`](site/) | готовые артефакты для сайта: robots.txt, JSON-LD, спецификация хаба, раздел llms.txt |
| [`docs/research/01-how-gemini-gets-context.md`](docs/research/01-how-gemini-gets-context.md) | как AI Overviews, AI Mode, Gemini app и Gemini API выбирают источники |
| [`docs/research/02-higgsfield-promotion.md`](docs/research/02-higgsfield-promotion.md) | ландшафт, аудит Higgsfield, диагноз, 10 возможностей, бюджет |
| [`docs/research/03-scaling.md`](docs/research/03-scaling.md) | карта движков, API для мониторинга, 500 интентов, архитектура |
| [`docs/presentation.md`](docs/presentation.md) | текст 5 слайдов |
| [`docs/speaker-guide.md`](docs/speaker-guide.md) | **разбор каждого слайда**: что говорить, откуда каждая цифра, как составлялся ресёрч, вопросы жюри, глоссарий |
| [`docs/tracker.md`](docs/tracker.md) | как работает трекер и что значат метрики |
| `aeo/`, `tests/` | трекер видимости и тесты |

## Трекер за минуту

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...        # ключ с включённым биллингом: grounding на Gemini 3+ только на платном тарифе
python -m aeo engines
python -m aeo run --engines gemini,gemini-memory --samples 5
python -m aeo expand config/intents/taxonomy.yaml --limit 500 --out config/intents/generated.yaml
python -m unittest discover -s tests -t .
```

Трекер опрашивает Gemini (с grounding через Google Search и без него), ChatGPT, Perplexity и Claude через официальные API. Он считает mention rate с 95% доверительным интервалом, top-1, citation share и share of voice. Отдельно он выводит домены, которые цитируются по многим интентам, и поисковые запросы, которые Gemini сам отправил в Google. Подробности в [`docs/tracker.md`](docs/tracker.md).

## Оговорки

- Ответы AI Overviews и AI Mode из нашей среды напрямую не наблюдались. Ландшафт построен по пулу страниц, из которого они собираются. Первый шаг roadmap — baseline-замер.
- Ответы через API совпадают с интерфейсом по брендам лишь на 15–32% (Surfer, 2026). API-метрики — это тренд, а не «то, что видит пользователь». Раз в месяц нужна сверка с реальным UI.
- Gemini API Terms запрещают автоматический сбор и анализ ссылок из grounding. Перед масштабированием трекера нужна юридическая проверка; раскрытие редиректов по умолчанию выключено.
- Часть данных (G2, Trustpilot, Reddit) взята из поисковых сниппетов: эти площадки блокируют прямые запросы. В отчётах такие места помечены.
