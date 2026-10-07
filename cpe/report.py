"""Portable static reports; no external assets, scripts or trackers."""
from html import escape

STYLE = """
:root{color-scheme:dark;--ink:#e6edf5;--muted:#a8b8c9;--line:#2b4058;--accent:#54dcc4}
*{box-sizing:border-box}body{margin:0;background:#0c1725;color:var(--ink);font:16px/1.6 system-ui,sans-serif}
main{max-width:1120px;margin:auto;padding:48px 24px}h1{font-size:clamp(30px,5vw,52px);line-height:1.15;margin:10px 0 18px}
h2{font-size:24px;margin-top:38px}p{max-width:85ch;color:var(--muted)}a{color:var(--accent)}
.eyebrow{color:var(--accent);font-size:13px;letter-spacing:2px;text-transform:uppercase}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.card{border:1px solid var(--line);background:#122235;padding:22px;border-radius:12px}.big{display:block;font-size:28px;line-height:1.3;margin:8px 0}
.small{font-size:13px;color:var(--muted)}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;border-bottom:1px solid var(--line);padding:12px;white-space:nowrap}th{color:var(--accent)}
code{background:#172d43;padding:3px 6px;border-radius:4px}svg{width:100%;height:auto;background:#102033;border-radius:12px}
.status{display:inline-block;border:1px solid #d4b364;color:#f2d394;padding:5px 12px;border-radius:30px;font-size:14px}footer{margin-top:40px;border-top:1px solid var(--line);padding-top:20px;color:var(--muted);font-size:13px}
"""

def fmt(value, percent=False):
    if value is None:
        return "Not available"
    return f"{value:.2%}" if percent else f"{value:.5g}"

def sparkline(rows):
    first = rows[0]["series"]
    series = [r for r in rows if r["series"] == first]
    values = [r["y"] for r in series]+[r["predictions"]["cpe"] for r in series]
    lo,hi=min(values),max(values)
    span=hi-lo or 1
    def points(name):
        ys = [r["y"] if name=="observed" else r["predictions"][name] for r in series]
        return " ".join(f"{55+i*900/max(1,len(ys)-1):.2f},{235-(v-lo)*180/span:.2f}" for i,v in enumerate(ys))
    return f'''<svg viewBox="0 0 1010 295" role="img" aria-label="Observed and predicted values for {escape(first)}">
    <text x="55" y="30" fill="#a8b8c9" font-size="15">First series: {escape(first)} · test observations</text>
    <line x1="55" y1="235" x2="955" y2="235" stroke="#496177"/><text x="6" y="58" fill="#a8b8c9" font-size="12">{hi:.3g}</text>
    <text x="6" y="236" fill="#a8b8c9" font-size="12">{lo:.3g}</text>
    <polyline points="{points('observed')}" fill="none" stroke="#b5c5d6" stroke-width="1.7"/>
    <polyline points="{points('cpe')}" fill="none" stroke="#54dcc4" stroke-width="1.8"/>
    <text x="55" y="265" fill="#a8b8c9" font-size="13">{series[0]['time']:g}</text>
    <text x="900" y="265" fill="#a8b8c9" font-size="13">{series[-1]['time']:g}</text>
    <text x="325" y="281" fill="#b5c5d6" font-size="13">Observed</text><text x="480" y="281" fill="#54dcc4" font-size="13">CPE forecast</text></svg>'''

def render_report(summary,protocol,rows,revision):
    primary=summary["primary"]
    ci=primary["uncertainty"]["mean_gain_95pct_interval"]
    metric_rows="".join(f"<tr><td>{escape(name)}</td><td>{fmt(m['mae'])}</td><td>{fmt(m['rmse'])}</td><td>{fmt(m['bias'])}</td><td>{fmt(m['interval_coverage'],True)}</td><td>{fmt(m['mean_interval_width'])}</td></tr>" for name,m in summary["models"].items())
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{escape(protocol['id'])} · Coherence Prediction Engine</title><style>{STYLE}</style><main>
    <div class="eyebrow">Coherence Prediction Engine · v0.1.0</div><h1>A result you can inspect.</h1>
    <span class="status">{escape(primary['disposition'].replace('_',' '))}</span>
    <p>{escape(protocol['claim'])}</p><p>Evidence: <strong>{escape(protocol['dataset_kind'])}</strong>. This is a bounded forecasting evaluation. Physical validation and independent replication are not established by this run.</p>
    <div class="grid"><div class="card"><span class="small">CPE mean absolute error</span><strong class="big">{fmt(summary['models']['cpe']['mae'])}</strong>{escape(protocol['value_unit'])}</div>
    <div class="card"><span class="small">Gain versus matched EWMA</span><strong class="big">{fmt(primary['relative_gain'],True)}</strong>Positive favors CPE</div>
    <div class="card"><span class="small">Evaluation observations</span><strong class="big">{summary['n']:,}</strong>{summary['series']} series</div></div>
    <h2>Predictions and observations</h2>{sparkline(rows)}<p class="small">Forecasts use only preceding observations. Test observations update the streaming state after each forecast; model parameters and interval radii stay fixed.</p>
    <h2>All registered models</h2><div class="scroll"><table><thead><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>Bias</th><th>Band coverage</th><th>Band width</th></tr></thead><tbody>{metric_rows}</tbody></table></div>
    <p>Primary comparison: CPE versus matched EWMA. Required relative MAE gain: {fmt(protocol['min_relative_gain'],True)}; descriptive 95% interval for absolute gain: [{fmt(ci[0])}, {fmt(ci[1])}]. Method: {escape(primary['uncertainty']['method'])}. Other comparisons are diagnostic.</p>
    <h2>Calibration and failure records</h2><p>Nominal empirical band coverage: {fmt(1-protocol['alpha'],True)}. These bands have no distribution-free time-series coverage guarantee. Normal-row diagnostic alert rate: {fmt(summary['diagnostics']['normal_alert_rate'],True)}. Labels available for {fmt(summary['diagnostics']['label_coverage'],True)} of test rows. Missing labels are never counted as negatives.</p>
    <h2>Next experimental decision</h2><p><strong>{escape(revision['action'].replace('_',' '))}</strong>. {escape(revision['rationale'])} The tested version remains frozen. A revision requires a new protocol and new evaluation observations.</p>
    <p><a href="summary.json">Metrics</a> · <a href="predictions.csv">All predictions</a> · <a href="events.jsonl">Chronological event record</a> · <a href="freeze.json">Frozen protocol</a> · <a href="revision.json">Revision proposal</a> · <a href="audit.json">Audit</a></p>
    <footer>Protocol {escape(protocol['id'])} · Freeze {summary['freeze_hash']}<br>Local hashes provide integrity checks. They do not prove an independent observer, a trusted timestamp, or a law of nature.</footer></main></html>'''
