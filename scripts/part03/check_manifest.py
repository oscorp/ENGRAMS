# -*- coding: utf-8 -*-
"""
check_manifest.py — сверить собранные фрагменты корпуса с манифестом (часть 3).

Запуск из корня репозитория:
    python scripts/part03/check_manifest.py
    python scripts/part03/check_manifest.py --chunks-dir data/corpus/chunks_584 --limit 5

По умолчанию сверяет data/corpus/chunks_584/ (туда пишет download_wiki_ru.py)
с data/corpus/corpus_manifest_v3.json: размер и md5 каждого файла.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def md5(path, block=1 << 20):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(block), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chunks-dir', default=str(ROOT / 'data/corpus/chunks_584'))
    ap.add_argument('--manifest', default=str(ROOT / 'data/corpus/corpus_manifest_v3.json'))
    ap.add_argument('--limit', type=int, default=None, help='проверить только первые N файлов')
    a, _ = ap.parse_known_args()
    man = json.loads(Path(a.manifest).read_text(encoding='utf-8'))['files']
    if a.limit:
        man = man[:a.limit]
    ok = missing = bad = 0
    for e in man:
        p = Path(a.chunks_dir) / e['file']
        if not p.exists():
            missing += 1
            continue
        if p.stat().st_size == e['bytes'] and md5(p) == e['md5']:
            ok += 1
        else:
            bad += 1
            print(f"✗ {e['file']}: не совпадает с манифестом")
    print(f"совпало {ok}, не совпало {bad}, нет файла {missing} (из {len(man)})")
    return 0 if bad == 0 and missing == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
