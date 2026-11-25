# ENGRAMS project rules

*The working rules under which every number in the series was obtained. Each one appeared after a specific mistake; where it is instructive, the mistake is given. Russian version: [RULES.ru.md](RULES.ru.md). The measurement rules are discussed in part 2 of the series.*

## Rule 0. Zero is not a small number

In strict mode there is no substitution for zero: no `+ EPS`, `+ 1e-10`, `max(x, tiny)`, `or 1.0`, `x[x == 0] = 1` or the like.

> **Zero means there is no Hebbian link, not that the link is small.** Replacing zero turns "no link" into "a weak link" and creates false joint activations. Both the set of candidates and their order change.

| situation | forbidden | instead |
|---|---|---|
| zero under a logarithm | `log(x + EPS)` | the coordinate does not take part: −∞ on the log scale |
| zero in a denominator | `x / (y + EPS)`, `y or 1.0` | the element is excluded, a counter goes to the log |
| zero frequency or weight | `w / (f + EPS)` | the element does not exist and is dropped |
| zero vector norm | `norm or 1.0` | the vector is excluded from candidates, a counter goes to the log |
| "just in case" safeguard | any | remove it; if the branch is unreachable, prove it and delete it |

Non-strict mode (part 1) is a separate research decision: it is switched on explicitly, its numbers are labelled, and it is never mixed with strict measurements.

Check before running any script:

```python
tree = ast.parse(src)
names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
assert 'EPS' not in names, 'rule 0 violated'
# and by eye: 1e-6, 1e-10, 1e-12, `or 1.0`, `[... == 0] = 1`
```

## Rule 1. Leak is the base, gen is the control

The window memory is the trained model, so leakage is the working mode, not an artefact. Every measurement contains both modes, leak first.

| mode | flag | meaning | role |
|---|---|---|---|
| **leak** | `--excl-radius -1` | the task's window is in memory | the base; decisions are made on it |
| **gen** | `--excl-radius 30` | a ±30 neighbourhood is cut out | transferability control |

Radius 0 is not leak: the filter `|window start − task position| > radius` is strict, so at 0 the task's own window is already excluded.

**Every number in a report carries its mode.** A number without a mode is invalid. *Why:* once a series of measurements taken on gen without a label gave 24 % against the reference 68 % (taken on leak), and this was mistaken for a degradation of the mechanism. On leak the same mechanism gave 92–100 %.

## Rule 2. Two modes of operation and a marker between them

The model can recall (an exact match of the context, the continuation head) and compose (composition via the G vector and clouds). The switching marker is the depth of the context match with the corpus. It must be defined on every task and printed in the report alongside the metrics.

## Rule 3. Memory and query are built by the same rules

The G formula lives in two places: in building the window memory and in processing the query. Change it only in both at once. The measurement script prints the G mode of the query and the mode from the memory's `meta.json` and confirms they match. The same holds for the window step, context length, rank limit and minimum context.

## Rule 4. Self-documentation

Every script puts a copy of itself and a `meta.json` into the folder of the data it creates. Opening the folder shows at once what built the data. If several runs write to the folder, a `YYYYMMDD_HHMM` stamp is added to the copy's name. The copy is part of the data: it is moved and deleted only together with it and is never edited after the fact. A mistake found later is described in `meta.json` and in the report.

## Rule 5. Compare like with like

One memory, one task set, one context length, one normalisation, one mode. Numbers from different task sets are never compared. *Why:* once the blend was measured on 1164 tasks and the switch on 582; the difference of 24.40 vs 25.26 turned out to be an artefact of the different sets.

## Rule 6. The criterion is declared before the measurement

Before the run, write down what counts as success, in points, and why this threshold is above noise. One task is worth 100/N points; a gain of less than two tasks cannot be told apart from noise. The best of several variants is chosen by a sign test over the tasks where they differ, with a Bonferroni correction for the number of variants.

## Rule 7. Facts first, then interpretation

First the numbers as they are ("74.31 vs 70.14"), then the interpretation, separately. A cause that was not established is written as such: "cause not established".

## Rule 8. Do not breed knobs

A parameter is added only if it is going to be measured now. A knob that decides nothing is removed together with its plumbing. *Example:* the number of windows at output (5, 10, 25) at the working β gave 100.00 / 100.00 / 99.31, so the knob was removed.

## Rule 9. Nothing is deleted irreversibly

A file's path: in place → quarantine (trash or external drive) → deleted, only on the author's explicit decision. When moving to an external drive: copy first, compare sizes, and only then send the original to the trash. The quarantine register records: path, size, date, why removed, what it affects, when it can be deleted for good, when to restore it. *Why:* once memory blanks (2.54 GB) were deleted bypassing the trash, and an interrupted run would have had to be recomputed, almost 20 hours.

### 9a. Rotation of intermediate results

For results that a re-run reproduces in minutes (probe output, temporary folders, logs), the current generation and one previous are kept. Streams, matrices, dictionaries, annotations and reports are never rotated. A rotating script prints what it deleted and touches only its own files by an exact name pattern.

## Rule 10. One step, one self-contained cell

All commands of a step go into one Jupyter cell: moving the script into the working folder, running it with full paths (each flag on its own line), and copying the script into the data folder if the script does not do it itself. If the next step depends on a number or error from the previous one, the chain is not handed out in full: first one step, the next one after its output has been read. *Why:* a chain of seven steps handed out at once would have failed overnight at step two on a non-existent flag.

## Rule 11. The environment is JupyterLab

Everything that runs is a ready notebook cell. Shell commands use `!`; Python goes in the cell body, not `!python -c` (otherwise quotes, indentation and Cyrillic get lost).

## Rule 12. Folder structure first

At the start of work the standard folders are created: `scripts`, `docs`, `reports`, `logs`, quarantine and subject folders. The tree creator is idempotent: it does not touch or overwrite what exists.

## Rule 13. Resume from where it stopped

Any pass longer than a minute can resume after an interruption (error, Ctrl-C, drive disconnect, laptop sleep, kernel crash):

1. work is split into units of minutes, not hours;
2. after each unit `progress.json` is written to disk;
3. the write is atomic: a temporary file, then `os.replace`;
4. `progress.json` stores a fingerprint of the arguments; on mismatch the script refuses to continue;
5. `--restart` starts over, and the previous output is not deleted but renamed with a timestamp;
6. at start it prints how much is done and how much remains; at the end, whether the run reached its end.
