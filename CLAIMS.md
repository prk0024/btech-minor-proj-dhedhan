# Evidence ledger

This ledger separates results that the root executable can regenerate from
historical research material under `new-repo/`. Paths below are the evidence,
not a claim that an unrun study was completed.

| Claim | Evidence | Status and limit |
| --- | --- | --- |
| The root code is a preliminary UCI logistic-regression audit. | [demo.py](demo.py), [requirements.txt](requirements.txt), [data/README.md](data/README.md) | Executable and reproduced. It is one observational Taiwanese credit dataset, not current Indian lending data. |
| The original pilot scores are AP 0.4894, ROC-AUC 0.7130, Brier 0.1477, group RBO 0.9240 and matched-random RBO 0.8631. | [results/pilot.json](results/pilot.json), [experiments/pilot-borrower-audit/pilot.json](experiments/pilot-borrower-audit/pilot.json), [experiments/reproduction/README.md](experiments/reproduction/README.md) | Executable and reproduced before edits. |
| The original five predefined splits favor correlation groups in overall RBO on four of five splits. | [experiments/repeated-splits/per_split.csv](experiments/repeated-splits/per_split.csv) | Executable. Descriptive repeated splits, not independent cohorts or an inferential test. |
| On the original five splits, first-reason agreement is mixed: correlation groups win twice, lose three times, and one win is +0.005 pp. | [experiments/repeated-splits/per_split.csv](experiments/repeated-splits/per_split.csv) | Executable. “First reason” means largest absolute signed group contribution, not a denial reason. |
| The original five median bill-cancellation values span 85.6%–90.7%. | [experiments/repeated-splits/per_split.csv](experiments/repeated-splits/per_split.csv), [experiments/pilot-borrower-audit/bill_cancellation.csv](experiments/pilot-borrower-audit/bill_cancellation.csv) | Executable. Cancellation is a diagnostic of internal opposing signs, not an error proof. |
| The audit has no zero-magnitude or exact-tie first reasons across the original five splits, and a leading group lowers risk on 49.4%–54.1% of borrower–fit rows. | [experiments/audit/README.md](experiments/audit/README.md) | Executable audit result. No decision threshold is applied. |
| The frozen one-or-two-reason rule meets its prespecified gain criterion on all five fresh splits. | [experiments/near-tie/PROTOCOL.md](experiments/near-tie/PROTOCOL.md), [experiments/near-tie/fresh/rule_metrics.csv](experiments/near-tie/fresh/rule_metrics.csv) | Executable fresh-split result. It compares selective explanation reliability with all-case reliability; it does not establish better model accuracy or a superior grouping method. |
| The frozen Taiwan threshold selected cases with above-baseline repeat agreement on all ten external splits. Neither external dataset met the prespecified joint target. | [External evaluation](experiments/external/README.md), [German results](experiments/external/south_german_results.csv), [Polish results](experiments/external/polish_results.csv) | Five overlapping splits per external dataset. The tested model family is logistic regression. |
| The root test suite passes. | [test_demo.py](test_demo.py), [test_near_tie.py](test_near_tie.py), [experiments/reproduction/README.md](experiments/reproduction/README.md) | Executable. The current suite has more tests than the historical “nine checks” snapshot. |
| The source workbook, split, background and Figure 2 values are consistent for workbook row 2812. | [trace_borrower.py](trace_borrower.py), [experiments/borrower-trace/row-2812.md](experiments/borrower-trace/row-2812.md) | Executable trace. The row is selected by the pre-existing median-cancellation rule, not for a favorable conclusion. |
| `new-repo/` contains a literature/proposal package and historical code snapshot. | [new-repo/comet_deliverables/00_START_HERE.md](new-repo/comet_deliverables/00_START_HERE.md) | Historical material only. Do not treat its plans as executable evidence. |
| Synthetic oracle tests, TreeSHAP/LIME comparisons, human evaluation, recourse, temporal validation and publication validation were completed. | No root executable evidence. | Not completed in this repository. |

The archived [results/run_log.txt](results/run_log.txt) is from Python 3.12.14,
whereas [results/pilot.json](results/pilot.json) is from Python 3.12.10. They
differ only at floating-point roundoff in Brier and additivity residual. The
reproduction matches `pilot.json`; details are in
[experiments/reproduction/README.md](experiments/reproduction/README.md).
