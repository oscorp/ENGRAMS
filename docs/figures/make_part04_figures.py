# -*- coding: utf-8 -*-
"""
make_part04_figures.py — рисунки части 4 («Леммы как объекты»).

Запуск (Jupyter, одна ячейка):
    %run /path/to/engrams/docs/figures/make_part04_figures.py
или: python docs/figures/make_part04_figures.py [--out docs/figures] [--lang ru en]

Рис. 1 — путь токена: правило v3 на примере предложения (схема; номера взяты
         из data/tokenizer_v3/lemma2id.json, леммы показаны такими, какими их
         даёт правило; это иллюстрация, а не вывод программы).
Рис. 2 — из чего состоит поток: настоящие частоты первой тысячи объектов
         из data/tokenizer_v3/lemma_stats.json и итоги отчёта о сборке.
Рис. 3 — v2 против v3 на том же предложении (схема).
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
BLUE_L = '#cfe0f6'; ORANGE_L = '#fad6c6'; AQUA_L = '#c9eedf'; GREY_L = '#ecebe8'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': INK,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2,
    'ytick.color': INK2, 'axes.facecolor': SURF, 'figure.facecolor': SURF,
    'savefig.facecolor': SURF, 'axes.spines.top': False, 'axes.spines.right': False,
})

TOTAL = 1_080_086_644      # объектов в потоке v3 (отчёт о сборке)
UNK = 55_371_230           # позиций [UNK] (5,13 %)

# Пример: «Население Шишкосвятова и Кукуева составляло 12 человек.»
# (текст, ветка, лемма) ветка: a = буквенный, p = знак/в словаре, x = выброшен
EXAMPLE = [('Население', 'a', 'население'), ('Шишкосвятова', 'a', 'шишкосвятов'),
           ('и', 'a', 'и'), ('Кукуева', 'a', 'кукуев'), ('составляло', 'a', 'составлять'),
           ('12', 'x', None), ('человек', 'a', 'человек'), ('.', 'p', '.')]

T = {
 'ru': {
  'f1_title': 'Как строка становится номерами: одно правило на каждый токен',
  'f1_rows': ['токен spaCy', 'ветка правила', 'лемма', 'номер в потоке'],
  'br': {'a': 'буквенный →\nлемма', 'p': 'знак →\nсам текст', 'x': 'ни то\nни другое →\nвыброшен'},
  'gone': 'нет в потоке', 'unk': '[UNK] = 0\n(вне словаря)',
  'f1_foot': 'Правило из build_streams_v3.py: 1) буквенный токен → лемма в нижнем регистре;\n2) иначе знак препинания или текст из словаря → сам текст; '
             '3) иначе токен выброшен — так выпадают числа;\n4) лемма вне словаря → [UNK]. Номера — из lemma2id.json; предложение — пример.',
  'f2_title': 'Из чего состоит поток: 1 080 086 644 объекта',
  'f2_x': 'ранг объекта (по убыванию частоты)', 'f2_y': 'вхождений в потоке',
  'f2_p': 'знаки препинания', 'f2_w': 'леммы',
  'f2_bar': ['знаки препинания\nв первой тысяче', 'леммы\nпервой тысячи', 'остальные\n~99 000 ячеек', '[UNK]'],
  'f2_bt': 'доля потока',
  'f2_foot': 'Частоты первой тысячи — data/tokenizer_v3/lemma_stats.json (настоящие данные). Остальные ячейки и [UNK] — по итогам отчёта о сборке:\n'
             'всего 1 080 086 644 объекта, [UNK] 55 371 230.',
  'f3_title': 'v2 против v3 на одном предложении',
  'f3_rows': ['текст', 'v2', 'v3'],
  'f3_note2': 'v2: «и» нет в словаре (фильтр len > 1), редкие слова выброшены → «население» и «составлять» стали соседями (расстояние 1)',
  'f3_note3': 'v3: «и» на месте, редкие слова занимают позицию как [UNK] → расстояние 4, как в тексте',
  'f3_num': 'число «12» выпадает в обеих версиях',
  'dist': 'расстояние',
 },
 'en': {
  'f1_title': 'How a line becomes numbers: one rule per token',
  'f1_rows': ['spaCy token', 'rule branch', 'lemma', 'id in the stream'],
  'br': {'a': 'alphabetic →\nlemma', 'p': 'mark →\nthe text', 'x': 'neither →\ndropped'},
  'gone': 'not in stream', 'unk': '[UNK] = 0\n(out of vocab)',
  'f1_foot': 'The rule from build_streams_v3.py: 1) alphabetic token → lower-case lemma; 2) else a punctuation mark or a text in the vocabulary → the text itself;\n'
             '3) else the token is dropped — this is how numbers disappear; 4) a lemma outside the vocabulary → [UNK].\nIds from lemma2id.json; the sentence is an example.',
  'f2_title': 'What the stream is made of: 1,080,086,644 objects',
  'f2_x': 'object rank (by decreasing frequency)', 'f2_y': 'occurrences in the stream',
  'f2_p': 'punctuation marks', 'f2_w': 'lemmas',
  'f2_bar': ['punctuation in\nthe top 1000', 'lemmas of\nthe top 1000', 'the other\n~99,000 entries', '[UNK]'],
  'f2_bt': 'share of the stream',
  'f2_foot': 'Top-1000 frequencies: data/tokenizer_v3/lemma_stats.json (real data). The other entries and [UNK]: totals from the build report:\n'
             '1,080,086,644 objects in all, 55,371,230 [UNK].',
  'f3_title': 'v2 versus v3 on one sentence',
  'f3_rows': ['text', 'v2', 'v3'],
  'f3_note2': 'v2: «и» (and) is not in the vocabulary (len > 1 filter), rare words dropped → «население» (population) and «составлять» (amount to) became neighbours (distance 1)',
  'f3_note3': 'v3: «и» kept, rare words hold their place as [UNK] → distance 4, as in the text',
  'f3_num': 'the number «12» drops out in both versions',
  'dist': 'distance',
 },
}


def load_vocab():
    l2i = json.load(open(ROOT / 'data/tokenizer_v3/lemma2id.json', encoding='utf-8'))
    stats = json.load(open(ROOT / 'data/tokenizer_v3/lemma_stats.json', encoding='utf-8'))
    return l2i, stats


def box(ax, x, y, w, h, text, fc, ec, fs=10, color=INK, weight='normal'):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.08',
                                fc=fc, ec=ec, lw=1))
    ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=color, weight=weight)


def fig1(t, l2i, out):
    n = len(EXAMPLE)
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    ax.set_xlim(-2.1, n - 0.4); ax.set_ylim(-0.9, 4.2); ax.axis('off')
    ys = [3.5, 2.35, 1.2, 0.2]
    for y, lab in zip(ys, t['f1_rows']):
        ax.text(-1.85, y, lab, ha='left', va='center', fontsize=10, color=INK2)
    for i, (tok, br, lem) in enumerate(EXAMPLE):
        box(ax, i, ys[0], 0.92, 0.5, tok, GREY_L, GRID, fs=9.5 if len(tok) < 11 else 8)
        fc = {'a': BLUE_L, 'p': AQUA_L, 'x': ORANGE_L}[br]
        box(ax, i, ys[1], 0.92, 0.8, t['br'][br], fc, GRID, fs=7.8, color=INK2)
        ax.annotate('', (i, ys[1] + 0.42), (i, ys[0] - 0.27), arrowprops=dict(arrowstyle='->', color=MUTED, lw=0.8))
        if br == 'x':
            ax.text(i, ys[2], t['gone'], ha='center', va='center', fontsize=8.5, color=ORANGE, style='italic')
            continue
        ax.annotate('', (i, ys[2] + 0.27), (i, ys[1] - 0.42), arrowprops=dict(arrowstyle='->', color=MUTED, lw=0.8))
        box(ax, i, ys[2], 0.92, 0.5, lem, SURF, GRID, fs=9 if len(lem) < 11 else 7.6)
        idx = l2i.get(lem)
        if idx is None:
            box(ax, i, ys[3], 0.92, 0.6, t['unk'], ORANGE_L, ORANGE, fs=7.8, color=INK)
        else:
            box(ax, i, ys[3], 0.92, 0.5, f'{idx:,}'.replace(',', ' '), SURF, BLUE, fs=9.5, color=BLUE, weight='bold')
        ax.annotate('', (i, ys[3] + 0.3), (i, ys[2] - 0.27), arrowprops=dict(arrowstyle='->', color=MUTED, lw=0.8))
    ax.set_title(t['f1_title'], loc='left', fontsize=13, weight='bold')
    fig.text(0.012, 0.015, t['f1_foot'], fontsize=8, color=INK2, ha='left', va='bottom')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.17)
    fig.savefig(out / 'p4_fig01_token_path.png', dpi=150)
    plt.close(fig)


def fig2(t, stats, out):
    top = stats['top_lemmas']
    freqs = np.array([x['freq'] for x in top], dtype=float)
    is_p = np.array([x['id'] >= 99946 for x in top])
    ranks = np.arange(1, len(top) + 1)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={'width_ratios': [1.25, 1]})
    ax.loglog(ranks, freqs, color=GRID, lw=1, zorder=1)
    ax.scatter(ranks[~is_p], freqs[~is_p], s=7, color=BLUE, label=t['f2_w'], zorder=2)
    ax.scatter(ranks[is_p], freqs[is_p], s=26, color=ORANGE, label=t['f2_p'], zorder=3)
    for i in range(6):
        ax.annotate(top[i]['lemma'], (ranks[i], freqs[i]), xytext=(6, 2), textcoords='offset points', fontsize=9, color=INK2)
    ax.set_xlabel(t['f2_x']); ax.set_ylabel(t['f2_y'])
    ax.grid(True, which='major', color=GRID, lw=0.6)
    ax.legend(frameon=False, loc='lower left')
    p_share = freqs[is_p].sum() / TOTAL
    w_share = freqs[~is_p].sum() / TOTAL
    unk_share = UNK / TOTAL
    rest = 1 - p_share - w_share - unk_share
    vals = [p_share, w_share, rest, unk_share]
    cols = [ORANGE, BLUE, BLUE_L, MUTED]
    left = 0
    for v, c, lab in zip(vals, cols, t['f2_bar']):
        bx.barh(0, v * 100, left=left * 100, color=c, height=0.5)
        bx.text((left + v / 2) * 100, 0.42 if v > 0.1 else -0.42, f'{lab}\n{v * 100:.1f} %'.replace('.', ',') if t is T['ru'] else f'{lab}\n{v * 100:.1f} %',
                ha='center', va='bottom' if v > 0.1 else 'top', fontsize=9, color=INK)
        left += v
    bx.set_xlim(0, 100); bx.set_ylim(-1.3, 1.3); bx.set_yticks([])
    bx.set_xlabel(t['f2_bt'] + ', %')
    bx.spines['left'].set_visible(False)
    fig.suptitle(t['f2_title'], x=0.01, ha='left', fontsize=13, weight='bold')
    fig.text(0.01, 0.01, t['f2_foot'], fontsize=8, color=INK2, ha='left', va='bottom')
    fig.subplots_adjust(left=0.07, right=0.98, top=0.88, bottom=0.2, wspace=0.12)
    fig.savefig(out / 'p4_fig02_stream.png', dpi=150)
    plt.close(fig)


def fig3(t, l2i, out):
    text = [w for w, _, _ in EXAMPLE]
    # v2: числа и всё вне словаря выброшены; «и» в словаре v2 нет (фильтр len > 1)
    v2 = []
    for w, br, lem in EXAMPLE:
        if br == 'x' or lem not in l2i or lem == 'и':
            v2.append(None)
        else:
            v2.append(lem)
    v3 = []
    for w, br, lem in EXAMPLE:
        v3.append(None if br == 'x' else (lem if lem in l2i else '[UNK]'))
    fig, ax = plt.subplots(figsize=(11.5, 5.0))
    ax.axis('off'); ax.set_xlim(-1.2, 9.2); ax.set_ylim(-1.75, 3.3)
    # строка текста
    for i, w in enumerate(text):
        box(ax, i, 2.8, 0.95, 0.45, w, GREY_L, GRID, fs=9 if len(w) < 11 else 7.8)
    ax.text(-1.15, 2.8, t['f3_rows'][0], va='center', fontsize=10, color=INK2)

    def stream(row, y, label):
        ax.text(-1.15, y, label, va='center', fontsize=10, color=INK2, weight='bold')
        k = 0; pos = {}
        for i, lem in enumerate(row):
            if lem is None:
                continue
            x = k * 1.0 + 0.0
            fc = ORANGE_L if lem == '[UNK]' else (SURF)
            box(ax, x, y, 0.95, 0.45, lem, fc, BLUE if lem in ('население', 'составлять') else GRID,
                fs=8.6 if len(lem) < 11 else 7.4)
            pos[lem] = k; k += 1
        return pos
    p2 = stream(v2, 1.35, t['f3_rows'][1])
    p3 = stream(v3, -0.1, t['f3_rows'][2])
    for p, y in ((p2, 1.35), (p3, -0.1)):
        a, b = p['население'], p['составлять']
        ax.annotate('', (b, y - 0.33), (a, y - 0.33),
                    arrowprops=dict(arrowstyle='<->', color=BLUE, lw=1.2, shrinkA=0, shrinkB=0))
        ax.text((a + b) / 2, y - 0.5, f"{t['dist']} {b - a}", ha='center', va='top', fontsize=9, color=BLUE)
    ax.text(-1.15, -1.0, t['f3_note2'], fontsize=8.6, color=INK2)
    ax.text(-1.15, -1.3, t['f3_note3'], fontsize=8.6, color=INK2)
    ax.text(-1.15, -1.6, t['f3_num'], fontsize=8.6, color=INK2)
    ax.set_title(t['f3_title'], loc='left', fontsize=13, weight='bold')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.04)
    fig.savefig(out / 'p4_fig03_v2_v3.png', dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT / 'docs/figures'))
    ap.add_argument('--lang', nargs='+', default=['ru', 'en'])
    args, _ = ap.parse_known_args()
    l2i, stats = load_vocab()
    for lang in args.lang:
        out = Path(args.out) / lang
        out.mkdir(parents=True, exist_ok=True)
        t = T[lang]
        fig1(t, l2i, out); fig2(t, stats, out); fig3(t, l2i, out)
        print('готово / done:', out)


if __name__ == '__main__':
    main()
