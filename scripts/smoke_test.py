# -*- coding: utf-8 -*-
"""
smoke_test.py — проверка, что конвейер частей 3–4 работает в свежем клоне.

Запуск из корня репозитория (после pip install -r requirements.txt и
python -m spacy download ru_core_news_lg):
    python scripts/smoke_test.py

Что делает (всё на маленьком примере data/sample/ruwiki_sample.xml, без интернета,
результат в data/work/smoke/, эта папка в git не входит):
  1. часть 3: download_wiki_ru.py разбирает пример дампа и режет его на фрагменты;
  2. часть 3: preprocess_v3.py --demo показывает шаги рецепта;
  3. часть 4: build_streams_v3.py строит три синхронных потока с опубликованным словарём;
  4. часть 4: build_top_lemmas_v3.py считает самые частые объекты;
  5. поток переводится обратно в слова словарём data/tokenizer_v3/lemma2id.json;
  6. часть 4: lemma_tokenizer_v3.py на примере должен ОТКАЗАТЬСЯ сохранять словарь:
     в трёх статьях нет всех служебных слов, срабатывает проверка из раздела 5 статьи.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / 'data/work/smoke'


def run(args, expect=0):
    print('\n$ python ' + ' '.join(str(a) for a in args), flush=True)
    r = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT)
    if r.returncode != expect:
        raise SystemExit(f'✗ код возврата {r.returncode}, ожидался {expect}')
    return r


def main():
    if W.exists():
        shutil.rmtree(W)
    (W / 'wiki_dump').mkdir(parents=True)
    shutil.copy(ROOT / 'data/sample/ruwiki_sample.xml', W / 'wiki_dump/ruwiki-dump.xml')

    run(['scripts/part03/download_wiki_ru.py', '--output-dir', W / 'wiki_dump', '--chunks-dir', W / 'chunks'])
    chunks = sorted((W / 'chunks').glob('chunk_*.txt'))
    assert chunks, 'нет фрагментов'
    print(chunks[0].read_text(encoding='utf-8')[:400])

    run(['scripts/part03/preprocess_v3.py', '--demo'])

    run(['scripts/part04/build_streams_v3.py', '--chunks-dir', W / 'chunks', '--out-root', W / 'streams',
         '--report-dir', W / 'reports', '--workers', 1])
    run(['scripts/part04/build_top_lemmas_v3.py', '--npy-dir', W / 'streams/lemmas_npy_v3',
         '--chunks', '0-0', '--output', W / 'top.json', '--top-n', 10])

    l2i = json.loads((ROOT / 'data/tokenizer_v3/lemma2id.json').read_text(encoding='utf-8'))
    i2l = {v: k for k, v in l2i.items()}
    ids = np.load(W / 'streams/lemmas_npy_v3/chunk_000000.npy')
    morph = np.load(W / 'streams/morph_npy_v3/chunk_000000.npy')
    assert len(ids) == len(morph), 'потоки не синхронны'
    print(f'\nпоток фрагмента 0: {len(ids)} объектов, [UNK]: {(ids == 0).sum()}')
    print(' '.join(i2l[int(i)] for i in ids))

    run(['scripts/part04/lemma_tokenizer_v3.py', '--text-folder', W / 'chunks', '--output-dir', W / 'tokenizer',
         '--report-dir', W / 'reports', '--workers', 1], expect=1)
    print('\n✓ проверка пройдена: конвейер работает; словарь на маленьком примере '
          'не сохранён, как и должно быть (нет всех служебных слов).')


if __name__ == '__main__':
    main()
