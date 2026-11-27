# -*- coding: utf-8 -*-
"""
build_top_lemmas_v3.py — target-фильтр: топ-N самых частых токенов в потоках v3.

Аналог v2-файла test_samples_local/top_lemmas.json (top_n=1000, пунктуация ВКЛЮЧЕНА).
Отличие v3: в потоке есть [UNK]=0 (5.13%) — исключается (--exclude-unk, по умолчанию вкл),
предсказывать UNK бессмысленно.

Выход: {'chunk': ..., 'top_n': N, 'min_count': ..., 'max_count': ..., 'top_ids': [...]}

Запуск из корня репозитория:
  python scripts/part04/build_top_lemmas_v3.py
  вход : data/streams_v3/lemmas_npy_v3/   (создаёт scripts/part04/build_streams_v3.py)
  выход: data/work/top_lemmas_1000.json        (опубликованный — data/tasks/top_lemmas_1000.json)

Для публикации изменены только пути: аргументы получили значения по умолчанию
внутри папок репозитория (см. docs/DATA_PATHS.md). Логика — как в исходном запуске.
"""
from __future__ import annotations
import argparse, ast, json, sys, time
from pathlib import Path
from glob import glob
import numpy as np


ROOT = Path(__file__).resolve().parents[2]   # корень репозитория


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--npy-dir', default=str(ROOT / 'data/streams_v3/lemmas_npy_v3'),
                    help='streams/lemmas_npy_v3')
    ap.add_argument('--chunks', default='0-583', help='диапазон чанков для подсчёта частот')
    ap.add_argument('--output', default=str(ROOT / 'data/work/top_lemmas_1000.json'))
    ap.add_argument('--top-n', type=int, default=1000)
    ap.add_argument('--vocab', type=int, default=100005)
    ap.add_argument('--exclude-unk', action='store_true', default=True)
    ap.add_argument('--keep-unk', dest='exclude_unk', action='store_false')
    ap.add_argument('--name-template', default='chunk_{:06d}.npy')
    args = ap.parse_args()

    a, b = (args.chunks.split('-') + [args.chunks])[:2]
    lo, hi = int(a), int(b)
    counts = np.zeros(args.vocab, np.int64)
    t0 = time.time(); n_tok = 0; used = 0
    for ci in range(lo, hi + 1):
        p = Path(args.npy_dir) / args.name_template.format(ci)
        if not p.exists():
            continue
        arr = np.load(p)
        counts += np.bincount(arr, minlength=args.vocab)[:args.vocab]
        n_tok += len(arr); used += 1
        if used % 100 == 0:
            print(f"  чанков {used}, токенов {n_tok:,} ({time.time()-t0:.0f}s)", flush=True)

    if args.exclude_unk:
        unk_c = int(counts[0]); counts[0] = 0
        print(f"[UNK]=0 исключён (частота была {unk_c:,} = {100*unk_c/max(n_tok,1):.2f}%)", flush=True)

    order = np.argsort(-counts)[:args.top_n]
    order = order[counts[order] > 0]
    top_ids = [int(x) for x in order]
    out = {'chunk': f'{lo}-{hi}', 'top_n': len(top_ids),
           'min_count': int(counts[order].min()), 'max_count': int(counts[order].max()),
           'n_tokens_total': int(n_tok), 'exclude_unk': bool(args.exclude_unk),
           'top_ids': top_ids}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(args.output, 'w'), ensure_ascii=False)
    print(f"\nтоп-{len(top_ids)}: max_count={out['max_count']:,} min_count={out['min_count']:,}", flush=True)
    print(f"первые 10 id: {top_ids[:10]}", flush=True)
    print(f"→ {args.output} ({time.time()-t0:.0f}s)", flush=True)


def smoke():
    import tempfile
    d = Path(tempfile.mkdtemp())
    np.save(d / 'chunk_000000.npy', np.array([0, 0, 5, 5, 5, 7, 7, 9], np.int32))
    o = d / 'top.json'
    sys.argv = ['x', '--npy-dir', str(d), '--chunks', '0-0', '--output', str(o),
                '--top-n', '3', '--vocab', '20']
    main()
    r = json.load(open(o))
    assert 0 not in r['top_ids'], "UNK не исключён"
    assert r['top_ids'][0] == 5, "порядок по частоте неверен"
    print("SMOKE OK")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--smoke':
        smoke()
    else:
        ast.parse(Path(__file__).read_text(encoding='utf-8')); main()
