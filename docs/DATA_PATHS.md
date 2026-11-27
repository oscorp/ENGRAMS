# Данные и пути / Data and paths

**RU.** Все скрипты запускаются из корня клона и по умолчанию читают и пишут только папки репозитория. Ни одного пути вне клона в коде нет.

## Порядок запуска

```bash
pip install -r requirements.txt
python -m spacy download ru_core_news_lg     # модель spaCy для частей 3–4 (~500 МБ)
python scripts/smoke_test.py                 # проверка конвейера частей 3–4 на маленьком примере, без интернета
```

Дальше по частям: рисунки — `python docs/figures/make_partNN_figures.py`; набор задач — `python scripts/part02/select_tasks.py`; корпус — `python scripts/fetch_data.py --what corpus` (или собрать из дампа, см. заглушку 2), проверка — `python scripts/part03/check_manifest.py`; потоки — `python scripts/fetch_data.py --what streams` (или собрать: `python scripts/part04/build_streams_v3.py`).

## Где что лежит

| путь | что | откуда берётся | в git |
|---|---|---|---|
| `data/tasks/` | набор из 3000 задач и фильтр цели (часть 2) | в репозитории | да |
| `data/corpus/corpus_manifest_v3.json` | размеры и md5 584 фрагментов (часть 3) | в репозитории | да |
| `data/corpus/chunks_584/` | 584 фрагмента Википедии, 11,4 ГиБ | `scripts/fetch_data.py` (Hugging Face) или `scripts/part03/download_wiki_ru.py` | только `chunk_000002.txt` |
| `data/raw/wiki_dump/` | XML-дамп Википедии | `scripts/part03/download_wiki_ru.py` | нет |
| `data/tokenizer_v3/` | словарь `lemma2id.json` и `lemma_stats.json` (часть 4) | в репозитории | да |
| `data/streams_v3/` | три потока на фрагмент: леммы, морфология, предложения | `scripts/fetch_data.py` или `scripts/part04/build_streams_v3.py` | только фрагмент 2 |
| `data/sample/ruwiki_sample.xml` | маленький пример дампа для `smoke_test.py` | в репозитории | да |
| `data/work/` | всё, что пересобирается заново: словарь, отчёты, проверочные прогоны | скрипты | нет |

## Заглушки: что пока не на месте

Осталась одна.

| № | где | что стоит | на что заменить и как получить |
|---|---|---|---|
| 1 | `scripts/part03/download_wiki_ru.py`, строка 147: `--dump-date` по умолчанию `latest` | скачивается свежий дамп, а не тот, из которого собран корпус (декабрь 2025, правки по 21.12.2025). Корпус из свежего дампа будет другим, md5 не совпадут | точный корпус — `python scripts/fetch_data.py --what corpus` (Hugging Face, https://huggingface.co/datasets/Os2003/engrams-ruwiki-v3). Если нужен именно дамп: передать `--dump-date ГГГГММДД` с датой выпуска, если он ещё лежит на https://dumps.wikimedia.org/ruwiki/ или в зеркалах |

---

**EN.** Every script runs from the root of the clone and by default reads and writes only repository folders. There are no paths outside the clone in the code.

Run order: `pip install -r requirements.txt`, `python -m spacy download ru_core_news_lg`, `python scripts/smoke_test.py` (checks the part 3–4 pipeline on a small sample, no internet needed). Then per part: figures `python docs/figures/make_partNN_figures.py`; task set `python scripts/part02/select_tasks.py`; corpus `python scripts/fetch_data.py --what corpus` and `python scripts/part03/check_manifest.py`; streams `python scripts/fetch_data.py --what streams` or `python scripts/part04/build_streams_v3.py`.

Layout: `data/tasks/` (part 2, in git); `data/corpus/` (manifest in git; `chunks_584/` from Hugging Face or the part 3 script, only fragment 2 in git); `data/raw/wiki_dump/` (dump, not in git); `data/tokenizer_v3/` (vocabulary, in git); `data/streams_v3/` (streams from Hugging Face or the part 4 script, only fragment 2 in git); `data/sample/` (sample dump for the smoke test); `data/work/` (rebuilt outputs, not in git).

Placeholders: (1) `scripts/part03/download_wiki_ru.py` line 147, `--dump-date latest` downloads a newer dump than the one the corpus was built from (December 2025), so md5 sums will differ; the exact corpus is on Hugging Face (`python scripts/fetch_data.py --what corpus`, https://huggingface.co/datasets/Os2003/engrams-ruwiki-v3).
