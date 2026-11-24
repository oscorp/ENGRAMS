# -*- coding: utf-8 -*-
"""
make_part01_figures.py — рисунки и анимации части 1 (обзор ENGRAMS).

Запуск (Jupyter, одна ячейка):
    %run /path/to/engrams/docs/figures/make_part01_figures.py
или из терминала:
    python docs/figures/make_part01_figures.py [--out docs/figures] [--lang ru en]

Пишет docs/figures/<lang>/fig01..fig10 (.png, анимации .gif и .mp4).
Числа на рисунках 1, 6, 9 — из заявки (§5, §8.1, §8.5); остальные рисунки —
игрушечные примеры, это подписано на самих рисунках.
Нужны numpy и matplotlib; для .mp4 — ffmpeg (если его нет, пишется только .gif).
"""
import argparse
import shutil
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import FancyBboxPatch

# ---------------------------------------------------------------- стиль
SURF = '#fcfcfb'; INK = '#0b0b0b'; INK2 = '#52514e'; MUTED = '#9a9893'
GRID = '#e6e5e1'; BLUE = '#2a78d6'; ORANGE = '#eb6834'; AQUA = '#1baf7a'
BLUE_L = '#cfe0f6'; ORANGE_L = '#fad6c6'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': INK,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2,
    'ytick.color': INK2, 'axes.facecolor': SURF, 'figure.facecolor': SURF,
    'savefig.facecolor': SURF, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': False, 'figure.dpi': 100,
})

T = {
 'ru': {
  'f1_title': 'Две дороги к одной статистике',
  'f1_bp': 'Обратное распространение ошибки',
  'f1_bp_steps': ['корпус', 'случайные\nвеса', 'прямой\nпроход', 'ошибка', 'градиенты\n(много эпох)'],
  'f1_en': 'ENGRAMS',
  'f1_en_steps': ['корпус', 'подсчёт пар\nпо расстояниям', 'нормировка\nу кандидата', 'произведение\nстрок контекста', 'предсказание'],
  'f1_bp_note': 'построение: ~8·10¹⁷ операций за эпоху\nпредсказание: ~2,5·10⁸ операций',
  'f1_en_note': 'построение: ~6·10¹⁰ операций, один проход\nпредсказание: ~10⁴ операций',
  'f1_foot': 'Оценки из заявки для корпуса 1,1·10⁹ лемм; трансформер 125 млн параметров.',
  'f2_sent': ['кот', 'видеть', 'мышь', 'в', 'сад'],
  'f2_title': 'Обучение = подсчёт: окно идёт по тексту и пополняет ранговые матрицы',
  'f2_mat': 'ΔF{r}: пары на расстоянии {r}',
  'f2_rows': 'кто стоит раньше', 'f2_cols': 'кто стоит позже',
  'f3_title': 'Одна матрица — две памяти: B = Fᵀ',
  'f3_F': 'F₁: «кто идёт после»\n(строка = слово, столбец = следующее)',
  'f3_B': 'B₁ = F₁ᵀ: «кто идёт перед»\n(строка = слово, столбец = предыдущее)',
  'f4_title': 'Обострение весов по Ципфу: три способа',
  'f4_a': 'а) одна матрица:\nΣ w(d)·ΔF_d, w(d) = ((1+c)/(1+d))^z',
  'f4_b': 'б) ранговая матрица глубины r\n(чемпион: только d = r)',
  'f4_c': 'в) пик весов на глубине r\n(s = 0, z = 2), не исследовано',
  'f4_after': 'за пиком:\nсвязи «из будущего»',
  'f4_x': 'расстояние d', 'f4_y': 'вес',
  'f5_title': 'Строгий и нестрогий режим (игрушечный пример)',
  'f5_cands': ['дождь', 'зонт', 'лужа', 'гроза', 'туман', 'радуга'],
  'f5_strict': 'строгий: ноль = связи нет',
  'f5_eps': 'нестрогий: ноль → ε = 0,01',
  'f5_new': 'новое\nсочетание',
  'f5_y': 'вектор совместимости G\n(к максимуму)',
  'f6_title': 'Нормировка у кандидата превращает счётчики в PMI (пример §8.5 заявки)',
  'f6_M': 'M — счётчики', 'f6_A': 'A = M / сумма столбца', 'f6_E': 'A · N / сумма строки = e^PMI',
  'f6_note': 'клетка (0,1): e^PMI = 0,875, PMI = −0,134 < 0 — пара встречается реже, чем при независимости',
  'f7_title': 'Геометрическое среднее: согласованные активации растут, несогласованные гаснут',
  'f7_row': 'строка {k}-го слова контекста', 'f7_G': 'G после шага {k}: взвешенное среднее геометрическое (к максимуму)',
  'f7_dead': 'ноль в строке —\nкандидат выбыл',
  'f7_c': 'кандидаты (игрушечный пример)',
  'f8_title': 'Окно памяти: косинус облаков в степени β',
  'f8_x': 'косинус облака окна и облака запроса', 'f8_y': 'множитель cos^β',
  'f8_note': 'при β = 32: cos 0,90 → {a:.3f};  cos 0,98 → {b:.2f}',
  'f9_title': 'Точность по глубине совпадения контекста с корпусом (leak, §8.1 заявки)',
  'f9_rec': 'воспоминание (n-граммы)', 'f9_comp': 'композиция (облака, β = 32)',
  'f9_x': 'глубина совпадения', 'f9_y': 'точность первого места, %', 'f9_n': '{n} задач',
  'f10_title': 'Детектор корреляции по nnz: ожидаемое случайное совпадение = nnz₁·nnz₂',
  'f10_X': 'вектор 1: доля единиц 0,7', 'f10_Yr': 'вектор 2 (случайный): 0,3',
  'f10_Yc': 'вектор 2 (связанный): 0,3',
  'f10_r': 'совпало {k} из 100 — около ожидаемых 21: связи нет',
  'f10_c': 'совпало {k} из 100 — больше 21: корреляция',
 },
 'en': {
  'f1_title': 'Two roads to the same statistics',
  'f1_bp': 'Backpropagation',
  'f1_bp_steps': ['corpus', 'random\nweights', 'forward\npass', 'loss', 'gradients\n(many epochs)'],
  'f1_en': 'ENGRAMS',
  'f1_en_steps': ['corpus', 'count pairs\nby distance', 'normalize\nat the candidate', 'product of\ncontext rows', 'prediction'],
  'f1_bp_note': 'build: ~8·10¹⁷ operations per epoch\nprediction: ~2.5·10⁸ operations',
  'f1_en_note': 'build: ~6·10¹⁰ operations, one pass\nprediction: ~10⁴ operations',
  'f1_foot': 'Estimates from the patent application for a 1.1·10⁹-lemma corpus; 125M-parameter transformer.',
  'f2_sent': ['cat', 'see', 'mouse', 'in', 'garden'],
  'f2_title': 'Training = counting: a window walks the text and fills the rank matrices',
  'f2_mat': 'ΔF{r}: pairs at distance {r}',
  'f2_rows': 'earlier word', 'f2_cols': 'later word',
  'f3_title': 'One matrix, two memories: B = Fᵀ',
  'f3_F': 'F₁: "what comes after"\n(row = word, column = next word)',
  'f3_B': 'B₁ = F₁ᵀ: "what comes before"\n(row = word, column = previous word)',
  'f4_title': 'Sharpening the weights Zipf-style: three ways',
  'f4_a': 'a) one matrix:\nΣ w(d)·ΔF_d, w(d) = ((1+c)/(1+d))^z',
  'f4_b': 'b) rank matrix of depth r\n(champion: only d = r)',
  'f4_c': 'c) weight peak at depth r\n(s = 0, z = 2), not yet studied',
  'f4_after': 'past the peak:\nlinks "from the future"',
  'f4_x': 'distance d', 'f4_y': 'weight',
  'f5_title': 'Strict and non-strict mode (toy example)',
  'f5_cands': ['rain', 'umbrella', 'puddle', 'storm', 'fog', 'rainbow'],
  'f5_strict': 'strict: zero = no link',
  'f5_eps': 'non-strict: zero → ε = 0.01',
  'f5_new': 'new\ncombination',
  'f5_y': 'compatibility vector G\n(scaled to max)',
  'f6_title': 'Normalizing at the candidate turns counts into PMI (example §8.5 of the application)',
  'f6_M': 'M: counts', 'f6_A': 'A = M / column sum', 'f6_E': 'A · N / row sum = e^PMI',
  'f6_note': 'cell (0,1): e^PMI = 0.875, PMI = −0.134 < 0: the pair is rarer than under independence',
  'f7_title': 'Geometric mean: agreeing activations grow, disagreeing ones fade',
  'f7_row': 'row of context word {k}', 'f7_G': 'G after step {k}: weighted geometric mean (scaled to max)',
  'f7_dead': 'zero in the row:\ncandidate is out',
  'f7_c': 'candidates (toy example)',
  'f8_title': 'Memory window: cloud cosine raised to the power β',
  'f8_x': 'cosine of window cloud and query cloud', 'f8_y': 'factor cos^β',
  'f8_note': 'with β = 32: cos 0.90 → {a:.3f};  cos 0.98 → {b:.2f}',
  'f9_title': 'Accuracy by match depth of the context in the corpus (leak, §8.1)',
  'f9_rec': 'recall (n-grams)', 'f9_comp': 'composition (clouds, β = 32)',
  'f9_x': 'match depth', 'f9_y': 'top-1 accuracy, %', 'f9_n': '{n} tasks',
  'f10_title': 'nnz correlation detector: expected chance overlap = nnz₁·nnz₂',
  'f10_X': 'vector 1: share of ones 0.7', 'f10_Yr': 'vector 2 (random): 0.3',
  'f10_Yc': 'vector 2 (linked): 0.3',
  'f10_r': 'overlap {k} of 100, close to the expected 21: no link',
  'f10_c': 'overlap {k} of 100, above 21: correlation',
 },
}


def num(x, lang, fmt='{:.2f}'):
    s = fmt.format(x)
    return s.replace('.', ',') if lang == 'ru' else s


def save(fig, out, name):
    fig.savefig(out / f'{name}.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


def save_anim(anim, fig, out, name, fps):
    anim.save(out / f'{name}.gif', writer=animation.PillowWriter(fps=fps), dpi=110)
    if shutil.which('ffmpeg'):
        anim.save(out / f'{name}.mp4', writer=animation.FFMpegWriter(
            fps=fps, codec='libx264', extra_args=['-pix_fmt', 'yuv420p']), dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- 1
def fig01(t, out, lang):
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.2); ax.axis('off')
    ax.set_title(t['f1_title'], loc='left', fontsize=15, pad=12)
    for y, label, steps, col, light, note in (
            (3.6, t['f1_bp'], t['f1_bp_steps'], ORANGE, ORANGE_L, t['f1_bp_note']),
            (1.3, t['f1_en'], t['f1_en_steps'], BLUE, BLUE_L, t['f1_en_note'])):
        ax.text(0.1, y + 0.95, label, fontsize=13, weight='bold', color=INK)
        for i, s in enumerate(steps):
            x = 0.1 + i * 1.75
            ax.add_patch(FancyBboxPatch((x, y - 0.35), 1.45, 0.9,
                         boxstyle='round,pad=0.02,rounding_size=0.08', fc=light, ec=col, lw=1.2))
            ax.text(x + 0.725, y + 0.1, s, ha='center', va='center', fontsize=8.8)
            if i:
                ax.annotate('', (x, y + 0.1), (x - 0.3, y + 0.1),
                            arrowprops=dict(arrowstyle='->', color=INK2, lw=1.2))
        if col == ORANGE:  # петля обучения
            ax.annotate('', (1.85 + 0.72, y + 0.55), (7.1 + 0.72, y + 0.55),
                        arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.4,
                                        connectionstyle='arc3,rad=0.35'))
        ax.text(9.05, y + 0.1, note, va='center', fontsize=10, color=INK2)
    ax.text(0.1, 0.15, t['f1_foot'], fontsize=9, color=MUTED)
    save(fig, out, 'fig01_two_roads')


# ---------------------------------------------------------------- 2, 3
def counts_toy(n_tok, R):
    F = np.zeros((R, n_tok, n_tok), int); events = []
    for i in range(n_tok):
        for r in range(1, R + 1):
            if i + r < n_tok:
                F[r - 1, i, i + r] += 1
                events.append((i, r, i + r, F.copy()))
    return F, events


def draw_grid(ax, M, words, title, hl=None, cmap_col=BLUE):
    n = len(words)
    ax.set_xlim(-0.5, n - 0.5); ax.set_ylim(n - 0.5, -0.5)
    for i in range(n):
        for j in range(n):
            v = M[i, j]
            fc = cmap_col if v else SURF
            alpha = 0.85 if v else 1
            ax.add_patch(plt.Rectangle((j - 0.45, i - 0.45), 0.9, 0.9, fc=fc, alpha=alpha,
                                       ec=GRID, lw=0.8))
            if v:
                ax.text(j, i, str(v), ha='center', va='center', color='white', fontsize=10, weight='bold')
    if hl:
        i, j = hl
        ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fc='none', ec=ORANGE, lw=2.5))
    ax.set_xticks(range(n)); ax.set_xticklabels(words, rotation=45, ha='right', fontsize=9)
    ax.set_yticks(range(n)); ax.set_yticklabels(words, fontsize=9)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(title, fontsize=10.5, color=INK)


def fig02(t, out, lang):
    words = t['f2_sent']; n = len(words); R = 3
    F, events = counts_toy(n, R)
    fig = plt.figure(figsize=(12, 5.6))
    fig.suptitle(t['f2_title'], x=0.02, ha='left', fontsize=14)
    axs = fig.add_axes([0.03, 0.80, 0.94, 0.08])
    axm = [fig.add_axes([0.08 + k * 0.31, 0.08, 0.24, 0.55]) for k in range(R)]
    frames = [None] * 3 + events + [events[-1]] * 6

    def draw(ev):
        axs.clear(); axs.axis('off'); axs.set_xlim(-0.5, n - 0.5); axs.set_ylim(-1, 1)
        cur = F * 0 if ev is None else ev[3]
        for k, w in enumerate(words):
            on = ev is not None and k in (ev[0], ev[2])
            axs.add_patch(FancyBboxPatch((k - 0.42, -0.5), 0.84, 1.0, boxstyle='round,pad=0.02',
                          fc=(ORANGE_L if on else SURF), ec=(ORANGE if on else GRID), lw=1.5))
            axs.text(k, 0, w, ha='center', va='center', fontsize=13)
        if ev is not None:
            i, r, j, _ = ev
            axs.annotate('', (j, 0.62), (i, 0.62), arrowprops=dict(
                arrowstyle='->', color=ORANGE, lw=1.6, connectionstyle='arc3,rad=-0.35'))
            axs.text((i + j) / 2, 1.05, f'r = {r}', ha='center', color=ORANGE, fontsize=11)
        for r in range(R):
            axm[r].clear()
            hl = (ev[0], ev[2]) if ev is not None and ev[1] == r + 1 else None
            draw_grid(axm[r], cur[r], words, t['f2_mat'].format(r=r + 1), hl)
        axm[0].set_ylabel(t['f2_rows'], fontsize=9, color=INK2)
        axm[1].set_xlabel(t['f2_cols'], fontsize=9, color=INK2)
    anim = animation.FuncAnimation(fig, draw, frames=frames, interval=700)
    save_anim(anim, fig, out, 'fig02_counting', fps=1.4)
    # статичный кадр для печати
    fig = plt.figure(figsize=(12, 5.6)); fig.suptitle(t['f2_title'], x=0.02, ha='left', fontsize=14)
    axm = [fig.add_axes([0.08 + k * 0.31, 0.12, 0.24, 0.62]) for k in range(R)]
    for r in range(R):
        draw_grid(axm[r], F[r], words, t['f2_mat'].format(r=r + 1))
    save(fig, out, 'fig02_counting_final')
    return F


def fig03(t, out, lang, F):
    words = t['f2_sent']
    F1 = F[0]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 5))
    fig.suptitle(t['f3_title'], x=0.02, ha='left', fontsize=14)
    draw_grid(a, F1, words, t['f3_F'], hl=(1, 2))
    draw_grid(b, F1.T, words, t['f3_B'], hl=(2, 1), cmap_col=AQUA)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, out, 'fig03_transpose')


# ---------------------------------------------------------------- 4
def fig04(t, out, lang):
    d = np.arange(1, 16); c = 1; r = 5
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    fig.suptitle(t['f4_title'], x=0.02, ha='left', fontsize=14)
    w_a = ((1 + c) / (1 + d)) ** 2
    w_b = (d == r).astype(float)
    w_c = (1 / (1 + np.abs(d - r))) ** 2
    for ax, w, title in ((axs[0], w_a, t['f4_a']), (axs[1], w_b, t['f4_b']), (axs[2], w_c, t['f4_c'])):
        cols = [BLUE] * len(d)
        if ax is axs[2]:
            cols = [BLUE if x <= r else ORANGE for x in d]
            ax.axvspan(r + 0.5, 15.6, color=ORANGE_L, alpha=0.45, lw=0)
            ax.text(10.5, 0.78, t['f4_after'], ha='center', fontsize=9.5, color=INK2)
        ax.bar(d, w, width=0.7, color=cols)
        ax.set_title(title, fontsize=10.5, loc='left')
        ax.set_xticks([1, 5, 10, 15]); ax.set_xlabel(t['f4_x'])
        ax.axhline(0, color=GRID, lw=1)
        if ax is not axs[0]:
            ax.axvline(r, color=MUTED, lw=0.8, ls=':')
            ax.text(r, 1.04, 'r', ha='center', color=INK2)
    axs[0].set_ylabel(t['f4_y']); axs[0].set_ylim(0, 1.1)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, out, 'fig04_zipf_weights')


# ---------------------------------------------------------------- 5
def fig05(t, out, lang):
    rows = np.array([[0.30, 0.10, 0.20, 0.25, 0.00, 0.15],
                     [0.35, 0.20, 0.25, 0.00, 0.10, 0.10],
                     [0.25, 0.15, 0.30, 0.20, 0.10, 0.00]])
    eps = 0.01
    def gm(M):
        return np.exp(np.log(M).mean(0))
    strict = np.where((rows > 0).all(0), gm(np.where(rows > 0, rows, 1.0)), 0.0)
    loose = gm(np.where(rows > 0, rows, eps))
    strict /= strict.max(); loose /= loose.max()
    x = np.arange(rows.shape[1])
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.set_title(t['f5_title'], loc='left', fontsize=14)
    ax.bar(x - 0.19, strict, 0.36, color=BLUE, label=t['f5_strict'])
    ax.bar(x + 0.19, loose, 0.36, color=ORANGE, label=t['f5_eps'])
    for i in x:
        if strict[i] == 0 and loose[i] > 0:
            ax.annotate(t['f5_new'], (i + 0.19, loose[i]), (i + 0.19, loose[i] + 0.35),
                        ha='center', fontsize=9.5, color=INK2,
                        arrowprops=dict(arrowstyle='->', color=INK2))
            ax.text(i - 0.19, 0.02, '0', ha='center', color=INK2)
    ax.set_xticks(x); ax.set_xticklabels(t['f5_cands'])
    ax.set_ylabel(t['f5_y']); ax.set_ylim(0, 1.3); ax.legend(frameon=False, loc='upper right')
    save(fig, out, 'fig05_strict_vs_eps')


# ---------------------------------------------------------------- 6
def fig06(t, out, lang):
    M = np.array([[3, 1, 0], [0, 2, 2], [1, 1, 4]], float)
    C = M.sum(0); R = M.sum(1); N = M.sum()
    A = M / C
    E = A * N / R[:, None]
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.4))
    fig.suptitle(t['f6_title'], x=0.02, ha='left', fontsize=13)
    for ax, X, title, fmt in ((axs[0], M, t['f6_M'], '{:.0f}'), (axs[1], A, t['f6_A'], '{:.3f}'),
                             (axs[2], E, t['f6_E'], '{:.3f}')):
        ax.imshow(X / X.max(), cmap='Blues', vmin=0, vmax=1.25)
        for i in range(3):
            for j in range(3):
                v = X[i, j]
                ax.text(j, i, '·' if v == 0 else num(v, lang, fmt), ha='center', va='center',
                        color=(INK if X[i, j] / X.max() < 0.55 else 'white'), fontsize=12)
        ax.set_xticks(range(3)); ax.set_yticks(range(3)); ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(title, fontsize=11)
    axs[2].add_patch(plt.Rectangle((0.5, -0.5), 1, 1, fc='none', ec=ORANGE, lw=2.5))
    fig.text(0.02, 0.02, t['f6_note'], fontsize=10, color=INK2)
    fig.tight_layout(rect=(0, 0.06, 1, 0.9))
    save(fig, out, 'fig06_normalization_pmi')


# ---------------------------------------------------------------- 7
def a_of_n(n):
    return 3.895 / (n - 2.633) ** 0.941 if n >= 3 else 1.0


def fig07(t, out, lang):
    m, K = 4, 12
    # игрушечные строки 4 слов контекста по 12 кандидатам
    rows = np.array([
        [0.30, 0.25, 0.90, 0.40, 0.35, 0.50, 0.20, 0.85, 0.30, 1.00, 0.45, 0.30],
        [0.00, 0.30, 0.85, 0.45, 0.00, 0.40, 0.25, 0.90, 0.35, 0.05, 0.30, 0.20],
        [0.35, 0.20, 0.80, 0.35, 0.30, 0.45, 0.30, 0.95, 0.25, 0.60, 0.00, 0.35],
        [0.25, 0.35, 0.90, 0.40, 0.30, 0.00, 0.20, 0.80, 0.30, 0.05, 0.40, 0.25]])
    a = a_of_n(m)
    p = [1.0] + [a * (k - 1) + 1 for k in range(2, m + 1)]
    Gs = []
    for k in range(1, m + 1):
        # показатели e_i раскрытой рекурсии после k шагов; для показа берём
        # взвешенное среднее геометрическое exp(Σ e_i ln v_i / Σ e_i): порядок тот же, что у G
        e = np.array([np.prod([1 / p[j] for j in range(max(i, 1), k)]) for i in range(k)])
        sub = rows[:k]
        alive = (sub > 0).all(0)
        lg = np.where(sub > 0, np.log(np.where(sub > 0, sub, 1.0)), 0.0)
        Gs.append(np.where(alive, np.exp((e[:, None] * lg).sum(0) / e.sum()), 0.0))
    letters = [chr(ord('A') + i) for i in range(K)]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.2), sharex=True)
    fig.suptitle(t['f7_title'], x=0.02, ha='left', fontsize=13)
    frames = [0, 0] + [k for k in range(m) for _ in range(3)] + [m - 1] * 4

    def draw(k):
        a1.clear(); a2.clear()
        x = np.arange(K)
        a1.bar(x, rows[k], color=AQUA, width=0.7)
        a1.set_ylim(0, 1.1); a1.set_title(t['f7_row'].format(k=k + 1), loc='left', fontsize=11)
        for j in np.flatnonzero(rows[k] == 0):
            a1.text(j, 0.04, '0', ha='center', color=ORANGE, fontsize=12, weight='bold')
        G = Gs[k] / Gs[k].max()
        cols = [BLUE if g > 0 else GRID for g in G]
        a2.bar(x, G, color=cols, width=0.7)
        for j in np.flatnonzero(G == 0):
            a2.text(j, 0.04, '×', ha='center', color=MUTED, fontsize=14)
        a2.set_ylim(0, 1.15); a2.set_title(t['f7_G'].format(k=k + 1), loc='left', fontsize=11)
        a2.set_xticks(x); a2.set_xticklabels(letters); a2.set_xlabel(t['f7_c'])
        if k == m - 1:
            best = int(np.argmax(G))
            a2.annotate('argmax', (best, G[best]), (best + 1.4, 1.08), color=INK2,
                        arrowprops=dict(arrowstyle='->', color=INK2))
    anim = animation.FuncAnimation(fig, draw, frames=frames, interval=800)
    save_anim(anim, fig, out, 'fig07_geometric_mean', fps=1.25)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.2), sharex=True)
    fig.suptitle(t['f7_title'], x=0.02, ha='left', fontsize=13)
    a1_, a2_ = a1, a2                   # статичный кадр = последний кадр анимации
    x = np.arange(K)
    a1_.bar(x, rows[m - 1], color=AQUA, width=0.7); a1_.set_ylim(0, 1.1)
    a1_.set_title(t['f7_row'].format(k=m), loc='left', fontsize=11)
    G = Gs[-1] / Gs[-1].max()
    a2_.bar(x, G, color=[BLUE if g > 0 else GRID for g in G], width=0.7); a2_.set_ylim(0, 1.15)
    a2_.set_title(t['f7_G'].format(k=m), loc='left', fontsize=11)
    a2_.set_xticks(x); a2_.set_xticklabels(letters); a2_.set_xlabel(t['f7_c'])
    save(fig, out, 'fig07_geometric_mean_final')


# ---------------------------------------------------------------- 8
def fig08(t, out, lang):
    c = np.linspace(0, 1, 400)
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.set_title(t['f8_title'], loc='left', fontsize=14)
    for b, col in ((1, MUTED), (4, AQUA), (32, BLUE)):
        ax.plot(c, c ** b, color=col, lw=2)
        xl = 0.55 if b == 1 else (0.72 if b == 4 else 0.93)
        ax.text(xl - 0.02, xl ** b + 0.04, f'β = {b}', color=INK, fontsize=10, ha='right')
    ax.set_xlabel(t['f8_x']); ax.set_ylabel(t['f8_y']); ax.set_xlim(0, 1); ax.set_ylim(0, 1.05)
    ax.text(0.02, 0.9, t['f8_note'].format(a=0.9 ** 32, b=0.98 ** 32).replace(
        '.', ',') if lang == 'ru' else t['f8_note'].format(a=0.9 ** 32, b=0.98 ** 32),
        fontsize=10, color=INK2)
    save(fig, out, 'fig08_cloud_beta')


# ---------------------------------------------------------------- 9
def fig09(t, out, lang):
    depth = ['1', '2', '3', '≥ 4']; n = [10, 14, 6, 270]
    rec = [20.0, 50.0, 83.3, 99.3]; comp = [80.0, 64.3, 66.7, 94.4]
    x = np.arange(4)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.set_title(t['f9_title'], loc='left', fontsize=13)
    ax.bar(x - 0.19, rec, 0.36, color=ORANGE, label=t['f9_rec'])
    ax.bar(x + 0.19, comp, 0.36, color=BLUE, label=t['f9_comp'])
    for i in x:
        ax.text(i - 0.19, rec[i] + 1.5, num(rec[i], lang, '{:.1f}'), ha='center', fontsize=9, color=INK2)
        ax.text(i + 0.19, comp[i] + 1.5, num(comp[i], lang, '{:.1f}'), ha='center', fontsize=9, color=INK2)
    ax.set_xticks(x)
    ax.set_xticklabels([f'{d}\n' + t['f9_n'].format(n=k) for d, k in zip(depth, n)])
    ax.set_xlabel(t['f9_x']); ax.set_ylabel(t['f9_y']); ax.set_ylim(0, 125)
    ax.legend(frameon=False, loc='upper left', ncol=2)
    save(fig, out, 'fig09_depth')


# ---------------------------------------------------------------- 10
def fig10(t, out, lang):
    rng = np.random.default_rng(3)
    L = 100
    X = np.zeros(L, int); X[rng.choice(L, 70, replace=False)] = 1
    Yr = np.zeros(L, int); Yr[rng.choice(L, 30, replace=False)] = 1
    Yc = np.zeros(L, int); Yc[rng.choice(np.flatnonzero(X), 28, replace=False)] = 1
    Yc[rng.choice(np.flatnonzero(X == 0), 2, replace=False)] = 1
    fig, axs = plt.subplots(5, 1, figsize=(11, 4.8), gridspec_kw=dict(height_ratios=[1, 1, .55, 1, .55]))
    fig.suptitle(t['f10_title'], x=0.02, ha='left', fontsize=13)

    def strip(ax, v, col, label, ov=None):
        ax.imshow(v[None, :], aspect='auto', cmap=matplotlib.colors.ListedColormap([GRID, col]))
        if ov is not None:
            for j in np.flatnonzero(ov):
                ax.add_patch(plt.Rectangle((j - 0.5, -0.5), 1, 1, fc='none', ec=ORANGE, lw=1.2))
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_ylabel(label, rotation=0, ha='right', va='center', fontsize=9.5, color=INK2)
    strip(axs[0], X, BLUE, t['f10_X'])
    strip(axs[1], Yr, AQUA, t['f10_Yr'], X & Yr)
    axs[2].axis('off'); axs[2].text(0, 0.5, t['f10_r'].format(k=int((X & Yr).sum())), fontsize=10)
    strip(axs[3], Yc, AQUA, t['f10_Yc'], X & Yc)
    axs[4].axis('off'); axs[4].text(0, 0.5, t['f10_c'].format(k=int((X & Yc).sum())), fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, out, 'fig10_nnz_detector')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(Path(__file__).resolve().parent))
    ap.add_argument('--lang', nargs='+', default=['ru', 'en'])
    a, _ = ap.parse_known_args()
    for lang in a.lang:
        out = Path(a.out) / lang
        out.mkdir(parents=True, exist_ok=True)
        t = T[lang]
        fig01(t, out, lang)
        F = fig02(t, out, lang)
        fig03(t, out, lang, F)
        fig04(t, out, lang); fig05(t, out, lang); fig06(t, out, lang)
        fig07(t, out, lang); fig08(t, out, lang); fig09(t, out, lang); fig10(t, out, lang)
        print(lang, '→', out, sorted(p.name for p in out.iterdir()))


if __name__ == '__main__':
    main()
