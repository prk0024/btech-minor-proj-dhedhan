"""Evaluate the frozen display rule on Polish Companies Bankruptcy."""
import argparse
from hashlib import sha256
from io import StringIO
from pathlib import Path
import json
from zipfile import ZipFile

import numpy as np
import pandas as pd
from scipy.io.arff import loadarff
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from demo import fit_one, groups_from_training, matched_random_partitions, mean_stability
from near_tie import cases, rule_metrics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("protocol", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()

protocol = json.loads(args.protocol.read_text())

with ZipFile(args.archive) as archive:
    records, _ = loadarff(StringIO(archive.read("1year.arff").decode("ascii")))
frame = pd.DataFrame(records)
y = frame.pop("class").eq(b"1").astype(int)
predictors = frame
rows = []
for seed in protocol["fresh_split_seeds"]:
    train, test = train_test_split(np.arange(len(frame)), test_size=.2, random_state=seed, stratify=y)
    X = predictors.loc[:, predictors.iloc[train].nunique().gt(1)]
    training = X.iloc[train]
    groups, _ = groups_from_training(training.fillna(training.median()))
    audit = np.random.default_rng(20).choice(test, 500, replace=False)
    fits = [fit_one(X, y, train, audit, seed=fit_seed) for fit_seed in range(10)]
    assert max(fit["residual"] for fit in fits) < 1e-8
    phis = [fit["phi"] for fit in fits]
    metrics = rule_metrics(cases(phis, groups), protocol["tau"], len(groups))
    partitions = matched_random_partitions([len(group) for group in groups], X.shape[1], 30, 101)
    metrics.update(
        split_seed=seed, n_test=len(test),
        correlation_rbo=mean_stability(phis, groups),
        random_mean_rbo=np.mean([mean_stability(phis, partition) for partition in partitions]),
        random_mean_top1=np.mean([cases(phis, partition)["repeat"].mean() for partition in partitions]),
        mean_roc_auc=np.mean([roc_auc_score(y.iloc[test], fit["model"].predict_proba(X.iloc[test])[:, 1]) for fit in fits]),
        non_singleton_groups=json.dumps([X.columns[group].tolist() for group in groups if len(group) > 1]),
    )
    assert metrics["n_cases"] + metrics["n_excluded_undefined"] == len(audit) * 90
    rows.append(metrics)
results = pd.DataFrame(rows)
results.to_csv(args.output, index=False)
print("ZIP SHA-256:", sha256(args.archive.read_bytes()).hexdigest())
print("Rows:", len(frame), "bankruptcies:", y.sum())
print(results.to_string(index=False))
