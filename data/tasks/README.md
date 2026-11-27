# Набор задач / Task set

**RU.** Набор задач, на котором сняты все числа серии ENGRAMS (часть 2).

| файл | что внутри |
|---|---|
| `chunk_000002_tasks_3000.json` | 3000 задач из фрагмента 2 русской Википедии (1 815 018 лемм, токенизатор v3, словарь 100 005). Каждая задача: `id`, `position` (позиция начала контекста в потоке: `context = поток[position : position+30]`, цель — `поток[position+30]`), `context` (30 номеров лемм перед целью), `target` (номер правильной леммы). Первые 500 задач выбраны с seed 42, следующие 2500 дописаны с seed 4242. |
| `top_lemmas_1000.json` | 1000 самых частых лемм по всем 584 фрагментам (1 080 086 644 леммы), без `[UNK]`. Фильтр цели. |

Рабочие 300 задач: из 3000 оставить те, чья цель есть в `top_lemmas_1000.json` (их 2820), и взять первые 300. Это делает `scripts/part02/select_tasks.py`. Номера лемм переводятся в слова словарём `data/tokenizer_v3/lemma2id.json` (часть 4).

Лицензия: CC BY-SA 4.0, данные производны от Википедии.

---

**EN.** The task set on which every number of the ENGRAMS series was measured (part 2).

| file | contents |
|---|---|
| `chunk_000002_tasks_3000.json` | 3000 tasks from fragment 2 of the Russian Wikipedia (1,815,018 lemmas, tokenizer v3, vocabulary 100,005). Each task: `id`, `position` (start of the context in the stream: `context = stream[position : position+30]`, the target is `stream[position+30]`), `context` (30 lemma ids before the target), `target` (correct lemma id). The first 500 tasks were drawn with seed 42, the next 2500 added with seed 4242. |
| `top_lemmas_1000.json` | The 1000 most frequent lemmas over all 584 fragments (1,080,086,644 lemmas), excluding `[UNK]`. The target filter. |

The working 300 tasks: keep the tasks whose target is in `top_lemmas_1000.json` (2820 of them) and take the first 300. `scripts/part02/select_tasks.py` does this. Lemma ids map to words via `data/tokenizer_v3/lemma2id.json` (part 4).

License: CC BY-SA 4.0, derived from Wikipedia.
