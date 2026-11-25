# -*- coding: utf-8 -*-
"""
select_tasks.py — выбор рабочих задач серии из набора data/tasks (часть 2).

Правило отбора (как в замерах чемпиона, --n-limit 300 --target-filter top_lemmas.json):
  1) из 3000 задач оставить те, чья цель входит в 1000 самых частых лемм корпуса;
  2) взять первые N из оставшихся (по умолчанию 300).
Если указан словарь лемм (lemma2id.json, публикуется в части 4), печатается разрез
целей на смысловые и служебные слова — тем же правилом, что в скрипте замера.

Запуск (Jupyter, одна ячейка):
    %run /path/to/engrams/scripts/part02/select_tasks.py --n 300
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# список служебных слов — дословно из скрипта замера чемпиона
FUNC_WORDS = set("""
в на с из к по за под над о об от до для при про через без между у во со ко
и а но или либо да же ли бы б не ни то что чтобы как когда где куда пока если хотя
я ты он она оно мы вы они себя свой мой твой наш ваш этот тот такой который какой
весь всякий каждый сам самый другой иной один
быть мочь стать являться бывать
уже ещё еще тоже также лишь только даже вот именно почти просто разве
""".split())


def is_content(lemma: str) -> bool:
    if not lemma:
        return False
    if not any(ch.isalnum() for ch in lemma):   # знак препинания
        return False
    return lemma.lower() not in FUNC_WORDS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tasks', default=str(ROOT / 'data/tasks/chunk_000002_tasks_3000.json'))
    ap.add_argument('--top', default=str(ROOT / 'data/tasks/top_lemmas_1000.json'))
    ap.add_argument('--n', type=int, default=300)
    ap.add_argument('--lemma2id', default='', help='словарь лемм (часть 4), для разреза целей')
    a, _ = ap.parse_known_args()

    d = json.loads(Path(a.tasks).read_text(encoding='utf-8'))
    top = set(json.loads(Path(a.top).read_text(encoding='utf-8'))['top_ids'])
    tasks = d['tasks']
    valid = [t for t in tasks if t['target'] in top]
    sel = valid[:a.n]
    print(f"задач в наборе: {len(tasks)}; цель в топ-1000: {len(valid)}; выбрано: {len(sel)}")
    print(f"номера выбранных задач: {sel[0]['id']} … {sel[-1]['id']}")

    if a.lemma2id:
        l2i = json.loads(Path(a.lemma2id).read_text(encoding='utf-8'))
        i2l = {v: k for k, v in l2i.items()}
        n_c = sum(1 for t in sel if is_content(i2l.get(t['target'], '')))
        print(f"смысловые цели: {n_c}; служебные: {len(sel) - n_c}")
        t = sel[0]
        print('пример:', ' '.join(i2l.get(x, '?') for x in t['context']), '=>', i2l.get(t['target']))


if __name__ == '__main__':
    main()
