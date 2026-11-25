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
| 3–6 | Corpus, lemmas, why not BPE, segments and pairs | planned |
| 7–10 | Rank matrices and B = Fᵀ, Zipf weights, normalization → PMI, PMI without counts | planned |
| 11–17 | Geometric mean, clouds, window memory, recall, n-grams, switching, the champion end to end | planned |
| 18–19 | Vocabulary: general words vs names; results and open directions | planned |

## Repository layout

```
docs/articles/{ru,en}/   articles, one per part and language
docs/figures/            figure scripts and rendered figures
src/engrams/             library code (from part 2 on)
scripts/                 scripts by part (scripts/partNN/)
data/                    dictionaries and the author's own data; large files on Hugging Face
```

Project rules under which all numbers were obtained: [docs/RULES.en.md](docs/RULES.en.md).

To rebuild the figures of parts 1 and 2:

```
pip install numpy matplotlib
python docs/figures/make_part01_figures.py
python docs/figures/make_part02_figures.py
```

## License

Source-available, not OSI open source.

- Code: [PolyForm Noncommercial 1.0.0](LICENSE). Free for research, education and other non-commercial purposes.
- Articles and the author's own data: CC BY-NC 4.0; data derived from Wikipedia: CC BY-SA 4.0. See [LICENSE-DATA.md](LICENSE-DATA.md).
- The methods are covered by Eurasian patent EA 044182 B1 and a pending patent application. **Any commercial use requires a license from the author**: see [COMMERCIAL.md](COMMERCIAL.md) and [NOTICE.md](NOTICE.md).

## Author

Oleg A. Serebrennikov. Telegram: publications in the channel [t.me/E_N_G_R_A_M_S](https://t.me/E_N_G_R_A_M_S), discussion in the group [t.me/sequence_memory](https://t.me/sequence_memory).
