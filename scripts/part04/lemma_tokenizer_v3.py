# -*- coding: utf-8 -*-
"""
lemma_tokenizer_v3.py — Построение словаря лемм (ENGRAMS v3).

ОТЛИЧИЕ ОТ v2 (критическое):
  БЫЛО:  if token.is_alpha and len(token.text) > 1:
  СТАЛО: if token.is_alpha:
  → в словарь возвращаются «и», «а», «с», «о», «у», «я».

Прочее ОТЛИЧИЕ:
  - модель по умолчанию ru_core_news_lg (sm ломает морфологию частиц: «чём-то» → NOUN)
  - ОБЯЗАТЕЛЬНАЯ проверка контрольного списка служебных слов (§1.1 ТЗ).
    Если хоть одно отсутствует — словарь НЕ сохраняется, exit(1).

Рецепт предобработки НЕ ИЗМЕНЁН (иначе координаты уедут):
  - удаление U+0301, замена \xa0, разделение слипшихся слов, BMP-фильтр
  - построчно, строки начинающиеся с '#' пропускаются

Запуск из корня репозитория (пути по умолчанию — папки репозитория):
  python scripts/part04/lemma_tokenizer_v3.py --min-freq 5 --max-vocab 100000 --workers 6
  вход : data/corpus/chunks_584/chunk_*.txt   (создаёт scripts/part03/download_wiki_ru.py)
  выход: data/work/tokenizer_v3/           (опубликованный словарь — data/tokenizer_v3/)
         data/work/reports/

Для публикации изменены только пути: аргументы получили значения по умолчанию
внутри папок репозитория (см. docs/DATA_PATHS.md), пример запуска переписан под них.
Логика сборки — как в исходном запуске.
"""

from __future__ import annotations
import os, sys, json, argparse, re, multiprocessing as mp
from pathlib import Path
from glob import glob
from collections import Counter
from typing import List, Dict

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

SPECIAL_TOKENS = ["[UNK]", "[PAD]", "[CLS]", "[SEP]", "[MASK]"]

# Пунктуация + математические знаки (ИДЕНТИЧНО v2 — не менять)
PUNCT_TOKENS = [
    ".", "!", "?", "…",
    ",", ";", ":", "—", "–", "-",
    "(", ")", "[", "]", "{", "}", "«", "»", "\"", "'",
    "+", "=", "<", ">", "≤", "≥", "≠", "±", "×", "÷",
    "∞", "∑", "∏", "∫", "√", "∂", "∇", "∈", "∉", "⊂",
    "⊃", "∪", "∩", "∅", "→", "←", "↔", "⟹", "⟺",
    "/", "\\", "%", "°", "^", "|", "&", "~", "#", "@",
]

# ── КОНТРОЛЬНЫЙ СПИСОК §1.1 ТЗ: все эти слова ОБЯЗАНЫ быть в словаре ──
SERVICE_WORDS: Dict[str, List[str]] = {
    "союзы": [
        "и", "а", "но", "да", "или", "либо", "зато", "однако", "чтобы", "если",
        "хотя", "пока", "потому", "ибо", "дабы", "притом", "причём", "также", "тоже",
    ],
    "предлоги": [
        "в", "на", "с", "о", "у", "к", "от", "за", "под", "над", "при", "для",
        "из", "до", "по", "про", "через", "между", "около", "вокруг", "сквозь",
        "вдоль", "кроме", "вместо", "ради", "без", "среди", "перед", "после",
        "близ", "возле", "мимо", "против", "сверх",
    ],
    "частицы": [
        "не", "ни", "же", "ли", "бы", "вот", "вон", "даже", "только", "лишь",
        "уж", "ведь", "разве",
    ],
    "местоимения": [
        "я", "ты", "он", "она", "оно", "мы", "вы", "они", "себя", "свой",
        "наш", "ваш", "их", "его", "её",
    ],
}


def _preprocess_ref(text: str) -> str:
    """Эталонный рецепт. Дублируется внутри воркера (spawn)."""
    text = text.replace('\xa0', ' ')
    text = text.replace('\u0301', '')
    text = re.sub(r'([а-яёa-z])([А-ЯЁA-Z])', r'\1 \2', text)
    text = ''.join(c for c in text if ord(c) < 0x10000)
    return text


def lemmatize_file(args):
    """Воркер: лемматизирует один файл → Counter лемм + пунктуации."""
    path, spacy_model_name = args
    import spacy, re as _re
    from collections import Counter as _Counter

    def _preprocess(text):
        text = text.replace('\xa0', ' ')
        text = text.replace('\u0301', '')
        text = _re.sub(r'([а-яёa-z])([А-ЯЁA-Z])', r'\1 \2', text)
        text = ''.join(c for c in text if ord(c) < 0x10000)
        return text

    nlp = spacy.load(spacy_model_name, disable=["ner", "parser"])
    punct_set = set(PUNCT_TOKENS)
    counter = _Counter()

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if _re.match(r'^#{1,}', line):
                continue
            clean_lines.append(_preprocess(line))

        for doc in nlp.pipe(clean_lines, batch_size=500):
            for token in doc:
                # ── ЕДИНСТВЕННАЯ ПРАВКА ОТНОСИТЕЛЬНО v2: снят len(...) > 1 ──
                if token.is_alpha:
                    lemma = token.lemma_.lower().strip()
                    if lemma:
                        counter[lemma] += 1
                elif token.text.strip() in punct_set:
                    counter[token.text.strip()] += 1

    except Exception as e:
        print(f"[warn] Ошибка в {path}: {e}", file=sys.stderr)

    return counter


def build_lemma_vocab(text_files, min_freq, max_vocab_size, spacy_model, num_workers):
    print(f"Лемматизация {len(text_files)} файлов ({num_workers} воркеров, {spacy_model})...")

    total_counter = Counter()
    tasks = [(f, spacy_model) for f in text_files]
    ctx = mp.get_context("spawn")

    with ctx.Pool(num_workers) as pool:
        from tqdm import tqdm
        for counter in tqdm(pool.imap_unordered(lemmatize_file, tasks),
                            total=len(tasks), desc="Файлы"):
            total_counter.update(counter)

    print(f"  Уникальных лемм до фильтрации: {len(total_counter):,}")

    punct_set = set(PUNCT_TOKENS)
    filtered = {l: f for l, f in total_counter.items()
                if f >= min_freq or l in punct_set}
    print(f"  После фильтрации (min_freq={min_freq}): {len(filtered):,}")

    if len(filtered) > max_vocab_size:
        non_punct = [(l, f) for l, f in filtered.items() if l not in punct_set]
        non_punct.sort(key=lambda x: -x[1])
        keep = dict(non_punct[:max_vocab_size - len(punct_set)])
        keep.update({p: filtered[p] for p in punct_set if p in filtered})
        filtered = keep
        print(f"  После ограничения (max={max_vocab_size}): {len(filtered):,}")

    return filtered, total_counter


def build_vocab_mappings(lemma_freqs):
    id2lemma: List[str] = list(SPECIAL_TOKENS)

    punct_set = set(PUNCT_TOKENS)
    sorted_lemmas = sorted(
        [(l, f) for l, f in lemma_freqs.items() if l not in punct_set],
        key=lambda x: -x[1]
    )
    for lemma, _ in sorted_lemmas:
        id2lemma.append(lemma)

    seen = set(id2lemma)
    for punct in PUNCT_TOKENS:
        if punct not in seen:
            id2lemma.append(punct)
            seen.add(punct)

    lemma2id = {lemma: idx for idx, lemma in enumerate(id2lemma)}
    return lemma2id, id2lemma


# ─────────────────────────────────────────────────────────────
# ПРОВЕРКА §1.1 — БЕЗ НЕЁ СЛОВАРЬ НЕ СОХРАНЯЕТСЯ
# ─────────────────────────────────────────────────────────────
def verify_service_words(lemma2id, lemma_freqs, report_dir, raw_counter):
    print("\n" + "=" * 60)
    print("ПРОВЕРКА §1.1: служебные слова в словаре")
    print("=" * 60)

    missing = []
    lines = []
    for group, words in SERVICE_WORDS.items():
        present = [w for w in words if w in lemma2id]
        absent = [w for w in words if w not in lemma2id]
        missing.extend(absent)
        lines.append(f"\n[{group}] {len(present)}/{len(words)}")
        for w in words:
            if w in lemma2id:
                lines.append(f"  ✓ {w:<10} id={lemma2id[w]:<7} freq={lemma_freqs.get(w, 0):,}")
            else:
                lines.append(f"  ✗ {w:<10} ОТСУТСТВУЕТ  (freq в корпусе={raw_counter.get(w, 0):,})")
        print(f"  [{group}]: {len(present)}/{len(words)}"
              + ("" if not absent else f"  ОТСУТСТВУЮТ: {' '.join(absent)}"))

    # Ключевые токены дефекта v2 — крупным планом
    print("\n  Токены, потерянные в v2 (должны вернуться):")
    for w in ["и", "а", "с", "о", "у", "я"]:
        if w in lemma2id:
            print(f"    ✓ «{w}»  id={lemma2id[w]:<7} freq={lemma_freqs.get(w, 0):,}")
        else:
            print(f"    ✗ «{w}»  ВСЁ ЕЩЁ ОТСУТСТВУЕТ")

    # Одиночные буквы, попавшие в словарь (мусор из инициалов) — информативно
    singles = sorted(
        [(l, lemma_freqs[l]) for l in lemma_freqs
         if len(l) == 1 and l.isalpha()],
        key=lambda x: -x[1]
    )
    print(f"\n  Одиночных букв в словаре: {len(singles)}")
    print("    " + "  ".join(f"«{l}»:{f:,}" for l, f in singles[:20]))
    lines.append(f"\n[одиночные буквы в словаре] {len(singles)}")
    for l, f in singles:
        lines.append(f"  «{l}» id={lemma2id[l]} freq={f:,}")

    rd = Path(report_dir)
    rd.mkdir(parents=True, exist_ok=True)
    with open(rd / "check_service_words_v3.txt", "w", encoding="utf-8") as f:
        f.write("ПРОВЕРКА §1.1 — служебные слова, lemma_tokenizer_v3\n")
        f.write(f"VOCAB = {len(lemma2id)}\n")
        f.write(f"ОТСУТСТВУЮТ: {missing if missing else 'нет — ВСЁ НА МЕСТЕ'}\n")
        f.write("\n".join(lines) + "\n")
    print(f"\n  Отчёт: {rd / 'check_service_words_v3.txt'}")

    if missing:
        print("\n  ✗✗ ПРОВЕРКА ПРОВАЛЕНА. Отсутствуют: " + " ".join(missing))
        print("  Словарь НЕ сохранён. Пересобирать.")
        return False

    print("\n  ✓✓ ПРОВЕРКА ПРОЙДЕНА: все служебные слова в словаре.")
    return True


def save_vocab(lemma2id, id2lemma, lemma_freqs, out_dir, spacy_model,
               min_freq, max_vocab):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with open(out / "lemma2id.json", "w", encoding="utf-8") as f:
        json.dump(lemma2id, f, ensure_ascii=False, indent=2)
    print(f"  Сохранено: lemma2id.json ({len(lemma2id):,} токенов)")

    with open(out / "id2lemma.txt", "w", encoding="utf-8") as f:
        for lemma in id2lemma:
            f.write(lemma + "\n")
    print(f"  Сохранено: id2lemma.txt")

    with open(out / "lemma_vocab_size.txt", "w") as f:
        f.write(str(len(id2lemma)) + "\n")

    top_lemmas = sorted(lemma_freqs.items(), key=lambda x: -x[1])[:1000]
    stats = {
        "version": "v3",
        "spacy_model": spacy_model,
        "vocab_size": len(id2lemma),
        "min_freq": min_freq,
        "max_vocab": max_vocab,
        "diff_from_v2": "снят фильтр len(token.text) > 1",
        "known_model_quirk": "lg лемматизирует 'ней' как 'ней' (не 'она') — оставлено как есть",
        "special_tokens": SPECIAL_TOKENS,
        "punct_tokens": PUNCT_TOKENS,
        "unk_id": lemma2id["[UNK]"],
        "top_lemmas": [{"lemma": l, "freq": f, "id": lemma2id.get(l, -1)}
                       for l, f in top_lemmas],
    }
    with open(out / "lemma_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"  Сохранено: lemma_stats.json")
    print(f"  VOCAB SIZE: {len(id2lemma):,}   (для --vocab-size далее)")


ROOT = Path(__file__).resolve().parents[2]   # корень репозитория


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--text-folder", default=str(ROOT / "data/corpus/chunks_584"))
    p.add_argument("--output-dir",  default=str(ROOT / "data/work/tokenizer_v3"))
    p.add_argument("--report-dir",  default=str(ROOT / "data/work/reports"))
    p.add_argument("--min-freq",    type=int, default=5)
    p.add_argument("--max-vocab",   type=int, default=100_000)
    p.add_argument("--spacy-model", type=str, default="ru_core_news_lg")
    p.add_argument("--workers",     type=int, default=6)
    p.add_argument("--chunk-limit", type=int, default=None,
                   help="Только N первых чанков (для smoke-теста)")
    return p.parse_args()


def main():
    args = parse_args()

    files = sorted(glob(str(Path(args.text_folder) / "chunk_*.txt")))
    if not files:
        raise FileNotFoundError(f"Нет chunk_*.txt в {args.text_folder}")
    if args.chunk_limit:
        files = files[:args.chunk_limit]
        print(f"[SMOKE] Ограничение: {len(files)} чанков — словарь НЕПОЛНЫЙ")
    print(f"Файлов: {len(files)}")

    lemma_freqs, raw_counter = build_lemma_vocab(
        files, args.min_freq, args.max_vocab, args.spacy_model, args.workers
    )
    lemma2id, id2lemma = build_vocab_mappings(lemma_freqs)

    ok = verify_service_words(lemma2id, lemma_freqs, args.report_dir, raw_counter)
    if not ok and not args.chunk_limit:
        sys.exit(1)
    if not ok:
        print("[SMOKE] Проверка провалена, но это ограниченный прогон — сохраняю всё равно.")

    print()
    save_vocab(lemma2id, id2lemma, lemma_freqs, args.output_dir,
               args.spacy_model, args.min_freq, args.max_vocab)

    n_lem = len(id2lemma) - len(SPECIAL_TOKENS) - len(PUNCT_TOKENS)
    print(f"\nГОТОВО. Словарь: {len(id2lemma):,} токенов")
    print(f"  спец={len(SPECIAL_TOKENS)}, пункт/мат={len(PUNCT_TOKENS)}, леммы={n_lem}")


if __name__ == "__main__":
    main()
