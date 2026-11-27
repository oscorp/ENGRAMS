# Словарь токенизатора v3 / Tokenizer v3 vocabulary

**RU.** Словарь, на котором построены все потоки, матрицы и числа серии ENGRAMS (часть 4).

| файл | что внутри |
|---|---|
| `lemma2id.json` | «лемма → номер», 100 005 ячеек: 0–4 служебные метки (`[UNK]` = 0), 5–99 945 леммы по убыванию частоты, 99 946–100 004 знаки препинания и математические знаки. Единственный источник истины: обратное отображение строится из него. |
| `lemma_stats.json` | модель spaCy (`ru_core_news_lg`), `min_freq = 5`, `max_vocab = 100 000`, списки служебных меток и знаков, 1000 самых частых лемм с частотами, известный дефект модели. |

Собран скриптом `scripts/part04/lemma_tokenizer_v3.py` по 584 фрагментам русской Википедии (часть 3). Лицензия: CC BY-SA 4.0, данные производны от Википедии.

---

**EN.** The vocabulary on which every stream, matrix and number of the ENGRAMS series is built (part 4).

| file | contents |
|---|---|
| `lemma2id.json` | "lemma → id", 100,005 entries: 0–4 special marks (`[UNK]` = 0), 5–99,945 lemmas by decreasing frequency, 99,946–100,004 punctuation and mathematical signs. The single source of truth: the reverse map is built from it. |
| `lemma_stats.json` | spaCy model (`ru_core_news_lg`), `min_freq = 5`, `max_vocab = 100,000`, lists of special marks and signs, the 1000 most frequent lemmas with frequencies, a known model defect. |

Built by `scripts/part04/lemma_tokenizer_v3.py` from the 584 fragments of the Russian Wikipedia (part 3). Licence: CC BY-SA 4.0, derived from Wikipedia.
