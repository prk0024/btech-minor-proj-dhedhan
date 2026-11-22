# External evaluation of the frozen display rule

The Taiwan study selected a relative-gap threshold of 0.36. These two follow-up evaluations reuse the [frozen protocol](../near-tie/PROTOCOL.md) and the repository's logistic-regression, attribution, grouping, and scoring functions. Each dataset receives newly fitted models and groups learned from its training rows. Each of the five stratified 80/20 splits uses ten bootstrap fits. Split seeds run from 20261032 to 20261036.

| Dataset | One-reason coverage | Repeat among selected cases | Gain over all-case repeat rate | Splits with coverage ≥50% and gain ≥5 percentage points |
| --- | ---: | ---: | ---: | ---: |
| [Taiwan, fresh splits](../near-tie/fresh/rule_metrics.csv) | 69.2–75.6% | 88.2–92.1% | 11.9–12.8 pp | 5/5 |
| [South German Credit](south_german_results.csv) | 27.6–33.3% | 59.7–68.4% | 12.9–20.1 pp | 0/5 |
| [Polish Companies Bankruptcy](polish_results.csv) | 35.6–52.0% | 17.1–40.9% | 1.8–9.9 pp | 0/5 |

Ranges describe the five splits within each dataset. The protocol required both targets on at least four splits. German coverage was below 50% on every split. In Poland, two splits met the gain target and one met the coverage target, on different splits. The ordered comparisons reuse records and model fits.

## Data and preprocessing

- **South German Credit (UPDATE)** uses 1,000 records and codes the 300 bad-credit outcomes as positive. The adapter excludes age, personal status/sex and foreign-worker status. It learns categories for eight indicator-encoded fields using training rows and audits all 200 held-out records per split (18,000 ordered comparisons). [UCI dataset](https://archive.ics.uci.edu/dataset/573/south+german+credit+update)
- **Polish Companies Bankruptcy** uses the 7,027 records and 271 bankruptcies in `1year.arff`. Training-constant inputs are removed. Missing values are filled with training medians for group discovery and with bootstrap-specific medians during model fitting. Each split audits 500 held-out companies (45,000 ordered comparisons). [UCI dataset](https://archive.ics.uci.edu/dataset/365/polish+companies+bankruptcy+data)

## Reproduce from the repository root

Use Python 3.12 with the pinned root requirements. Download the original archives and write regenerated tables to a new run directory.

```bash
uv venv --python 3.12
uv pip install -r requirements.txt
source .venv/bin/activate
mkdir -p runs/external
curl -fL 'https://archive.ics.uci.edu/static/public/573/south+german+credit+update.zip' -o runs/external/south-german.zip
curl -fL 'https://archive.ics.uci.edu/static/public/365/polish+companies+bankruptcy+data.zip' -o runs/external/polish.zip
python -m experiments.external.south_german_audit runs/external/south-german.zip experiments/near-tie/protocol.json runs/external/south_german_results.csv
python -m experiments.external.polish_audit runs/external/polish.zip experiments/near-tie/protocol.json runs/external/polish_results.csv
```

Each adapter prints the archive SHA-256. The recorded values are:

| Archive | SHA-256 |
| --- | --- |
| South German Credit | `0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551` |
| Polish Companies Bankruptcy | `17377929aa0b204bbf957e56462cf827c19fe4e2ce89f27dfbc77f9ea2bb16c9` |

The CSV columns `coverage`, `baseline_repeat`, `single_reason_repeat` and `single_minus_baseline` use fractions. Multiply the last by 100 for gain in percentage points. The CSVs also report random-partition controls and predictive ROC-AUC.

To draw [Figure 7](../../figures/figure-7-transfer-targets.png) and [Figure 8](../../figures/figure-8-repeat-agreement.png) from the committed tables:

```bash
python -m experiments.external.plot_results --output-dir runs/external/figures
```
