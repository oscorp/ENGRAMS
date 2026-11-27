# -*- coding: utf-8 -*-
"""
fetch_data.py — скачать большие данные серии с Hugging Face прямо на их места в клоне.

Датасет: https://huggingface.co/datasets/Os2003/engrams-ruwiki-v3
Его папки повторяют устройство репозитория, поэтому файлы ложатся туда,
где их ждут скрипты частей 3–4.

Запуск из корня репозитория:
    python scripts/fetch_data.py                  # корпус и потоки (≈ 19,7 ГБ)
    python scripts/fetch_data.py --what corpus    # только 584 фрагмента (11,4 ГиБ) → data/corpus/chunks_584/
    python scripts/fetch_data.py --what streams   # только потоки v3 → data/streams_v3/
    python scripts/fetch_data.py --what corpus --chunks 0-9   # первые 10 фрагментов

После скачивания корпуса: python scripts/part03/check_manifest.py
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Os2003/engrams-ruwiki-v3'


def patterns(what, chunks):
    if chunks:
        a, b = (chunks.split('-') + [chunks])[:2]
        ids = [f'{i:06d}' for i in range(int(a), int(b) + 1)]
    else:
        ids = ['*']
    out = []
    if what in ('corpus', 'all'):
        out += [f'data/corpus/chunks_584/chunk_{i}.txt' for i in ids]
    if what in ('streams', 'all'):
        out += [f'data/streams_v3/lemmas_npy_v3/chunk_{i}.npy' for i in ids]
        out += [f'data/streams_v3/morph_npy_v3/chunk_{i}.npy' for i in ids]
        out += [f'data/streams_v3/spans_v3/sent_spans_chunk_{i}.pkl' for i in ids]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--what', choices=['corpus', 'streams', 'all'], default='all')
    ap.add_argument('--chunks', default='', help='диапазон фрагментов, например 0-9; по умолчанию все 584')
    a, _ = ap.parse_known_args()
    from huggingface_hub import snapshot_download
    snapshot_download(repo_id=REPO, repo_type='dataset', local_dir=str(ROOT),
                      allow_patterns=patterns(a.what, a.chunks))
    print('готово: файлы в', ROOT / 'data')


if __name__ == '__main__':
    main()
