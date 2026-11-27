# -*- coding: utf-8 -*-
"""
common_v3.py — ОБЩИЙ модуль ENGRAMS v3.

Здесь живут ЕДИНСТВЕННЫЕ реализации:
  - pack_morph() / unpack_morph()  — упаковка морфологии в uint16
  - split_by_punct()               — нарезка потока на отрезки между знаками препинания

🔴 ТЗ §1.3/§1.4: функция нарезки ОБЩАЯ для fit_delta_F_v3 и fit_features_v3.
   Ни один из них не должен реализовывать нарезку у себя — только импорт отсюда.
   Иначе ΔF_R и ΔF_R_features разъедутся по длине.

⚠️ uint16, НЕ int16: по конвенции ТЗ POS занимает биты 13–15, а 7<<13 = 57344 > 32767
   (максимум int16) → переполнение. Конвенция битов не меняется, меняется только dtype.
"""
from __future__ import annotations
import numpy as np

MORPH_DTYPE = np.uint16
LEMMA_DTYPE = np.int32

# ─────────────────────────────────────────────────────────────
# КОНВЕНЦИЯ БИТОВ (ТЗ §1.2). 0 = «признака НЕТ».
# ─────────────────────────────────────────────────────────────
MORPH_LAYOUT = {
    # признак: (сдвиг, число бит)
    "gender": (0, 2),
    "number": (2, 2),
    "case":   (4, 3),
    "tense":  (7, 2),
    "person": (9, 2),
    "aspect": (11, 2),
    "pos":    (13, 3),
}

# Признаки, по которым считается СОГЛАСОВАНИЕ (§1.4). POS — не признак согласования.
AGREEMENT_FEATURES = ["gender", "number", "case", "tense", "person", "aspect"]

# Число значимых (ненулевых) значений — для расчёта уровня случайности
FEATURE_CARDINALITY = {
    "gender": 3,   # Masc/Fem/Neut  → случайный уровень ≈ 1/3
    "number": 2,   # Sing/Plur      → ≈ 1/2
    "case":   6,   # Nom..Loc       → ≈ 1/6
    "tense":  3,   # Pres/Past/Fut  → ≈ 1/3
    "person": 3,   # 1/2/3          → ≈ 1/3
    "aspect": 2,   # Imp/Perf       → ≈ 1/2
}

GENDER_MAP = {"Masc": 1, "Fem": 2, "Neut": 3}
NUMBER_MAP = {"Sing": 1, "Plur": 2}
CASE_MAP   = {"Nom": 1, "Gen": 2, "Dat": 3, "Acc": 4, "Ins": 5, "Loc": 6}
TENSE_MAP  = {"Pres": 1, "Past": 2, "Fut": 3}
PERSON_MAP = {"First": 1, "Second": 2, "Third": 3}
ASPECT_MAP = {"Imp": 1, "Perf": 2}
POS_MAP = {
    "NOUN": 1, "PROPN": 1,
    "VERB": 2, "AUX": 2,
    "ADJ": 3,
    "ADV": 4,
    "PRON": 5, "DET": 5,
    "ADP": 6,
}
POS_OTHER = 7  # союзы, частицы, пунктуация, числа, X — «прочее»


def _first(morph, key, table):
    """token.morph.get('Gender') → ['Fem'] → 2. Пусто/неизвестно → 0."""
    vals = morph.get(key)
    if not vals:
        return 0
    return table.get(vals[0], 0)


def pack_morph(token) -> int:
    """spaCy Token → uint16 по конвенции §1.2."""
    m = token.morph
    code = 0
    code |= _first(m, "Gender", GENDER_MAP) << 0
    code |= _first(m, "Number", NUMBER_MAP) << 2
    code |= _first(m, "Case",   CASE_MAP)   << 4
    code |= _first(m, "Tense",  TENSE_MAP)  << 7
    code |= _first(m, "Person", PERSON_MAP) << 9
    code |= _first(m, "Aspect", ASPECT_MAP) << 11
    code |= POS_MAP.get(token.pos_, POS_OTHER) << 13
    return code


def unpack_morph(code):
    """uint16 (скаляр или np.ndarray) → dict признак → значение."""
    out = {}
    for name, (shift, nbits) in MORPH_LAYOUT.items():
        mask = (1 << nbits) - 1
        out[name] = (code >> shift) & mask
    return out


def get_feature(code, name):
    """Векторно-безопасное извлечение одного признака."""
    shift, nbits = MORPH_LAYOUT[name]
    return (code >> shift) & ((1 << nbits) - 1)


# ─────────────────────────────────────────────────────────────
# РАЗДЕЛИТЕЛИ ОТРЕЗКОВ (ТЗ §1.3, ответ Олега №4: ; и : включены)
# ─────────────────────────────────────────────────────────────
SEPARATOR_CHARS = [
    ".", "!", "?", "…",   # границы предложений
    ",", ";", ":",        # клаузальные границы (; и : — по решению Олега)
    "—", "–",             # тире
    "(", ")", "[", "]",   # скобки
    "«", "»", '"',        # кавычки
]

# Режимы обращения со знаком препинания (см. вопрос №6):
#   'drop'  — знак выбрасывается (псевдокод §1.3)
#   'close' — знак = последний токен своего отрезка
#   'hinge' — знак = последний токен предыдущего И первый токен следующего  [ПО УМОЛЧАНИЮ]
PUNCT_MODE_DEFAULT = "hinge"

MIN_SEGMENT_LEN = 2


def build_separator_ids(lemma2id) -> set:
    """id разделителей по словарю. Отсутствующие в словаре — молча пропускаются."""
    return {lemma2id[c] for c in SEPARATOR_CHARS if c in lemma2id}


def split_by_punct(tokens, sep_ids, mode=PUNCT_MODE_DEFAULT,
                   min_len=MIN_SEGMENT_LEN, return_index=False):
    """
    🔴 ЕДИНСТВЕННАЯ функция нарезки. Импортируется и fit_delta_F_v3, и fit_features_v3.

    tokens : 1-D array id лемм (весь чанк)
    sep_ids: set id разделителей
    mode   : 'drop' | 'close' | 'hinge'

    Возвращает список отрезков.
      return_index=False → список списков ID токенов
      return_index=True  → список списков ПОЗИЦИЙ в исходном потоке
                           (нужно fit_features_v3, чтобы взять morph по тем же координатам)

    Отрезки короче min_len отбрасываются.
    """
    segments = []
    cur = []          # позиции в исходном потоке
    for pos, t in enumerate(tokens):
        t = int(t)
        if t in sep_ids:
            if mode == "drop":
                pass
            elif mode == "close":
                cur.append(pos)
            elif mode == "hinge":
                cur.append(pos)
            else:
                raise ValueError(f"Неизвестный punct-mode: {mode}")

            if len(cur) >= min_len:
                segments.append(cur)
            # шарнир: знак открывает следующий отрезок
            cur = [pos] if mode == "hinge" else []
        else:
            cur.append(pos)

    if len(cur) >= min_len:
        segments.append(cur)

    if return_index:
        return segments
    return [[int(tokens[p]) for p in seg] for seg in segments]


def segment_stats(tokens, sep_ids, mode=PUNCT_MODE_DEFAULT, max_dist=30):
    """Статистика нарезки: сколько отрезков, длины, сколько пар на каждый ранг."""
    segs = split_by_punct(tokens, sep_ids, mode, return_index=True)
    lens = np.array([len(s) for s in segs], dtype=np.int64) if segs else np.zeros(0, np.int64)
    pairs = np.zeros(max_dist + 1, dtype=np.int64)
    for L in lens:
        for R in range(1, min(max_dist + 1, L)):
            pairs[R] += L - R
    return {
        "n_tokens":   int(len(tokens)),
        "n_segments": int(len(segs)),
        "len_mean":   float(lens.mean()) if len(lens) else 0.0,
        "len_median": float(np.median(lens)) if len(lens) else 0.0,
        "len_max":    int(lens.max()) if len(lens) else 0,
        "pairs_per_R": pairs.tolist(),
        "pairs_total": int(pairs.sum()),
    }
