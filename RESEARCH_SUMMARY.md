# Final research summary

## Strongest supported positive finding

With its relative-gap threshold selected on the original five exploratory
splits and committed before the evaluation, the one-or-two-reason rule showed
one headline reason in 69.2–75.6% of ordered fit-pair cases on all five fresh
splits. In those one-reason cases, agreement exceeded the all-case
single-reason baseline by 11.9–12.8 percentage points on every fresh split.
The comparison is within correlation groups; it is a selective explanation
reliability result, not a prediction-accuracy result or evidence that
correlation groups beat random groups overall.

**Defensible report sentence:** “After a gap threshold was chosen on five
exploratory splits and frozen before evaluation, showing one headline reason
only when its leading group was clearly ahead improved first-reason repeat
agreement by 11.9–12.8 percentage points at 69.2–75.6% coverage on all five
fresh splits of the UCI dataset.”

Fresh splits share the same source population, so this is descriptive evidence,
not a claim about independent cohorts or a population p-value.

## The original grouping comparison

On the original five predefined splits, correlation grouping exceeded the
mean of 30 size-matched random partitions in overall ranking stability on four
splits: +0.0609, +0.0479, +0.0209 and +0.0064 RBO; it lost by −0.0018 on the
fifth. On five fresh splits, it won on three (+0.0083, +0.0107 and +0.0222)
and lost on two (−0.0008 and −0.0025). Thus the combined ten-split count is
seven wins and three losses, with a much smaller fresh advantage.

Individual first-reason stability is not consistently favorable. On the
original splits correlation groups won twice (+0.005 and +0.311 percentage
points) and lost three times (−2.062, −2.789 and −0.457). On fresh splits it
won once (+1.953) and lost four times (−0.141, −2.447, −0.530 and −2.698).
The near-zero +0.005 result is effectively a tie at the displayed precision.

## Fresh split results

| Seed | Overall RBO delta | First-reason delta (pp) | Cancellation | Rule coverage | Rule R1 − baseline (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20261032 | +0.0083 | −0.141 | 91.4% | 69.2% | +12.8 |
| 20261033 | −0.0008 | −2.447 | 89.6% | 70.5% | +12.6 |
| 20261034 | −0.0025 | −0.530 | 84.5% | 71.8% | +12.4 |
| 20261035 | +0.0107 | −2.698 | 84.6% | 75.6% | +11.9 |
| 20261036 | +0.0222 | +1.953 | 85.8% | 73.6% | +12.3 |

The full original table is in
[experiments/repeated-splits/README.md](experiments/repeated-splits/README.md).
Full-precision fresh values are in
[experiments/fresh-splits/per_split.csv](experiments/fresh-splits/per_split.csv)
and frozen-rule values in
[experiments/near-tie/fresh/rule_metrics.csv](experiments/near-tie/fresh/rule_metrics.csv).

## What each result means

- **Prediction accuracy:** Across the pilot's ten bootstrap fits, mean AP is
  0.4894, ROC-AUC 0.7130 and Brier 0.1477. These score predicted default
  probabilities; they are not explanation metrics.
- **Overall ranking stability:** RBO compares the ranking of mean absolute
  signed group contributions across refits. It is a population-level
  representation stability metric.
- **Individual first-reason stability:** It asks whether the same borrower’s
  largest absolute signed group contribution is first in two refits. It is a
  local repeatability metric and is mixed for grouping versus random controls.
- **Cancellation:** The six monthly bill contributions have 85.6–90.7% median
  cancellation on the original splits and 84.5–91.4% on fresh splits. They
  contain large opposing signed terms, so their small net sum needs a
  component drill-down.

The first reason can lower predicted risk: 49.4–54.1% of original
borrower–fit rows had a negative leading signed contribution. No decision
threshold is fitted, so “first reason” is not a denial reason.

## Verified fixes

No verified defect changed a published score. The audit did find a silent
edge-case risk: `argmax` would have called an all-zero group row a first
reason, and ties were only implicit. The code now counts and excludes
undefined rows in the defined-only diagnostic, counts exact ties, preserves
the historical tie order, and reports whether the leading group lowered risk.
All 25,000 original borrower–fit rows had neither a zero first reason nor a
tie, so the corrected diagnostic equals the published one.

The audit also made random partitions testable, saved attributions for later
analysis, traced one Figure 2 borrower through the workbook and refit,
repaired the clean-checkout comparison to accept newly added audit columns,
and made figure sources machine-readable.

## External evaluation of the frozen threshold

On South German Credit, one-reason coverage was 27.6–33.3% and the repeat-agreement gain was 12.9–20.1 percentage points. On Polish Companies Bankruptcy, coverage was 35.6–52.0% and the gain was 1.8–9.9 points. The rule met both targets on zero splits of either external dataset. Each external dataset used freshly fitted logistic models and train-derived groups. [Methods and per-split results](experiments/external/README.md)

## Remaining submission limits

The monthly bill-cancellation analysis covers the Taiwan dataset. The external experiments assess transfer of the display rule to two additional datasets.
It lacks synthetic known-ground-truth experiments, another
model family or explainer, temporal evaluation, recourse, human evaluation and
inferential treatment of dependent fit pairs. It therefore does not support
claims of causal recourse, legal compliance, general explanation correctness,
or publication readiness.
