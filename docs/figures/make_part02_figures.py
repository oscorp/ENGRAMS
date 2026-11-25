# -*- coding: utf-8 -*-
"""
make_part02_figures.py — рисунки части 2 («Как мы меряем»).

Запуск (Jupyter, одна ячейка):
    %run /path/to/engrams/docs/figures/make_part02_figures.py
или из терминала:
    python docs/figures/make_part02_figures.py [--out docs/figures] [--lang ru en]

Пишет docs/figures/<lang>/p2_fig01..p2_fig04 (.png).
Рис. 1 — настоящая задача №9 из набора chunk_000002_windows_test_3000.
Рис. 4 — числа чемпиона (300 задач, README чемпиона).
Нужны numpy и matplotlib.
"""
import argparse
from math import comb
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

SURF = '#fcfcfb'; INK = '#0b0b0b'; INK2 = '#52514e'; MUTED = '#9a9893'
GRID = '#e6e5e1'; BLUE = '#2a78d6'; ORANGE = '#eb6834'; AQUA = '#1baf7a'
BLUE_L = '#cfe0f6'; ORANGE_L = '#fad6c6'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': INK,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2,
    'ytick.color': INK2, 'axes.facecolor': SURF, 'figure.facecolor': SURF,
    'savefig.facecolor': SURF, 'axes.spines.top': False, 'axes.spines.right': False,
    'figure.dpi': 100,
})

# задача №9 набора (леммы v3; числа в v3 выброшены из потока, [UNK] — лемма вне словаря)
TASK9 = ('область , а также четыре округ [UNK] район ( урюпинский сельский округ , '
         '[UNK] аульный округ , [UNK] сельский округ , [UNK] городской администрация ) . '
         'в указать граница пригородный').split()
TARGET9 = 'зона'
assert len(TASK9) == 30

T = {
 'ru': {
  'f1_title': 'Задача: по 30 предыдущим леммам предсказать следующую (задача №9 набора)',
  'f1_ctx': 'контекст: 30 лемм; голубые — последние 15, которые видят ранговые матрицы', 'f1_tgt': 'цель', 'f1_q': '?',
  'f1_foot': 'Леммы русской Википедии, фрагмент 2. «[UNK]» — редкая лемма вне словаря. '
             'Числа в этой версии токенизатора выброшены из потока.',
  'f2_title': 'Режимы замера: leak и gen на одной ленте корпуса',
  'f2_leak': 'leak: окно задачи есть в памяти — основа решений',
  'f2_gen': 'gen: окрестность ±30 лемм вырезана — контроль переносимости',
  'f2_task': 'задача', 'f2_cut': 'вырезано ±30', 'f2_mem': 'память окон (фрагменты 2 и 3)',
  'f2_zero': 'радиус 0 — не leak: собственное окно уже выброшено',
  'f3_title': 'Сколько стоит одна задача и когда разница значима',
  'f3_a': 'цена одной задачи = 100/N пунктов', 'f3_ax': 'число задач N', 'f3_ay': 'пунктов',
  'f3_thr': 'порог шума: 2 задачи',
  'f3_b': 'знаковый тест: выиграно k, проиграно 0', 'f3_bx': 'k (выиграно задач)',
  'f3_by': 'p (двусторонний)', 'f3_bonf': 'Бонферрони, 4 варианта: 0,0125',
  'f3_sw': 'переключатель:\n+10/−0, p = 0,002',
  'f4_title': 'Общая точность и точность на смысловых словах (чемпион, 300 задач)',
  'f4_heads': ['воспоминание\n(n-граммы)', 'композиция\n(вектор G, β = 32)', 'облака\n(β = 32)', 'слияние'],
  'f4_all': 'все 300 задач', 'f4_con': 'смысловые слова (144)', 'f4_y': 'точность первого места, %',
  'f4_leak': 'leak', 'f4_gen': 'gen',
 },
 'en': {
  'f1_title': 'The task: predict the next lemma from the 30 before it (task no. 9 of the set)',
  'f1_ctx': 'context: 30 lemmas; the last 15 (blue) are the ones the rank matrices see', 'f1_tgt': 'target', 'f1_q': '?',
  'f1_foot': 'Lemmas of Russian Wikipedia, fragment 2. "[UNK]" is a rare lemma outside the vocabulary. '
             'Numbers are dropped from the stream in this tokenizer version.',
  'f2_title': 'Measurement modes: leak and gen on one strip of the corpus',
  'f2_leak': 'leak: the task window is in memory — the basis for decisions',
  'f2_gen': 'gen: a ±30-lemma neighbourhood is cut out — a transfer check',
  'f2_task': 'task', 'f2_cut': 'cut ±30', 'f2_mem': 'window memory (fragments 2 and 3)',
  'f2_zero': 'radius 0 is not leak: the task’s own window is already excluded',
  'f3_title': 'What one task is worth, and when a difference is significant',
  'f3_a': 'value of one task = 100/N points', 'f3_ax': 'number of tasks N', 'f3_ay': 'points',
  'f3_thr': 'noise threshold: 2 tasks',
  'f3_b': 'sign test: k won, 0 lost', 'f3_bx': 'k (tasks won)',
  'f3_by': 'p (two-sided)', 'f3_bonf': 'Bonferroni, 4 variants: 0.0125',
  'f3_sw': 'switching:\n+10/−0, p = 0.002',
  'f4_title': 'Overall accuracy and accuracy on content words (champion, 300 tasks)',
  'f4_heads': ['recall\n(n-grams)', 'composition\n(vector G, β = 32)', 'clouds\n(β = 32)', 'fusion'],
  'f4_all': 'all 300 tasks', 'f4_con': 'content words (144)', 'f4_y': 'top-1 accuracy, %',
  'f4_leak': 'leak', 'f4_gen': 'gen',
 },
}


def num(x, lang, fmt='{:.2f}'):
    s = fmt.format(x)
    return s.replace('.', ',') if lang == 'ru' else s


def save(fig, out, name):
    fig.savefig(out / f'{name}.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


def fig01(t, out, lang):
    fig, ax = plt.subplots(figsize=(12.5, 3.6))
    ax.set_xlim(0, 16); ax.set_ylim(0.55, 3.3); ax.axis('off')
    w = 15.0 / 16
    for i, tok in enumerate(TASK9):
        row, col = divmod(i, 16)
        x = col * w + 0.2; y = 2.2 - row * 1.0
        far = i < 15
        fc = BLUE_L if not far else '#eceae4'
        ax.add_patch(FancyBboxPatch((x, y), w - 0.08, 0.62, boxstyle='round,pad=0.02,rounding_size=0.06',
                                    fc=fc, ec='none'))
        ax.text(x + (w - 0.08) / 2, y + 0.31, tok, ha='center', va='center',
                fontsize=5.6 if len(tok) > 10 else (6.6 if len(tok) > 7 else 8.4), color=INK)
    # цель
    x = 14 * w + 0.2; y = 1.2
    ax.add_patch(FancyBboxPatch((x, y), w * 2 - 0.08, 0.62, boxstyle='round,pad=0.02,rounding_size=0.06',
                                fc=ORANGE_L, ec=ORANGE, lw=1.4))
    ax.text(x + w - 0.04, y + 0.31, f'{t["f1_q"]}  →  {TARGET9}', ha='center', va='center',
            fontsize=10, color=ORANGE, weight='bold')
    ax.text(0.2, 3.05, t['f1_ctx'], color=INK2, fontsize=10)
    ax.text(x + w - 0.04, 1.95, t['f1_tgt'], color=ORANGE, fontsize=10, ha='center')
    ax.text(0.2, 0.75, t['f1_foot'], color=MUTED, fontsize=8.5)
    ax.set_title(t['f1_title'], loc='left', fontsize=12.5, pad=6)
    save(fig, out, 'p2_fig01_task')


def fig02(t, out, lang):
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 4.2))
    rng = np.random.default_rng(3)
    for ax, mode in zip(axes, ['leak', 'gen']):
        ax.set_xlim(0, 200); ax.set_ylim(0, 1.6); ax.axis('off')
        for x0 in range(0, 200, 2):
            c = BLUE_L if rng.random() > 0.15 else '#dfe9f7'
            ax.add_patch(Rectangle((x0, 0.35), 1.8, 0.55, fc=c, ec='none'))
        p = 120
        if mode == 'gen':
            ax.add_patch(Rectangle((p - 30, 0.3), 60, 0.65, fc=SURF, ec=ORANGE, lw=1.2, ls='--'))
            ax.text(p + 16, 0.62, t['f2_cut'], ha='center', va='center', color=ORANGE, fontsize=9.5)
        ax.add_patch(Rectangle((p - 30, 0.35), 30, 0.55, fc='none', ec=INK, lw=1.4))
        ax.add_patch(Rectangle((p, 0.35), 2, 0.55, fc=ORANGE, ec='none'))
        ax.text(p - 15, 1.05, t['f2_task'], ha='center', color=INK, fontsize=9.5)
        ax.text(0, 1.38, t['f2_leak'] if mode == 'leak' else t['f2_gen'], fontsize=11,
                color=BLUE if mode == 'leak' else ORANGE, weight='bold')
        ax.text(200, 0.12, t['f2_mem'], ha='right', fontsize=8.5, color=MUTED)
    axes[1].text(0, 0.05, t['f2_zero'], fontsize=8.8, color=INK2)
    fig.suptitle(t['f2_title'], x=0.02, ha='left', fontsize=12.5)
    save(fig, out, 'p2_fig02_leak_gen')


def sign_p(k):
    # двусторонний знаковый тест при k выигрышах и 0 проигрышах
    return min(1.0, 2 * 0.5 ** k)


def fig03(t, out, lang):
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2))
    Ns = [150, 300, 3000]
    xx = np.arange(len(Ns)); w = 0.36
    v1 = [100 / n for n in Ns]; v2 = [200 / n for n in Ns]
    b1 = a.bar(xx - w / 2, v1, w, color=BLUE, label=t['f3_a'])
    b2 = a.bar(xx + w / 2, v2, w, color=ORANGE, label=t['f3_thr'])
    for bars in (b1, b2):
        for bb in bars:
            h = bb.get_height()
            a.text(bb.get_x() + bb.get_width() / 2, h + 0.03, num(h, lang), ha='center', fontsize=9.5)
    a.set_xticks(xx); a.set_xticklabels([str(n) for n in Ns])
    a.legend(frameon=False, fontsize=9, loc='upper right')
    a.set_xlabel(t['f3_ax']); a.set_ylabel(t['f3_ay'])
    a.set_ylim(0, 1.6)
    ks = np.arange(1, 13)
    ps = [sign_p(k) for k in ks]
    b.semilogy(ks, ps, 'o-', color=BLUE, ms=5)
    b.axhline(0.05, color=MUTED, lw=1, ls=':'); b.text(12, 0.058, 'p = 0,05' if lang == 'ru' else 'p = 0.05', ha='right', color=MUTED, fontsize=9)
    b.axhline(0.0125, color=ORANGE, lw=1.2, ls='--'); b.text(12, 0.0175, t['f3_bonf'], ha='right', color=ORANGE, fontsize=9)
    b.plot([10], [sign_p(10)], 'o', color=AQUA, ms=9)
    b.annotate(t['f3_sw'], (10, sign_p(10)), xytext=(6.2, 0.00025), color=AQUA, fontsize=9.5,
               arrowprops=dict(arrowstyle='->', color=AQUA))
    b.set_title(t['f3_b'], loc='left', fontsize=11); b.set_xlabel(t['f3_bx']); b.set_ylabel(t['f3_by'])
    fig.suptitle(t['f3_title'], x=0.02, ha='left', fontsize=12.5)
    fig.tight_layout()
    save(fig, out, 'p2_fig03_noise')


# числа чемпиона: leak все / leak смысловые / gen все / gen смысловые
CHAMP = {
    'ngram': (94.00, 92.36, 33.67, 25.69),
    'sfwd': (92.00, 100.00, 26.00, 27.78),
    'cloud': (89.67, 97.92, 23.67, 25.69),
    'fused': (92.33, 97.22, 34.00, 31.25),
}


def fig04(t, out, lang):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4), sharey=True)
    keys = ['ngram', 'sfwd', 'cloud', 'fused']
    x = np.arange(len(keys)); w = 0.36
    for ax, mode, off in zip(axes, [t['f4_leak'], t['f4_gen']], [0, 2]):
        va = [CHAMP[k][off] for k in keys]; vc = [CHAMP[k][off + 1] for k in keys]
        b1 = ax.bar(x - w / 2, va, w, color=BLUE, label=t['f4_all'])
        b2 = ax.bar(x + w / 2, vc, w, color=AQUA, label=t['f4_con'])
        for bars in (b1, b2):
            for bb in bars:
                h = bb.get_height()
                ax.text(bb.get_x() + bb.get_width() / 2, h + 1.2, num(h, lang), ha='center', fontsize=8.3)
        ax.set_xticks(x); ax.set_xticklabels(t['f4_heads'], fontsize=9)
        ax.set_title(mode, loc='left', fontsize=11.5)
        ax.set_ylim(0, 112)
    axes[0].set_ylabel(t['f4_y'])
    axes[1].legend(frameon=False, loc='upper right', fontsize=9.5)
    fig.suptitle(t['f4_title'], x=0.02, ha='left', fontsize=12.5)
    fig.tight_layout()
    save(fig, out, 'p2_fig04_content')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(Path(__file__).resolve().parent))
    ap.add_argument('--lang', nargs='+', default=['ru', 'en'])
    a, _ = ap.parse_known_args()
    for lang in a.lang:
        out = Path(a.out) / lang
        out.mkdir(parents=True, exist_ok=True)
        t = T[lang]
        fig01(t, out, lang); fig02(t, out, lang); fig03(t, out, lang); fig04(t, out, lang)
        print('готово:', out)


if __name__ == '__main__':
    main()
