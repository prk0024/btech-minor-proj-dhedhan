# COMET-XAI Lite study guide to explanation stability

Imagine a credit model gives the same borrower almost the same risk score on Monday and Friday. On Monday its biggest explanation is the credit limit. On Friday it is repayment history. The borrower’s record stayed the same. The bank trained the second model on a slightly different sample. Which part of the explanation should you trust to repeat?

**COMET-XAI Lite studies that question by repeatedly training a model and explaining the same people.** On a historical Taiwanese credit dataset, a simple rule found many cases in which the leading explanation repeated. The same cutoff performed differently on two other datasets. To understand why those statements can both be true, follow one borrower from a spreadsheet row to an explanation, then follow that explanation across model refits. [Repository at the version covered by this guide](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/README.md)

# From a credit record to a research question

Think of a supervised learning dataset as a spreadsheet. A **row** is one example. A **feature** is an input column available when making a prediction. The **target** is the answer the model learns to predict. Default is the recorded failure to meet a repayment obligation. Here a row is a credit-card account, the inputs include its bills and repayments, and the target records whether the client defaulted the following month. A model fits its parameters on past examples, then estimates a probability for a held-out example.

XAI stands for explainable artificial intelligence. An **explanation** in this project is a numerical breakdown of one model score. Each input receives a signed contribution relative to a reference level. The project calls the group with the largest contribution in absolute magnitude the **first reason**. If the strongest contribution is negative, that reason points toward lower predicted risk. The experiment never makes an approve-or-deny decision.

Why might the first reason change? Suppose August and September bills closely track each other. Either bill can help a model estimate risk. One training sample may give August a slightly larger coefficient, another may give September the larger one. Similar predicted scores can then have different leading contributors. This is a motivation for the audit. The experiment measures actual switches without requiring the predicted scores of two fits to be identical.

The project asks three related questions. Does grouping inputs that move together make rankings repeat more often than equally sized random groups? How much of the positive and negative detail disappears when monthly contributions are added? And can the distance between the first and second reasons tell us when it makes sense to show only one? Each question has its own comparison and its own denominator.

# The data and the experiment

The main dataset is UCI’s **Default of Credit Card Clients**, with 30,000 historical Taiwanese accounts. The event rate is 22.12%, roughly 22 defaults per 100 accounts. The code keeps 19 inputs. The outcome is stored separately. ID, sex, education, marital status, and age are excluded from the predictors. Removing these columns says which inputs the model sees. Establishing fairness would require its own evaluation. [UCI dataset](https://doi.org/10.24432/C55S3H) · [Loader and feature definitions](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/demo.py)

| Input family | Count | What one value means |
|---|---:|---|
| Credit limit | 1 | The account’s credit limit, recorded as LIMIT_BAL |
| Repayment status | 6 | A monthly status code, such as a recorded payment delay |
| Bill amounts | 6 | The amount on one month’s billing statement |
| Payment amounts | 6 | The amount paid for one month |

The status and payment columns describe different things. For example, PAY_2 is a repayment-status code, whereas PAY_AMT2 is a monetary amount. The model treats the status codes as numeric. That choice imposes a numerical spacing on categories that may have different meanings.

## What changes when the model is refitted

1. **Split the accounts.** A stratified 80/20 split assigns 24,000 accounts to training and 6,000 to testing, keeping the default proportions similar. A seed fixes a random draw so someone else can reproduce it.
2. **Choose the people to explain.** Select 500 of the 6,000 test accounts at random with seed 20. Every refit on this split explains these same 500 accounts. Prediction metrics use all 6,000 test accounts.
3. **Learn the feature groups.** Use only the 24,000 training rows to group related columns. Keep this partition fixed across refits so a group has the same meaning whenever two fits are compared.
4. **Draw a bootstrap sample.** Draw 24,000 training rows with replacement. The same account can appear more than once, and others are left out. Train a model on this draw. Repeat with seeds 0 through 9 to get ten fits.
5. **Explain and compare.** For each fit, calculate feature contributions for each audit account. Aggregate them into groups, find the winner, and compare the results across fits. Repeating the whole procedure with another split changes the training pool, audit sample, and potentially the learned groups.

Two counts will recur. Ten fits yield **45 unordered pairs**, because comparing A with B is the same as comparing B with A for simple agreement. Multiplying by 500 accounts gives 22,500 comparisons per partition. When A chooses what to display and B checks it, direction matters. There are **90 ordered pairs** and 45,000 comparisons. Those comparisons repeatedly use the same people and fits. Their shared people and fits must be accounted for when estimating uncertainty. [Experiment code](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/demo.py) · [Rule protocol](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/near-tie/PROTOCOL.md)

# How one prediction becomes an explanation

The model is **logistic regression**. Each input gets a learned weight, called a coefficient. A larger coefficient in absolute value makes a one-unit change on the model’s input scale move the score farther, holding the other inputs fixed. The training pipeline replaces missing entries with training-sample medians, standardizes the columns, and fits regularized logistic regression. Standardization subtracts a center and divides by a scale so a dollar and a status code have comparable numerical treatment. Regularization discourages excessively large weights. The code fits these steps anew on each bootstrap draw.

Logistic regression adds terms on the **log-odds** scale. If the predicted probability is 0.20, the odds are 0.20 divided by 0.80, or 1 to 4. Taking the natural logarithm gives about −1.386. A log-odds score of zero corresponds to 50% probability. A positive contribution pushes probability upward relative to the same score without that term. The probability change depends on the starting score. A contribution of +0.10 is therefore measured in log-odds units.

Write the score as an intercept plus a sum of coefficient times standardized input. For a particular fitted model, the **background** is the full training pool transformed by that fit’s preprocessing. The baseline log-odds is the intercept plus the weights applied to the average transformed inputs. Subtracting this baseline from the borrower’s score leaves a sum of feature contributions. For feature j the arithmetic is:

```text
contribution[j] = fitted_weight[j] × (borrower_value[j] − training_mean[j])
borrower log-odds = baseline log-odds + sum of all feature contributions
```

Here both values in parentheses are on the same preprocessed scale. For an illustrative feature with weight −0.30 and a value two standardized units above the training mean, the contribution is −0.60. An input at its training mean contributes zero even if its coefficient is large. The baseline is the average training **log-odds** under that fit. Averaging probabilities is a different operation.

In explainable machine learning, **feature attribution** means assigning portions of a model output to inputs. SHAP stands for Shapley Additive Explanations. It is a family of attributions based on averaging what an input adds when different other inputs are already known. The particular convention here replaces unavailable features using a background distribution without conditioning on the observed features. For an additive linear score, the resulting interventional SHAP calculation reduces exactly to the arithmetic above. The code evaluates that expression directly and verifies that the baseline plus the contributions reconstructs the score. Exact reconstruction tells us that the accounting is correct for this model. It cannot tell us what would happen if a borrower changed their behavior. [Implementation and additivity check](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/demo.py)

# Why features are grouped

A **partition** assigns every input to exactly one group. The project builds a partition from training-data Spearman correlations. Spearman correlation measures whether two columns tend to rank accounts similarly or in reverse order. The code uses the absolute correlation so either kind of relationship can link features. It starts with individual features and uses **complete-linkage clustering**. At the chosen cutoff, every pair within a resulting group must have absolute correlation at least 0.70. This prevents A from pulling in C solely because both are close to B.

In the pilot, 19 columns become 11 groups. All six bills form one group. Two sets of repayment-status columns form groups of two and three. The credit limit and the remaining inputs stand alone. For any one borrower and fit, the contribution of a group is the **sum with signs preserved**. The strength used to rank it is the absolute value of that sum.

Consider two invented months contributing +0.40 and −0.35. Together they contribute +0.05, even though 0.75 units of total magnitude went into the calculation. A different group contributing −0.20 outranks the bill group because 0.20 exceeds 0.05. Adding the absolute values first would produce a different ranking and answer a different question.

**Why compare with random groups?** Shortening a list can make it easier for rankings to agree even when the groups have no particular meaning. The control shuffles the feature identities, divides them into groups with exactly the same sizes as the learned groups, and repeats this 30 times using seed 101. Each random partition stays fixed across all ten fits. The audit measures agreement *within* each partition and then averages the 30 scores. It never asks whether a random group has the same name or contents as a correlation group. [Grouping and control implementation](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/demo.py)

# One real borrower from beginning to end

Open the borrower trace for zero-based row 2812, workbook ID 2813. This account was in the pilot test set, was sampled for the audit, and had an observed outcome of no default. It was selected for Figure 2 because its cancellation was closest to the median for refit 0, with ties broken by row index. That selection makes it an example of typical cancellation for that fit. [Borrower trace](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/borrower-trace/row-2812.md) · [Figure 2](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/figures/figure-2-cancellation.pdf)

| Month | Raw bill | Contribution to log-odds |
|---|---:|---:|
| September | 19,674 | +0.1182 |
| August | 17,810 | −0.0100 |
| July | 19,753 | −0.0739 |
| June | 21,550 | +0.0122 |
| May | 21,032 | −0.0003 |
| April | 19,979 | −0.0074 |

Every listed bill amount is positive. The contribution can still be negative because it depends on both the coefficient and the difference from the training background. Adding the full-precision contributions gives a signed bill total of **+0.0388** after rounding. Adding their magnitudes gives **0.2220**. The code measures the fraction of the total magnitude that disappears when signs are respected:

```text
cancellation = 1 − absolute value of signed total / total magnitude
             ≈ 1 − 0.0388 / 0.2220
             ≈ 82.5%
```

A value of 0% means all nonzero contributions point the same way. A value of 100% means opposite signs balance exactly despite nonzero total magnitude. If every contribution is zero, the fraction is undefined. For the pilot’s reported median, the code computes a fraction for each borrower and fit, then takes the median over defined rows across 500 borrowers × 10 fits. That gives **85.6%**. The 82.5% describes this one example.

Look beyond the bills. The strongest group for this borrower was credit limit at **−0.0578**. The runner-up was one monthly payment at **+0.0448**. The distance between their magnitudes was about 0.0130. Dividing by the leading magnitude gives **0.225**, a 22.5% lead using the winner as denominator. Under the later display rule, this fit would show both reasons. The recorded outcome tells us how the loan performed. Checking whether the explanation repeats requires a second model fit.

# Reading the metrics

The project scores three different objects. The repayment outcome is used to score predictions. The other fits are used to score repeatability. The signed components inside one group are used to score cancellation.

| Measure | Calculation in plain language | Pilot result |
|---|---|---:|
| Average precision (AP) | Rank accounts by default score. At thresholds that recover additional actual defaults, average the precision with the corresponding gains in recall as weights. The event rate of 0.2212 gives context. | 0.4894 |
| ROC-AUC | How often an actual defaulter ranks above a non-defaulter across pairs, counting a tie as half. Random ordering scores 0.5. | 0.7130 |
| Brier score | Average the squared difference between predicted probability and outcome, coded 0 or 1. Lower is better. | 0.1477 |
| Rank-biased overlap (RBO) | Compare two complete rankings of groups, giving greater weight to agreement near the top. Identical rankings score 1. | 0.9240 for correlation groups |
| First-reason agreement | Compare two fits on the same account. Score 1 when the winning group identity matches, otherwise 0. Average over accounts and pairs. | 78.5% for correlation groups |
| Bill cancellation | Measure how much of the six bill contributions’ total magnitude cancels within one account and fit. Take the median. | 85.6% |

In the AP calculation, **precision** means the fraction of accounts flagged at a threshold that actually default. **Recall** means the fraction of all actual defaults caught at that threshold. As the threshold moves, the model flags more or fewer accounts. AP summarizes how well precision holds up as recall increases.

**How RBO gets its ranking.** Within one fit, calculate each group’s strength for each audit account. Average the strengths over the 500 accounts, then sort the groups. Compare two such rankings by looking at the overlap in their first item, first two items, first three items, and so on. The parameter 0.85 controls how quickly the weights decrease with depth. For lists A–B–C and A–C–B, the overlap fractions are 1, 1/2, and 1. The implementation scores those lists 0.93625. An RBO of 0.924 is a ranking score on a zero-to-one scale.

**How local agreement differs.** If two borrowers exchange which group leads for them, the dataset-wide average strengths can stay the same while both borrowers’ winners change. Also, a win here records the group identity. A repeat can occur even if the signed direction changes. Exact top ties go to the earliest group in partition order. All-zero rows have no defined winner and are excluded from the rule analysis. Across the five original splits the audit found zero tied or all-zero winners among 25,000 borrower–fit rows. In 49.4–54.1% of rows per split the top group lowered predicted risk. [Metric code](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/demo.py) · [Audit results](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/audit/README.md)

# What the grouping experiment found

On the pilot split the ungrouped feature ranking scored 0.7761 RBO. The correlation groups scored 0.9240 and the size-matched random groups averaged 0.8631. The direct controlled comparison is **+0.0609 RBO** for the overall ranking. For an individual’s first reason, the same methods scored **78.5% versus 80.6%**, a difference of **−2.06 percentage points** using unrounded numbers. A percentage-point difference is subtraction of two percentages. The apparently conflicting answers come from comparing different objects. [Pilot results](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/results/pilot.json) · [Figure 1](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/figures/figure-1-agreement.pdf)

| Taiwan splits | Higher overall RBO than matched random | Higher individual agreement than matched random | Median bill cancellation across splits |
|---|---:|---:|---:|
| Original five, including the pilot | 4 of 5 | 2 of 5 | 85.6–90.7% |
| Five fresh split seeds | 3 of 5 | 1 of 5 | 84.5–91.4% |

One of the two original local wins was approximately **0.005 percentage points**. The count of wins gives that tiny difference the same weight as a much larger one. The repository publishes the effect sizes as well. Fresh splits changed the train/test assignment within the same source dataset. The comparison supports a modest, mixed result for grouping, especially at the individual level. [Original splits](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/repeated-splits/per_split.csv) · [Fresh splits](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/fresh-splits/per_split.csv)

# How the one or two reason rule works

Suppose the two biggest group strengths are 0.50 and 0.49. A small change in fitted weights could swap them. If they are 0.50 and 0.10, the runner-up has much farther to go. The **relative gap** expresses the lead as a fraction of the winning strength. With m1 the largest and m2 the second largest, the gap is (m1 − m2) / m1. The two examples give 0.02 and 0.80. A gap of 0.36 means the runner-up is 64% as strong as the winner. It says nothing by itself about a 36% default probability.

The **source fit** decides what to display. When its gap is at least 0.36, show the leading group alone. Otherwise show its top two groups. A second, **replicate fit**, independently supplies its ranking for the same person, using a different bootstrap draw from the same training pool. Only the source fit’s scores enter its choice. Pairs with an undefined winner in either fit are excluded. Switching source and replicate can change how many reasons are shown.

## Choosing the threshold and giving it a fair test

The first five Taiwan split seeds (20261027 through 20261031) served as exploratory data for the rule. The code pooled their valid ordered comparisons and tried cutoffs from 0.00 to 0.99 in steps of 0.01. It picked the smallest cutoff whose selected one-reason cases achieved at least 90% repeat agreement. The selected cutoff was **0.36**, yielding 71.6% coverage and 90.3% agreement on those exploratory cases. A more restrictive cutoff could achieve high agreement simply by selecting very few cases. That is why coverage has to travel with the result.

The threshold and evaluation criterion were recorded in commit 21eff88 before the five fresh Taiwan split seeds were evaluated. The criterion required a gain of **at least five percentage points** at **at least 50% one-reason coverage**, on **at least four of five splits**. The exploratory 90% target selected the cutoff. The fresh pass criterion used gain and coverage, so a fresh repeat rate below 90% can still pass. [Frozen protocol](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/near-tie/PROTOCOL.md) · [Threshold implementation](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/near_tie.py)

## The four numbers in a rule result

- **Coverage** is the fraction of valid ordered comparisons in which the source shows one reason. The remainder receive two.
- **Baseline repeat rate (B)** is the fraction of all valid comparisons in which the two first reasons match. A randomly selected subset at the same coverage has this repeat rate in expectation.
- **Selected repeat rate (R1)** is the fraction of the one-reason comparisons in which the displayed reason remains first in the replicate. **Gain** is R1 minus B. Positive gain means the rule selected easier-to-repeat cases. Displaying fewer reasons never changes either fitted model.
- **Containment** counts a success if the replicate winner appears anywhere in the displayed set of one or two reasons. Two chances can increase containment mechanically. The repository also evaluates randomly assigning which cases get two reasons at the same rate, and a separate control that always pairs the source winner with a uniformly random other group.

For the first fresh Taiwan split, there were 45,000 valid comparisons. One reason was shown in 69.2%, or 31,140 comparisons. In those, the leading reason repeated in 92.13%. Across all comparisons the repeat rate was 79.38%. Their difference, rounded, is **12.8 percentage points**. Overall containment was 88.55%, including the harder cases that received two reasons. These percentages differ because they score different events or use different denominators. [Full-precision results](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/near-tie/fresh/rule_metrics.csv)

All five fresh Taiwan splits passed. Coverage ranged from **69.2% to 75.6%**, R1 from **88.2% to 92.1%**, and gain from **11.9 to 12.8 percentage points**. The repo also compares methods at fixed coverage levels of 25%, 50%, 75%, and 100%. A separate exploratory analysis asked how well the gap ranks future repeats above switches. On all five original correlation-group splits, the *absolute* gap had higher ROC-AUC for predicting repeats than the relative gap. This matters when interpreting the choice of rule. Its success against random selection leaves room for simpler alternatives. [Selective coverage results](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/near-tie/fresh/selective_coverage.csv) · [Exploratory gap comparison](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/near-tie/exploratory/gap_auc.csv)

# What happened on two other datasets

The checked-in experiment at version 8107cf0 uses Taiwan data. Two [external evaluations](../experiments/external/README.md) applied the repo’s fitting, grouping, and scoring functions to different datasets. They used the same frozen threshold, the same five fresh seed numbers, stratified 80/20 splits, and ten bootstrap fits per split. Each dataset received newly fitted models and newly learned groups. The question was whether the **display rule** transferred when another model was trained on a different problem. [Repository evidence ledger](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/CLAIMS.md)

**South German Credit** has 1,000 credit records, including 300 labeled bad. The adapter coded bad credit as the positive class. It excluded age, personal-status/sex, and foreign-worker status. Eight categorical fields, including credit history and loan purpose, became indicator columns using categories observed in training. Each indicator says whether a record has a particular category. The remaining inputs retained their supplied numeric codes or values. All 200 held-out accounts were audited per split, yielding 18,000 ordered comparisons. [UCI South German Credit](https://archive.ics.uci.edu/dataset/573/south+german+credit+update)

**Polish Companies Bankruptcy** concerns companies and financial ratios. The adapter used only the file named `1year.arff`, with 7,027 records and 271 bankruptcy labels. It removed features constant within the training set, filled missing values with training medians for group discovery, and used the repo’s bootstrap-specific imputation for each model fit. Each split audited 500 held-out companies, yielding 45,000 ordered comparisons. A leading reason here is a group of company ratios. [UCI Polish Companies Bankruptcy](https://archive.ics.uci.edu/dataset/365/polish+companies+bankruptcy+data)

| Five evaluation splits per dataset | Coverage | Baseline repeat | Selected repeat | Gain in points | Splits passing both targets |
|---|---:|---:|---:|---:|---:|
| Taiwan credit cards | 69.2–75.6% | 75.7–79.4% | 88.2–92.1% | 11.9–12.8 | 5/5 |
| South German Credit | 27.6–33.3% | 46.7–52.5% | 59.7–68.4% | 12.9–20.1 | 0/5 |
| Polish companies | 35.6–52.0% | 15.3–32.9% | 17.1–40.9% | 1.8–9.9 | 0/5 |

Each range gives the lowest and highest value across the five splits. Endpoints in different columns can come from different splits. On South German Credit, all five splits cleared the gain target and none cleared coverage. On Polish companies, two cleared gain and one cleared coverage, on different splits. An individual Polish split could have a positive gain even though most single explanations still changed under refitting. For example, on seed 20261032 the baseline was 15.3% and the selected rate was 17.1%.

Across these runs, the frozen rule selected cases with higher observed repeat agreement on every evaluated split. The cutoff met the prespecified joint target only on Taiwan. Dataset size, input representation, event rate, and outcome all change between settings. The runs cannot isolate which difference explains the drop. They also cannot justify calling 0.36 a universal reliability threshold.

# Finding your way through the repository

Read from the repository root at commit 8107cf0. The root scripts are the implementation behind the current Taiwan results. The historical directory contains an earlier pilot and a broader project proposal. For a first reading, follow one route through the code:

1. **Acquire the rows.** `download_data.py` checks the workbook’s SHA-256 fingerprint. `demo.py → load_frame` separates predictors from the recorded outcome. A matching fingerprint means the input bytes match the archived workbook.
2. **Train and explain.** In `demo.py`, read `run`, then `groups_from_training`, `fit_one`, `group_magnitudes`, and `first_reason_rows`. The saved attribution array has axes **fit × audit account × feature**, or 10 × 500 × 19 for a standard Taiwan run. Once this array is available, many explanation questions can be answered without training again.
3. **Compare and repeat.** In `demo.py`, `mean_stability` turns per-account strengths into overall rankings. `borrower_top1_agreement` compares local winners. `bill_cancellation_table` retains the signed components. `repeat_splits.py` runs the same procedure with each split seed and collects one summary row per split.
4. **Evaluate the display rule.** In `near_tie.py`, `cases` constructs ordered comparisons, `select_tau` selects the exploratory threshold, `rule_metrics` calculates the outcomes, and `evaluate` applies the saved protocol. `report_figures.py` converts recorded results into the six report figures.
5. **Check the evidence.** `trace_borrower.py` reconstructs the worked borrower. `test_demo.py` and `test_near_tie.py` exercise hand-checkable cases and pipeline behavior. `check_reproduction.py` compares the pilot and original splits against archived values and checks the fresh runs’ ranges and gain criteria. Checking exact fresh values also requires comparing the CSVs.

In a generated pilot directory, open **pilot.json** for model metrics, group membership, and overall ranking results. Open **borrower_audit.json** for agreement, cancellation summaries, and counts. **bill_cancellation.csv** contains the six monthly contributions by account and fit, **metrics.csv** contains prediction scores by fit, **splits.npz** stores row indices, and **attributions.npz** stores the arrays used in downstream analyses. CSV is a plain-text table, JSON is a named set of fields, and NPZ holds numeric arrays. [Pilot output code](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/demo.py) · [Run verification](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/check_reproduction.py)

For the research history, start with the current research summary and claims ledger. The literature review explains how this work relates to earlier studies of explanation stability, dependence-based grouping, and information hidden by aggregation. The archived dossier, study guide, slide decks, and starter code under `new-repo/` describe an earlier stage. Its broader ideas include **recourse** (actions that could change a decision), uncertainty under changes over time, alternative explainers such as LIME, and a nonlinear tree-model benchmark. The root implementation addresses the narrower stability audit. The small `kth_margin` helper checks an order-statistic calculation from the older manual and plays no role in fitting the model or choosing the 0.36 gap. [Current summary](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/RESEARCH_SUMMARY.md) · [Literature review](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/research/literature-review/review.md) · [Historical package index](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/new-repo/comet_deliverables/00_START_HERE.md)

# Reproducing the checked-in experiment

With Git and uv installed, use a terminal to create a checkout of the studied version. A virtual environment keeps the project’s packages together. These commands create one with Python 3.12. Run subsequent commands from the repository root. [uv installation](https://docs.astral.sh/uv/getting-started/installation/) · [Pinned Python packages](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/requirements.txt)

```bash
git clone https://github.com/prk0024/btech-minor-proj-dhedhan.git
cd btech-minor-proj-dhedhan
git checkout 8107cf0
uv venv --python 3.12
uv pip install -r requirements.txt
```

Activate the environment with `source .venv/bin/activate` on macOS/Linux, or `.\.venv\Scripts\Activate.ps1` in Windows PowerShell. Download the workbook first to enable the data-dependent integration test. The pilot output directory must be new. For a second run choose a new name and update the paths that refer to it.

```bash
python download_data.py
python -m unittest -v test_demo.py test_near_tie.py
python demo.py --borrower-audit --output-dir runs/study-pilot
python trace_borrower.py --bill-csv runs/study-pilot/bill_cancellation.csv --output runs/study-pilot/row-2812.md
```

Expected checkpoints are **26 passing tests**, then about **78.5%**, **80.6%**, and **85.6%** for correlation-group first-reason agreement, random-group first-reason agreement, and median bill cancellation. Open the generated borrower trace and match its signed totals to the worked example above. A discrepancy in the last decimal can arise from floating-point arithmetic. A different split, fit count, or input file can change the scientific comparison.

```bash
python repeat_splits.py --seeds original --output-dir runs/study-original
python near_tie.py explore --splits-dir runs/study-original --output runs/study-rule/exploratory
python repeat_splits.py --seeds fresh --output-dir runs/study-fresh
python near_tie.py evaluate --splits-dir runs/study-fresh --protocol experiments/near-tie/protocol.json --output runs/study-rule/fresh
python check_reproduction.py --pilot-dir runs/study-pilot --original-csv runs/study-original/per_split.csv --fresh-csv runs/study-fresh/per_split.csv --near-tie-dir runs/study-rule/fresh
```

The exploratory command should rediscover 0.36. The evaluation command above deliberately reads the **committed protocol**. Open `runs/study-rule/fresh/rule_metrics.csv`, locate seed 20261032, and check coverage and repeat agreement against the worked comparison. The verdict should say that five splits met the gain rule. Re-running these known seeds demonstrates reproducibility. New evidence about transfer requires other data. The root loader specifically expects the Taiwan workbook, so the external checks needed dataset-specific adapters. [Clean-checkout record](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/clean-checkout/README.md) · [Archived fresh verdict](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/experiments/near-tie/fresh/verdict.json)

# What the evidence leaves open

**Repeatability and correctness.** A model can consistently rely on a misleading proxy. These datasets provide repayment or bankruptcy labels, but they provide no known true explanation for each person or company. High agreement establishes reproducibility of the leading group under this refitting procedure. Testing what genuinely caused an outcome, what action would improve it, and what explanation a person understands would each need different evidence.

**Which source of instability was tested.** Within a split the borrower, group partition, and explanation convention stay fixed. Changing the bootstrap training rows changes the fitted preprocessing and coefficients. Relearning the groups on every bootstrap would add another source of variation and require a definition of when two different feature sets count as the same group. The monthly inputs are repeated observations inside one record. Random train/test splits do not test performance in a later economic period.

**What could make the research stronger.** A direct comparison at identical one-reason coverage would test whether the relative gap selects more repeatable cases than the absolute gap or the leading magnitude alone. A separate experiment could test whether knowing which months offset one another adds predictive information beyond the gap. The cancellation fraction is determined by the signed net and unsigned total, so any claim of additional information needs a baseline that accounts for those quantities. These are open experiments. Prior work already investigates attribution stability and feature grouping. The narrower contribution here is the controlled comparison and the measured limits of the chosen display rule. [Research positioning and proposed experiments](https://github.com/prk0024/btech-minor-proj-dhedhan/blob/8107cf0410ada347f25e249427b95d841184f7ca/research/literature-review/review.md)

# Check your understanding

1. Two months contribute +0.60 and −0.50. Another group contributes −0.14. Which group wins, and how much cancels inside the monthly group?
2. A borrower’s two strongest group magnitudes are 0.25 and 0.16. How many reasons does the frozen rule show?
3. At 40% coverage a rule raises repeat agreement from 52% to 71%. Does that split pass the recorded joint criterion?
4. Why can the pilot show better overall ranking agreement and worse individual first-reason agreement at the same time?
5. If an explanation repeats for 90 of 100 comparisons, what else would you need to know before claiming it helps borrowers make better decisions?

**Answers**

1. The monthly net is +0.10, so the other group wins with magnitude 0.14. Cancellation is 1 − 0.10 / 1.10, or about 90.9%. The strongest group lowers predicted risk.
2. The relative gap is (0.25 − 0.16) / 0.25 = 0.36. The mathematical rule includes equality, so it shows one reason.
3. The gain is 19 percentage points, comfortably above five. Coverage is below 50%, so the split misses the criterion.
4. The overall analysis first averages over people and then ranks groups. The local analysis ranks groups separately for each person before comparing winners. Changes that reverse individual winners can cancel out in an average.
5. You would need evidence about what people understand and can do with the explanation, whether the suggested relationship is actionable, and what outcomes follow. The refit-agreement count measures none of those outcomes. Even interpreting its uncertainty requires knowing which people and fits were reused.

If you can reconstruct the 82.5% cancellation for row 2812, explain why it yields two displayed reasons, and say why Germany missed the coverage target despite a large gain, you can explain the central result of the project in your own words.
