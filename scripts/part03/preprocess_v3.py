# -*- coding: utf-8 -*-
"""
preprocess_v3.py — рецепт подготовки текста для токенизатора v3 (часть 3).

Рецепт заморожен: любая правка сдвигает позиции в потоке лемм, а с ними
окна памяти и задачи части 2. Менять его можно только вместе с полной
пересборкой и под новым именем версии.

Порядок шагов (как в сборке v3):
  1) неразрывный пробел U+00A0 → обычный пробел;
  2) знак ударения U+0301 удаляется («Компью́тер» → «Компьютер»);
  3) слипшиеся слова разлепляются: строчная буква + заглавная → «… …»;
  4) символы вне базовой плоскости Юникода (BMP, код ≥ 0x10000) удаляются;
  5) текст обрабатывается построчно, строки, начинающиеся с «#», пропускаются
     (это заголовки статей «### Заголовок ###»).

Запуск (Jupyter):
    %run scripts/part03/preprocess_v3.py --demo
    %run scripts/part03/preprocess_v3.py --in chunk_000002.txt --out chunk_000002.prep.txt
"""
import argparse
import re

_GLUED = re.compile(r'([а-яёa-z])([А-ЯЁA-Z])')


def preprocess(text: str) -> str:
    """Шаги 1–4 рецепта для одной строки."""
    text = text.replace('\xa0', ' ')
    text = text.replace('́', '')
    text = _GLUED.sub(r'\1 \2', text)
    text = ''.join(c for c in text if ord(c) < 0x10000)
    return text


def iter_lines(path):
    """Шаг 5: построчно, без строк, начинающихся с '#'."""
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            yield preprocess(line.rstrip('\n'))


DEMO = [
    'Компью́тер\xa0— устройство',     # ударение и неразрывный пробел
    'в 1946 годуПервый электронный',        # слипшиеся слова
    'знак \U00017000 вне BMP',              # символ вне BMP
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src')
    ap.add_argument('--out')
    ap.add_argument('--demo', action='store_true')
    a = ap.parse_args()
    if a.demo or not a.src:
        for s in DEMO:
            print(repr(s), '→', repr(preprocess(s)))
        return
    n = 0
    with open(a.out, 'w', encoding='utf-8') as g:
        for line in iter_lines(a.src):
            g.write(line + '\n'); n += 1
    print(n, 'строк →', a.out)


if __name__ == '__main__':
    main()
