# Method and fixed experimental contract

## Target

Predict the next real-valued observation in an equally spaced series. The frozen claim is that the CPE candidate lowers mean absolute error (MAE) by at least 5% versus a matched EWMA residual-correction model on the registered test segment. Each dataset is a separate experiment; there is no aggregate claim obtained by choosing the best dataset.

This is a new engineering experiment using a scalar specialization of ME-047. It is not a numerical solution of EFMW's physical field equations or a reproduction of EXP-001's control-loss lead-time study.

## Exact recurrence and time order

Fit an intercept `b` and slope `a` by least squares on adjacent observations in the training segment only. Clip `a` to [-0.99, 0.99] as a predeclared stability constraint. If training variance is zero, use a=0 and b=the training mean. Set scale to max(training population standard deviation, 1e-12 in the data's numerical units).

For the base forecast, innovation and recursive memory:

\[
\widehat y^0_t=a y_{t-1}+b,\qquad
r_t=y_t-\widehat y^0_t,\qquad
m_t=\lambda m_{t-1}+(1-\lambda)r_t.
\]

Here lambda=0.97 in all shipped experiments. Memory starts at zero and is warmed on the training segment after the AR fit. Training predictions are not scored as held-out results.

ME-047 is instantiated on two scalar values in matching units:

\[
C_t=1-\frac{|y_t-\widehat y^0_t|}{|y_t|+|\widehat y^0_t|+\epsilon},
\qquad \epsilon=0.01\,\mathrm{scale}>0.
\]

The numerical implementation first rescales the operands to avoid overflow. The candidate and matched comparator are:

\[
\widehat y^{\mathrm{CPE}}_t=\widehat y^0_t+C_{t-1}m_{t-1},
\qquad
\widehat y^{\mathrm{EWMA}}_t=\widehat y^0_t+m_{t-1}.
\]

The coherence gate is an explicit **experimental design choice**, not a theorem that follows from the 102 equations. Both forecasts use the same fitted AR model, observations and memory. Their only predictive difference is the lagged coherence multiplier. A benefit must be measured rather than assumed.

The no-memory ablation replaces `m_(t-1)` with `r_(t-1)`. AR(1) removes the residual correction entirely. Persistence predicts `y_(t-1)`; the mean baseline predicts the training mean.

For every test time:

1. Produce all six predictions from the state through t-1.
2. Write and flush a forecast event containing no target observation.
3. Receive y_t and record it separately.
4. Update residual, memory and coherence.
5. Proceed to the next forecast.

This is prequential evaluation: previous test outcomes become legal history for later predictions. No test outcome refits a, b, decay, epsilon scale, bands, comparator or pass criterion.

## Calibration and diagnostics

The contiguous calibration segment follows training and precedes test. Each model receives a fixed symmetric empirical interval radius from its calibration absolute errors: the ceil((n+1)(1-alpha))-th order statistic. Insufficient calibration size is an error. No time-series exchangeability or distribution-free coverage theorem is asserted. Reported test coverage reveals misspecification.

The absolute recursive memory is a post-observation diagnostic. Its threshold is the same empirical quantile construction on calibration memory magnitudes. An alert means `abs(m_t) > threshold`; ties do not alert. It is not a probability and it is not evidence of predicting a future failure. Synthetic labels indicate a planted forcing regime, not an actual machine failure. Missing labels remain unknown and yield no false-alarm or detection estimate.

## Scoring and decisions

Primary effect = MAE(EWMA) - MAE(CPE), in observation units. Relative effect divides by MAE(EWMA). If that denominator is zero, relative effect is undefined and no advantage is accepted.

For at least five series, resample entire series as clusters. With fewer than five, resample circular blocks within each series using the frozen block length. The shipped settings use 1,000 draws and seed 20261007. The resulting percentile interval is descriptive and depends on appropriate dependence assumptions; 59 sunspot test years with 11-year blocks are a limited benchmark.

The registered forecasting hypothesis is supported **within that benchmark only** if relative MAE gain >= 5%, the descriptive 95% interval lower bound is positive, and the optional labelled-normal diagnostic alert constraint passes. With no normal labels, that constraint is explicitly unevaluated; no alert-reliability claim follows. An interval wholly below zero records predictive rejection. Other failures record lack of support or alert-rate rejection. All six models remain in the report; no best-baseline switching or post-hoc winner selection is performed.

The engine generates a revision decision: seek independent replication after support, or reject the tested advantage claim and retain EWMA as the working alternative. It never silently retunes the frozen run. A changed model needs a new protocol and new test observations. No parameter search is conducted in the shipped release.

## Known limitations

- AR(1), EWMA, persistence, empirical bands and resampling are established methods. This package does not establish algorithmic novelty.
- ME-047 is sensitive to a change in the origin of the measurement scale. A common additive shift can change coherence; positive rescaling with epsilon rescaled preserves it, apart from numerical floors. Meaningful coordinate conventions must be specified per application.
- A high coherence value is a numerical similarity, not truth, consciousness, reliability probability, or physical validation.
- The physical eleven-sector atlas provides a reference and coverage audit. No justified mapping from these univariate observations to physical FieldSpace sectors is assumed.
- No compute-cost advantage, failure lead-time advantage, independent replication, generalization to arbitrary systems or fifth force is established.
- Hashes detect mismatches against retained receipts, not a malicious author who rewrites every hash. Local timestamps are not trusted timestamps. Independent prospective studies require independent custody and publication of the freeze/tickets.
- Three predetermined datasets are reported individually. Searching across further datasets would require accounting for selection and multiplicity before making a general claim.
