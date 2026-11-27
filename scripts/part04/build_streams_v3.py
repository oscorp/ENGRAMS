# -*- coding: utf-8 -*-
"""
build_streams_v3.py — ОДИН проход spaCy → ТРИ синхронных потока (ТЗ §1.2).

Заменяет build_all_lemma_ids.py.

Выход (на каждый чанк):
  streams/lemmas_npy_v3/chunk_NNNNNN.npy   int32   id лемм
  streams/morph_npy_v3/chunk_NNNNNN.npy    uint16  морфо-коды, ТЕ ЖЕ КООРДИНАТЫ
  streams/spans_v3/sent_spans_chunk_NNNNNN.pkl     границы предложений (razdel)
                                                    в координатах ПОТОКА: [(start, stop), ...]

🔴 КРИТИЧНО: lemmas[i] и morph[i] — один и тот же токен. Длины обязаны совпадать.
   Проверка встроена: при расхождении чанк НЕ сохраняется.

ОТЛИЧИЯ ОТ v2:
  1. снят фильтр len(token.text) > 1
  2. OOV → [UNK] (НЕ пропуск!) — дистанция между соседями не искажается (ответ Олега №7)
  3. добавлен morph-поток (uint16, не int16 — иначе POS<<13 переполняется)
  4. добавлены спаны предложений (razdel) — без второго прохода
  5. модель ru_core_news_lg

РЕЦЕПТ preprocess И ПОРЯДОК ОБХОДА — НЕ ТРОНУТЫ (иначе координаты уедут).
Строки пайпятся так же, как в vocab-проходе (nlp.pipe(clean_lines)), поэтому
токенизация ИДЕНТИЧНА lemma_tokenizer_v3. Спаны получаются наложением razdel-границ
на char-офсеты spaCy внутри той же строки — токенизация от этого не меняется.

Запуск из корня репозитория (пути по умолчанию — папки репозитория):
  python scripts/part04/build_streams_v3.py --workers 6
  вход : data/corpus/chunks_584/chunk_*.txt   (создаёт scripts/part03/download_wiki_ru.py)
         data/tokenizer_v3/lemma2id.json   (опубликованный словарь)
  выход: data/streams_v3/{lemmas_npy_v3, morph_npy_v3, spans_v3}/
         data/work/reports/

Для публикации изменены только пути: аргументы получили значения по умолчанию
внутри папок репозитория (см. docs/DATA_PATHS.md), пример запуска переписан под них.
Логика сборки — как в исходном запуске.
"""
from __future__ import annotations
import os, sys, json, pickle, argparse, time
import multiprocessing as mp
from glob import glob
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_v3 import pack_morph, MORPH_DTYPE, LEMMA_DTYPE  # noqa: E402

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


ROOT = Path(__file__).resolve().parents[2]   # корень репозитория


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--chunks-dir',  default=str(ROOT / 'data/corpus/chunks_584'))
    p.add_argument('--out-root',    default=str(ROOT / 'data/streams_v3'),
                   help='Корень streams/ — внутри создаст lemmas_npy_v3, morph_npy_v3, spans_v3')
    p.add_argument('--lemma2id',    default=str(ROOT / 'data/tokenizer_v3/lemma2id.json'))
    p.add_argument('--report-dir',  default=str(ROOT / 'data/work/reports'))
    p.add_argument('--spacy-model', default='ru_core_news_lg')
    p.add_argument('--workers',     type=int, default=6)
    p.add_argument('--chunk-limit', type=int, default=None)
    p.add_argument('--force',       action='store_true',
                   help='Пересобрать даже готовые чанки')
    return p.parse_args()


# ─────────────────────────────────────────────────────────────
# ВОРКЕР
# ─────────────────────────────────────────────────────────────
def process_chunk(task):
    (txt_path, lemma_out, morph_out, span_out,
     lemma2id_path, spacy_model, force) = task

    import spacy, re as _re, json as _json, pickle as _pickle
    import numpy as _np
    from razdel import sentenize
    from common_v3 import pack_morph as _pack, MORPH_DTYPE as _MD, LEMMA_DTYPE as _LD

    name = Path(txt_path).stem

    if (not force and os.path.exists(lemma_out)
            and os.path.exists(morph_out) and os.path.exists(span_out)):
        n = len(_np.load(lemma_out, mmap_mode='r'))
        return {"chunk": name, "skipped": True, "n_tokens": int(n),
                "n_unk": -1, "n_sents": -1, "ok": True}

    def _preprocess(text):
        text = text.replace('\xa0', ' ')
        text = text.replace('\u0301', '')
        text = _re.sub(r'([а-яёa-z])([А-ЯЁA-Z])', r'\1 \2', text)
        text = ''.join(c for c in text if ord(c) < 0x10000)
        return text

    with open(lemma2id_path, 'r', encoding='utf-8') as f:
        lemma2id = _json.load(f)
    UNK_ID = lemma2id['[UNK]']

    nlp = spacy.load(spacy_model, disable=['parser', 'ner'])

    with open(txt_path, encoding='utf-8', errors='ignore') as f:
        raw_lines = f.readlines()

    clean_lines = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        if _re.match(r'^#{1,}', line):
            continue
        clean_lines.append(_preprocess(line))

    ids, morphs, sent_spans = [], [], []
    n_unk = 0

    for line, doc in zip(clean_lines, nlp.pipe(clean_lines, batch_size=500)):
        # границы предложений внутри строки — в CHAR-координатах
        bounds = [(s.start, s.stop) for s in sentenize(line)]
        b_i = 0
        cur_start = len(ids)   # позиция в ПОТОКЕ, где начинается текущее предложение

        for token in doc:
            # ── рецепт v2 + снятый фильтр длины ──
            if token.is_alpha:
                lemma = token.lemma_.lower().strip()
            elif token.is_punct or token.text in lemma2id:
                lemma = token.text.strip()
            else:
                continue
            if not lemma:
                continue

            # ── закрыть предложение, если токен ушёл за его границу ──
            while b_i < len(bounds) and token.idx >= bounds[b_i][1]:
                if len(ids) > cur_start:
                    sent_spans.append((cur_start, len(ids)))
                cur_start = len(ids)
                b_i += 1

            # ── OOV → [UNK], НЕ пропуск (ответ Олега №7) ──
            tok_id = lemma2id.get(lemma)
            if tok_id is None:
                tok_id = UNK_ID
                n_unk += 1

            ids.append(tok_id)
            morphs.append(_pack(token))

        if len(ids) > cur_start:
            sent_spans.append((cur_start, len(ids)))

    ids_arr   = _np.asarray(ids,    dtype=_LD)
    morph_arr = _np.asarray(morphs, dtype=_MD)

    # ── 🔴 ПРОВЕРКА СИНХРОННОСТИ: без неё не сохраняем ──
    if len(ids_arr) != len(morph_arr):
        return {"chunk": name, "skipped": False, "ok": False,
                "n_tokens": len(ids_arr), "n_morph": len(morph_arr),
                "n_unk": n_unk, "n_sents": len(sent_spans),
                "error": "ДЕСИНХРОН lemmas/morph"}

    for d in (lemma_out, morph_out, span_out):
        os.makedirs(os.path.dirname(os.path.abspath(d)), exist_ok=True)
    _np.save(lemma_out, ids_arr)
    _np.save(morph_out, morph_arr)
    with open(span_out, 'wb') as f:
        _pickle.dump(sent_spans, f, protocol=4)

    return {"chunk": name, "skipped": False, "ok": True,
            "n_tokens": int(len(ids_arr)), "n_unk": n_unk,
            "n_sents": len(sent_spans)}


# ─────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    t0 = time.time()

    out_root  = Path(args.out_root)
    d_lemmas  = out_root / 'lemmas_npy_v3'
    d_morph   = out_root / 'morph_npy_v3'
    d_spans   = out_root / 'spans_v3'
    for d in (d_lemmas, d_morph, d_spans):
        d.mkdir(parents=True, exist_ok=True)

    with open(args.lemma2id, encoding='utf-8') as f:
        lemma2id = json.load(f)
    VOCAB = len(lemma2id)

    print("=" * 62)
    print("build_streams_v3 — леммы + морфология + спаны за ОДИН проход")
    print("=" * 62)
    print(f"  словарь : {args.lemma2id}")
    print(f"  VOCAB   : {VOCAB:,}   UNK_ID={lemma2id['[UNK]']}")
    print(f"  модель  : {args.spacy_model}")
    print(f"  выход   : {out_root}")

    txt_files = sorted(glob(str(Path(args.chunks_dir) / 'chunk_*.txt')))
    if args.chunk_limit:
        txt_files = txt_files[:args.chunk_limit]
        print(f"  [SMOKE] ограничение: {len(txt_files)} чанков")
    if not txt_files:
        raise FileNotFoundError(f"Нет chunk_*.txt в {args.chunks_dir}")
    print(f"  чанков  : {len(txt_files)}   workers={args.workers}\n")

    tasks = []
    for txt in txt_files:
        name = Path(txt).stem
        tasks.append((
            txt,
            str(d_lemmas / f"{name}.npy"),
            str(d_morph  / f"{name}.npy"),
            str(d_spans  / f"sent_spans_{name}.pkl"),
            args.lemma2id, args.spacy_model, args.force,
        ))

    ctx = mp.get_context('spawn')
    results = []
    BATCH = args.workers * 2      # маленький батч → меньше RAM
    n_done = 0
    with ctx.Pool(processes=args.workers) as pool:
        for i in range(0, len(tasks), BATCH):
            for r in pool.map(process_chunk, tasks[i:i + BATCH]):
                results.append(r)
            n_done = min(i + BATCH, len(tasks))
            fresh = sum(1 for r in results if not r['skipped'])
            toks  = sum(r['n_tokens'] for r in results)
            # разреженный прогресс: по батчам, не по окнам
            print(f"  {n_done}/{len(tasks)} чанков  новых={fresh}  "
                  f"токенов={toks:,}  ({time.time()-t0:.0f}с)", flush=True)

    # ── СВОДКА + ПРОВЕРКА ──
    bad = [r for r in results if not r['ok']]
    fresh = [r for r in results if not r['skipped']]
    total_tokens = sum(r['n_tokens'] for r in results)
    total_unk    = sum(r['n_unk'] for r in fresh if r['n_unk'] >= 0)
    total_sents  = sum(r['n_sents'] for r in fresh if r['n_sents'] >= 0)
    fresh_tokens = sum(r['n_tokens'] for r in fresh)

    print("\n" + "=" * 62)
    print("ИТОГ")
    print("=" * 62)
    print(f"  чанков обработано : {len(fresh)}  (пропущено готовых: {len(results)-len(fresh)})")
    print(f"  токенов всего     : {total_tokens:,}")
    if fresh_tokens:
        print(f"  [UNK]             : {total_unk:,}  ({100*total_unk/fresh_tokens:.2f}% свежих)")
        print(f"  предложений       : {total_sents:,}")

    # независимая сверка длин на диске
    print("\n  Сверка len(lemmas) == len(morph) по всем файлам...")
    desync = []
    for txt in txt_files:
        name = Path(txt).stem
        lp, mp_ = d_lemmas / f"{name}.npy", d_morph / f"{name}.npy"
        if not (lp.exists() and mp_.exists()):
            desync.append((name, 'ФАЙЛ ОТСУТСТВУЕТ'))
            continue
        nl = len(np.load(lp, mmap_mode='r'))
        nm = len(np.load(mp_, mmap_mode='r'))
        if nl != nm:
            desync.append((name, f'{nl} != {nm}'))

    if desync or bad:
        print(f"  ✗✗ ПРОБЛЕМЫ: {len(desync) + len(bad)}")
        for name, why in desync[:20]:
            print(f"     {name}: {why}")
        for r in bad[:20]:
            print(f"     {r['chunk']}: {r.get('error')}")
    else:
        print(f"  ✓✓ ВСЕ {len(txt_files)} ЧАНКОВ СИНХРОННЫ")

    rd = Path(args.report_dir)
    rd.mkdir(parents=True, exist_ok=True)
    with open(rd / 'streams_manifest_v3.json', 'w', encoding='utf-8') as f:
        json.dump({
            "version": "v3",
            "spacy_model": args.spacy_model,
            "vocab_size": VOCAB,
            "unk_id": lemma2id['[UNK]'],
            "morph_dtype": "uint16",
            "morph_layout": "см. common_v3.MORPH_LAYOUT",
            "oov_policy": "OOV → [UNK] (дистанция сохраняется)",
            "n_chunks": len(txt_files),
            "total_tokens": total_tokens,
            "desync": desync,
            "chunks": {r['chunk']: r['n_tokens'] for r in results},
        }, f, ensure_ascii=False, indent=2)
    print(f"\n  Манифест: {rd / 'streams_manifest_v3.json'}")
    print(f"  Время: {time.time()-t0:.0f}с")

    if desync or bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
