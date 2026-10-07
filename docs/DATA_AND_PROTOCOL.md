# External data and protocol contract

Input is UTF-8 CSV with exactly these headers:

```csv
series,time,y,split,event
sensor_a,0,1.25,train,
sensor_a,1,1.32,train,
```

Each series needs at least 20 training, 20 calibration and 20 test observations, in that order and in contiguous blocks. Calibration also must be long enough for the requested quantile. Times must be numeric, finite, strictly increasing, equally spaced and unique within each series. Different series may have different time ranges. The engine does not silently sort, impute, exclude outliers or interpolate missing measurements. Do explicit preprocessing before freezing and document it.

`y` is one finite measured scalar. `event` is 0 for a known normal state, 1 for a known event state, or empty for unknown. Empty never means negative. The supplied threshold-calibration protocol requires no known events in train/calibration; labelled events there are rejected. A different training policy needs a new explicit experiment design.

The model predicts the next sample of that scalar. Labels are used only for diagnostic scoring, never as a predictor input. Failure probabilities, arbitrary feature vectors, irregular intervals and physical PDE integration are outside v0.1.

Copy one `protocols/*.json` file and give the new experiment a unique `id`, a narrow `claim`, accurate `value_unit` and `time_unit`, and the correct `dataset_kind` (`synthetic` or `external_retrospective`). The engine accepts no unrecognized protocol fields and fixes the primary comparator to matched EWMA. `decay` must be in [0,1); `epsilon_scale` must be positive. Freeze `alpha`, the minimum relative gain, bootstrap draws, block length, seed and allowable labelled-normal alert rate. For this implementation, `equation_ids` is `["ME-047"]`, `sectors` is `[]`, and `interaction_order` is 0.

Bulk CSV evaluation always labels evidence as a retrospective replay. Prospective operation uses the separate forecast and resolve commands. Keeping an outcome locally secret from a predictor function does not by itself establish evaluator blinding.

## Included data

| File | Origin | Chronological splits | Interpretation |
|---|---|---|---|
| `control_drift.csv` | Fixed synthetic AR process, 12 seeds | Per series: 200 train / 150 calibration / 250 test | A planted change in forcing after sample 375; not a physical failure experiment |
| `control_null.csv` | Same seed family with no forcing change | Same counts | Negative control; related to the drift fixture, not an independent replication |
| `sunspots.csv` | statsmodels mirror of historical NGDC annual sunspot data | 1700–1879 train / 1880–1949 calibration / 1950–2008 test | External observational, retrospective, 59 test observations, no event labels |

`data/sunspots_original.csv` preserves the retrieved source table. The dataset is documented as public domain by statsmodels. It is a legacy 1700–2008 series, not a claim to use the latest revised solar index. Source URLs and byte identities are recorded in `cpe/registry/source_lock.json` and `references/PROVENANCE.md`.

All source values were available during software construction. No benchmark in this release is described as a blind, independently conducted prospective confirmation. The model family and criteria were fixed before evaluating the supplied release runs, and no tuning was conducted after viewing their results.

To regenerate the supplied data and registries, run `python scripts/build_assets.py`. A data or source change invalidates any old freeze; start a new experiment directory.
