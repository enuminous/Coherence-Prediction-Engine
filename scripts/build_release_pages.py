"""Build the release overview from actual stored outcomes, never from expected wins."""
import json
import sys
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cpe.report import STYLE,fmt

def main():
    summaries=json.loads((ROOT/'runs/all_results.json').read_text())
    labels={'control_drift':'Synthetic drift','control_null':'Synthetic null','sunspots':'Historical sunspots'}
    table=[];md=[]
    for name,s in summaries.items():
        p=s['primary'];ci=p['uncertainty']['mean_gain_95pct_interval']
        cells=[labels[name],str(s['n']),fmt(s['models']['cpe']['mae']),fmt(s['models']['ewma']['mae']),fmt(p['relative_gain'],True),p['disposition'].replace('_',' ')]
        table.append('<tr>'+''.join(f'<td>{escape(c)}</td>' for c in cells)+f'<td><a href="runs/{name}/report.html">Open report</a></td></tr>')
        md.append('| '+' | '.join(cells)+' |')
    content='''# Release results — v0.1.0

All three predeclared experiments were retained. **No experiment met the registered acceptance criteria.** No predictor parameter, threshold or comparison was tuned after these results were observed.

| Experiment | Test observations | CPE MAE | Matched EWMA MAE | Relative gain | Disposition |
|---|---:|---:|---:|---:|---|
'''+ '\n'.join(md)+'''

Positive gain favors CPE. The registered minimum was +5%, together with a positive descriptive uncertainty lower bound and the applicable diagnostic alert constraint.

The drift candidate was approximately 15.52% worse than matched EWMA by MAE. Its mean-gain interval lay entirely below zero. Persistence also outperformed both in this fixture. The null candidate's gain was approximately 0.072%; its interval crossed zero. Synthetic labelled-normal alert rates were 17.33% (drift) and 18.40% (null), exceeding the registered 10% ceiling. The alert diagnostic is shared by the matched models; this failure limits that diagnostic, not just the gate.

On 59 held-out historical sunspot years, the candidate's MAE gain was approximately 0.041%, well below 5%, with an interval crossing zero. Its nominal 90% empirical band covered approximately 74.58% of test outcomes. The no-memory ablation had lower error in this particular dataset; that exploratory observation is not a new independently confirmed winner. Event labels were unavailable, so alert rates are unevaluated.

## Software verification

21 contract tests pass. They cover forecast causality, unchanged training/calibration under future-data changes, preservation of failures, input and source freeze mismatches, ledger tampering, correct handling of missing labels, standalone ticket resolution, recurrence bounds, and the distinction between triple coverage and higher-order dynamics. See `validation/tests.log`.

## Evidence disposition

- Demonstrated: runnable causal prediction/observation/scoring workflow, evidence records and combinatorial atlas checks.
- Rejected or unsupported in these benchmarks: the registered 5% coherence-gating advantage.
- Unresolved: independent prospective replication, adequate real-application calibration, the full ME-102 empirical gate, physical dynamics for the reference atlas, and broader physical claims.

The correct experimental action is to retain the matched conventional alternative, preserve these failed candidate results, and formulate any revised candidate in a new frozen experiment using new test observations. A functioning engine can reject its own candidate model.

## Reproduction

Run `python scripts/run_release.py my-reproduction` from the extracted folder. It creates a new set of complete run directories. Source or data changes invalidate old receipts. Each run can be checked with `python -m cpe verify RUN_DIRECTORY`.
'''
    (ROOT/'RELEASE_RESULTS.md').write_text(content,encoding='utf-8')
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Coherence Prediction Engine</title><style>{STYLE}
    .hero{{padding:20px 0 18px}}.hero p{{font-size:19px;max-width:760px}}.nav{{display:flex;gap:16px;flex-wrap:wrap;margin:22px 0 40px}}.button{{padding:10px 18px;border:1px solid var(--line);border-radius:8px;text-decoration:none}}.primary{{background:var(--accent);color:#102033;font-weight:700}}.four{{grid-template-columns:repeat(auto-fit,minmax(160px,1fr))}}.banner{{border-left:3px solid #f2c56e;padding:10px 22px;background:#24283a;margin:30px 0}}.flow{{display:flex;flex-wrap:wrap;gap:10px}}.flow span{{border:1px solid var(--line);padding:8px 12px;border-radius:6px}}td{{white-space:normal}}pre{{overflow:auto;padding:20px;background:#122235;border-radius:10px}}pre code{{background:transparent;padding:0}}@media(max-width:600px){{main{{padding:28px 18px}}.hero p{{font-size:17px}}}}
    </style></head><body><main><section class="hero"><div class="eyebrow">Monolithic · Research software · v0.1.0</div><h1>Coherence<br>Prediction Engine</h1><p>Forecasts you can challenge. A working loop for predictions, baseline comparisons, auditable failures and the next experimental decision.</p><div class="nav"><a class="button primary" href="README.md">Quick start</a><a class="button" href="docs/METHOD.md">Exact method</a><a class="button" href="RELEASE_RESULTS.md">Release findings</a></div></section>
    <div class="grid four"><div class="card"><span class="small">Source equation catalogue</span><strong class="big">102</strong>Explicit implementation status</div><div class="card"><span class="small">Three-sector combinations</span><strong class="big">165</strong>Exhaustive coverage audit</div><div class="card"><span class="small">Registered predictors</span><strong class="big">6</strong>One matched primary comparison</div><div class="card"><span class="small">Software contract tests</span><strong class="big">21 passed</strong>Causality, integrity and scope</div></div>
    <h2>The experimental loop</h2><div class="flow"><span>Specify</span><span>Freeze</span><span>Predict</span><span>Observe</span><span>Compare</span><span>Ablate</span><span>Record</span><span>Retain or reject</span></div>
    <p>Python 3.10+, no runtime dependencies. The core produces one-step forecasts from prior observations. Separate forecast tickets support scoring outcomes after they arrive.</p>
    <div class="banner"><strong>Release finding: the tested advantage was not established.</strong><p>The first coherence-gated candidate did not meet the registered acceptance criteria. All three experiments, including their failures and revision decisions, remain in this package.</p></div>
    <h2>Every registered benchmark</h2><div class="scroll"><table><thead><tr><th>Experiment</th><th>Test n</th><th>CPE MAE</th><th>EWMA MAE</th><th>Gain</th><th>Result</th><th>Evidence</th></tr></thead><tbody>{''.join(table)}</tbody></table></div><p class="small">Positive gain favors CPE. A 5% gain and the frozen uncertainty/diagnostic conditions were required. The public sunspot data are retrospective observations; the other two datasets are related synthetic fixtures.</p>
    <h2>Four connected components</h2><div class="grid"><div class="card"><strong>EFMW / Monolithic</strong><p>Executable ME-047 scalar coherence plus the original 102-entry reference map. The forecast gate is an experimental design choice.</p><a href="cpe/registry/equations.json">Equation bindings</a></div><div class="card"><strong>Zoo / TORTOISE</strong><p>A source-grounded regression adapter for freezing, predicting, scoring and ablating. Independent replication remains a separate obligation.</p><a href="cpe/registry/zoo_operations.json">Operation contract</a></div><div class="card"><strong>FieldSpace atlas</strong><p>All three-element subsets of eleven sector labels. Higher-order gaps are reported explicitly; physical dynamics are not inferred from counts.</p><a href="cpe/registry/atlas_165.json">165 entries</a></div><div class="card"><strong>Evidence and revision</strong><p>Source and data identities, sequential forecasts, outcomes, matched comparisons and a rule-based next-experiment recommendation.</p><a href="docs/INTEGRATION_AND_GAPS.md">Integration and gaps</a></div></div>
    <h2>Run locally</h2><pre><code>python -m unittest discover -s tests -v
python -m cpe verify runs/sunspots
python scripts/run_release.py my-reproduction</code></pre>
    <p><a href="docs/DATA_AND_PROTOCOL.md">Use your observations</a> · <a href="docs/PROOF_OBLIGATIONS.md">Proof obligations</a> · <a href="references/PROVENANCE.md">Source provenance</a> · <a href="validation/tests.log">Test record</a></p>
    <footer>Matthew Chenoweth Wright / Monolithic · October 7, 2026<br>A bounded science-engine prototype. Software checks, mathematical statements and physical evidence retain distinct statuses. ME-102 remains an open empirical gate.</footer></main></body></html>'''
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    print('Built index.html and RELEASE_RESULTS.md from the complete result set.')

if __name__=='__main__': main()
