# -*- coding: utf-8 -*-
"""
make_part03_figures.py — рисунки части 3 («Корпус»).

Запуск (Jupyter, одна ячейка):
    %run /path/to/engrams/docs/figures/make_part03_figures.py
или: python docs/figures/make_part03_figures.py [--out docs/figures] [--lang ru en]

Рис. 1 — шаги рецепта подготовки на примерах строк (иллюстрация, не корпус).
Рис. 2 — размеры 584 фрагментов по манифесту data/corpus/corpus_manifest_v3.json.
Рис. 3 — схема: одна правка рецепта сдвигает позиции в потоке.
Нужны numpy и matplotlib.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
SURF = '#fcfcfb'; INK = '#0b0b0b'; INK2 = '#52514e'; MUTED = '#9a9893'
GRID = '#e6e5e1'; BLUE = '#2a78d6'; ORANGE = '#eb6834'; AQUA = '#1baf7a'
BLUE_L = '#cfe0f6'; ORANGE_L = '#fad6c6'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': INK,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2,
    'ytick.color': INK2, 'axes.facecolor': SURF, 'figure.facecolor': SURF,
    'savefig.facecolor': SURF, 'axes.spines.top': False, 'axes.spines.right': False,
})

T = {
 'ru': {
  'f1_title': 'Рецепт подготовки: пять шагов (примеры строк)',
  'steps': [('1. неразрывный пробел → пробел', 'Компьютер␣—␣устройство', 'Компьютер — устройство'),
            ('2. знак ударения удаляется', 'Компью́тер', 'Компьютер'),
            ('3. слипшиеся слова разлепляются', 'годуПервый', 'году Первый'),
            ('4. символы вне BMP удаляются', 'знак [U+17000] вне', 'знак  вне'),
            ('5. строки с «#» пропускаются', '### Компьютер ###', '(строка пропущена)')],
  'f1_foot': '␣ — неразрывный пробел U+00A0. Без шага 2 «Компью́тер» не считается словом и уходит в [UNK]; '
             'без шага 4 такой символ ронял морфологический анализатор.',
  'f2_title': '584 фрагмента корпуса: объём и число статей',
  'f2_a': 'объём фрагментов почти одинаков: медиана {med:.2f} млн байт,\nпоследний — {last:.2f} млн; число статей меняется в 27 раз', 'f2_b': 'статей во фрагменте', 'f2_x': 'номер фрагмента',
  'f2_foot': 'По манифесту data/corpus/corpus_manifest_v3.json. Статьи посчитаны по строкам «### Заголовок ###».',
  'f3_title': 'Почему рецепт заморожен: одна правка сдвигает координаты',
  'f3_old': 'рецепт v3', 'f3_new': 'без шага 3', 'f3_pos': 'позиция в потоке',
  'f3_note': 'правка меняет число объектов в строке → все позиции правее сдвигаются → окна памяти\n'
             'и задачи части 2 указывают уже на другие слова',
  'f3_ex_old': ['в', 'году', 'первый', 'электронный', 'компьютер', 'был', 'построен'],
  'f3_ex_new': ['в', 'годупервый', 'электронный', 'компьютер', 'был', 'построен', '…'],
  'f3_ins': '«годуПервый» — один объект вместо двух',
 },
 'en': {
  'f1_title': 'Text preparation recipe: five steps (example strings)',
  'steps': [('1. no-break space → space', 'Компьютер␣—␣устройство', 'Компьютер — устройство'),
            ('2. stress mark removed', 'Компью́тер', 'Компьютер'),
            ('3. glued words split', 'годуПервый', 'году Первый'),
            ('4. non-BMP characters removed', 'знак [U+17000] вне', 'знак  вне'),
            ('5. lines starting with "#" skipped', '### Компьютер ###', '(line skipped)')],
  'f1_foot': '␣ is the no-break space U+00A0. Without step 2 «Компью́тер» (computer) is not a word and becomes [UNK]; '
             'without step 4 such a character crashed the morphological analyser.',
  'f2_title': 'The 584 corpus fragments: size and number of articles',
  'f2_a': 'fragment sizes are nearly equal: median {med:.2f} million bytes,\nthe last one {last:.2f} million; article counts vary 27-fold', 'f2_b': 'articles per fragment', 'f2_x': 'fragment number',
  'f2_foot': 'From the manifest data/corpus/corpus_manifest_v3.json. Articles counted by lines "### Title ###".',
  'f3_title': 'Why the recipe is frozen: one change shifts the coordinates',
  'f3_old': 'recipe v3', 'f3_new': 'without step 3', 'f3_pos': 'position in the stream',
  'f3_note': 'a change alters the number of objects in a line → every position to the right shifts → memory windows\n'
             'and the part 2 tasks now point at different words',
  'f3_ex_old': ['в', 'году', 'первый', 'электронный', 'компьютер', 'был', 'построен'],
  'f3_ex_new': ['в', 'годупервый', 'электронный', 'компьютер', 'был', 'построен', '…'],
  'f3_ins': '«годуПервый» is one object instead of two',
 },
}


def fig1(t, out):
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 11); ax.set_ylim(0, 6.2); ax.axis('off')
    ax.text(0.1, 5.9, t['f1_title'], fontsize=14, weight='bold', va='top')
    for i, (lab, a, b) in enumerate(t['steps']):
        y = 4.9 - i * 0.92
        ax.text(0.1, y, lab, fontsize=11, color=INK2, va='center')
        for x0, s, fc in ((4.3, a, ORANGE_L), (7.75, b, BLUE_L)):
            ax.add_patch(FancyBboxPatch((x0, y - 0.3), 3.05, 0.6, boxstyle='round,pad=0.02,rounding_size=0.08',
                                        fc=fc, ec='none'))
            ax.text(x0 + 0.12, y, s, fontsize=11.5, va='center', family='DejaVu Sans')
        ax.annotate('', xy=(7.7, y), xytext=(7.4, y), arrowprops=dict(arrowstyle='->', color=INK2, lw=1.2))
    ax.text(0.1, 0.12, t['f1_foot'], fontsize=9, color=INK2, wrap=True)
    fig.savefig(out, dpi=160, bbox_inches='tight'); plt.close(fig)


def fig2(t, out, man):
    files = man['files']
    mb = np.array([f['bytes'] for f in files]) / 1e6
    art = np.array([f['articles'] for f in files])
    x = np.arange(len(files))
    fig, a2 = plt.subplots(figsize=(11, 4.4))
    fig.suptitle(t['f2_title'], fontsize=14, weight='bold', x=0.01, ha='left')
    a2.bar(x, art, width=1.0, color=ORANGE, lw=0); a2.set_ylabel(t['f2_b']); a2.set_xlabel(t['f2_x'])
    a2.grid(axis='y', color=GRID, lw=0.8); a2.set_axisbelow(True); a2.set_xlim(-1, len(files)); a2.set_ylim(0, art.max() * 1.25)
    a2.text(0.01, 0.97, t['f2_a'].format(med=np.median(mb), last=mb[-1]), transform=a2.transAxes,
            va='top', fontsize=10, color=INK2,
            bbox=dict(boxstyle='round,pad=0.4', fc=SURF, ec=GRID))
    fig.text(0.01, -0.01, t['f2_foot'], fontsize=9, color=INK2)
    fig.tight_layout(); fig.savefig(out, dpi=160, bbox_inches='tight'); plt.close(fig)


def fig3(t, out):
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_xlim(-2.6, 8.6); ax.set_ylim(-1.9, 3.1); ax.axis('off')
    ax.text(-2.2, 3.0, t['f3_title'], fontsize=14, weight='bold', va='top')
    for row, (lab, words, y) in enumerate(((t['f3_old'], t['f3_ex_old'], 1.6), (t['f3_new'], t['f3_ex_new'], 0.4))):
        ax.text(-2.5, y, lab, fontsize=11, color=INK2, va='center')
        for i, w in enumerate(words):
            X = i * 1.25
            fc = BLUE_L if (row == 0 or i == 0) else ORANGE_L
            if row == 1 and i == 1:
                fc = ORANGE
            ax.add_patch(FancyBboxPatch((X - 0.58, y - 0.3), 1.16, 0.6, boxstyle='round,pad=0.02,rounding_size=0.08',
                                        fc=fc, ec='none'))
            ax.text(X, y, w, ha='center', va='center', fontsize=9.5,
                    color='white' if (row == 1 and i == 1) else INK)
    for i in range(7):
        ax.text(i * 1.25, 2.15, str(1000 + i), ha='center', fontsize=9, color=MUTED)
    ax.text(3 * 1.25, 2.55, t['f3_pos'], ha='center', fontsize=9.5, color=MUTED)
    ax.annotate(t['f3_ins'], xy=(1.25, 0.05), xytext=(1.25, -0.8), ha='center', fontsize=9.5, color=ORANGE,
                arrowprops=dict(arrowstyle='->', color=ORANGE))
    ax.text(-2.5, -1.75, t['f3_note'], fontsize=9.5, color=INK2)
    fig.savefig(out, dpi=160, bbox_inches='tight'); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT / 'docs/figures'))
    ap.add_argument('--lang', nargs='+', default=['ru', 'en'])
    a, _ = ap.parse_known_args()
    man = json.loads((ROOT / 'data/corpus/corpus_manifest_v3.json').read_text(encoding='utf-8'))
    for lang in a.lang:
        d = Path(a.out) / lang; d.mkdir(parents=True, exist_ok=True)
        t = T[lang]
        fig1(t, d / 'p3_fig01_recipe.png')
        fig2(t, d / 'p3_fig02_fragments.png', man)
        fig3(t, d / 'p3_fig03_coordinates.png')
        print('→', d)


if __name__ == '__main__':
    main()
