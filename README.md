# ENGRAMS: sequence memory

[Русская версия](README.ru.md)

> ## 🤝 Why we are opening this work
>
> **The goal of publishing it is to build a community: a group of people who are interested in this work and would like to join the project.** The code, the results and the open questions are published so that they can be checked, developed and explored together. If you are interested, write in the discussion group [t.me/sequence_memory](https://t.me/sequence_memory) or open an issue in this repository. The series is published in the channel [t.me/E_N_G_R_A_M_S](https://t.me/E_N_G_R_A_M_S); discussion happens in the group @sequence_memory linked to it. This keeps the parts of the series in order in the channel instead of mixed with questions and comments.

ENGRAMS is a language model built from corpus statistics instead of backpropagation. It counts how often words occur at each distance from each other, normalizes those counts at the candidate (which turns them into pointwise mutual information), and predicts the next word with a geometric mean of the context rows, plus recall from a memory of text windows. Every row and column of every matrix is a word, so every step of a prediction can be read and traced back to the corpus.

Champion on lemmas of Russian Wikipedia (about 1.1 billion objects, vocabulary of 100,005), top-1 accuracy on 300 tasks:

| method | leak | gen |
|---|---:|---:|
| recall by n-gram voting | 94.00 | 33.67 |
| composition over window memory, β = 32 | 92.00 | 26.00 |
| switching by match depth | 98.67* | — |

\* measured on 150 report tasks of a non-strict dump: +10/−0 against the best fixed blend (92.00), p = 0.002. *leak*: the task's window is in memory; *gen*: a ±30 neighbourhood of the task is excluded. The memory covers about 0.7% of the corpus, which is why gen is low; see part 19.

## The series

The project is published in 19 parts. Each part adds working code to this repository under a tag `part-NN` and comes with two articles, Russian and English, in [`docs/articles/`](docs/articles/).

| # | part | status |
|---|---|---|
| 1 | [Overview: statistics instead of its approximation](docs/articles/en/01_overview.md) | published |
| 2 | [How we measure: tasks, leak and gen, noise and the zero rule](docs/articles/en/02_measurement.md) | published |
| 3 | [The corpus: where the text comes from and why the recipe is frozen](docs/articles/en/03_corpus.md) | published |
| 4 | [Lemmas as objects: tokenizer v3](docs/articles/en/04_lemmas.md) | published |
| 5–6 | Why not BPE, segments and pairs | planned |
| 7–10 | Rank matrices and B = Fᵀ, Zipf weights, normalization → PMI, PMI without counts | planned |
| 11–17 | Geometric mean, clouds, window memory, recall, n-grams, switching, the champion end to end | planned |
| 18–19 | Vocabulary: general words vs names; results and open directions | planned |

## How to run

A clone works right away: every script runs from the repository root and writes only into its folders.

```bash
git clone https://github.com/oscorp/ENGRAMS.git && cd ENGRAMS
pip install -r requirements.txt
python -m spacy download ru_core_news_lg     # spaCy model for parts 3–4
python scripts/smoke_test.py                 # checks the part 3–4 pipeline on a small sample
```

In Jupyter: `%pip install -r requirements.txt`, then `!python …` for each command.

| part | command |
|---|---|
| 1–4, figures | `python docs/figures/make_part01_figures.py` … `make_part04_figures.py` |
| 2, the working 300 tasks | `python scripts/part02/select_tasks.py` |
| 3, corpus | `python scripts/fetch_data.py --what corpus`, check `python scripts/part03/check_manifest.py` |
| 3, line preparation | `python scripts/part03/preprocess_v3.py --demo` |
| 4, streams | `python scripts/fetch_data.py --what streams` or build `python scripts/part04/build_streams_v3.py` |

Where the data lives, what is downloaded from Hugging Face and which links are still placeholders: [docs/DATA_PATHS.md](docs/DATA_PATHS.md).

## Repository layout

```
docs/articles/{ru,en}/   articles, one per part and language
docs/figures/            figure scripts and rendered figures
scripts/                 scripts by part (scripts/partNN/), smoke_test.py check, fetch_data.py download
data/                    tasks, vocabulary, corpus manifest, fragment 2; large files on Hugging Face
requirements.txt         dependencies of all parts
```

Project rules under which all numbers were obtained: [docs/RULES.en.md](docs/RULES.en.md).

## License

Source-available, not OSI open source.

- Code: [PolyForm Noncommercial 1.0.0](LICENSE). Free for research, education and other non-commercial purposes.
- Articles and the author's own data: CC BY-NC 4.0; data derived from Wikipedia: CC BY-SA 4.0. See [LICENSE-DATA.md](LICENSE-DATA.md).
- The methods are covered by Eurasian patent EA 044182 B1 and a pending patent application. **Any commercial use requires a license from the author**: see [COMMERCIAL.md](COMMERCIAL.md) and [NOTICE.md](NOTICE.md).

## Author

Oleg A. Serebrennikov. Telegram: publications in the channel [t.me/E_N_G_R_A_M_S](https://t.me/E_N_G_R_A_M_S), discussion in the group [t.me/sequence_memory](https://t.me/sequence_memory).
