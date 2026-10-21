"""HTML Report Generation for Network Troubleshooting Sessions."""

import html
import json
from typing import Any
from diagnostics.models import DiagnosticSession, TestStatus


def generate_html_report(session: DiagnosticSession) -> str:
    """Generates an executive, print-ready, professional HTML diagnostic report."""

    # Escape dynamic inputs
    symptom_esc = html.escape(session.user_symptom)
    host_esc = html.escape(session.target_host or "N/A")
    port_esc = html.escape(str(session.target_port or "N/A"))
    session_id_esc = html.escape(session.session_id)
    start_time_esc = html.escape(session.start_time)
    end_time_esc = html.escape(session.end_time or "In progress")
    mode_badge = '<span class="badge badge-sim">SIMULATION LAB</span>' if session.is_simulated else '<span class="badge badge-live">LIVE ENVIRONMENT</span>'

    # Top Root Cause
    top_cause_html = ""
    if session.hypotheses:
        top_h = session.hypotheses[0]
        top_cause_html = f"""
        <div class="card card-alert">
            <div class="card-header">
                <h3>Primary Probable Root Cause: {html.escape(top_h.title)}</h3>
                <span class="badge badge-{top_h.confidence.value.lower()}">{html.escape(top_h.confidence.value)} CONFIDENCE ({int(top_h.confidence_score * 100)}%)</span>
            </div>
            <p><strong>Diagnosis:</strong> {html.escape(top_h.probable_root_cause)}</p>
            <p><strong>Recommended Action:</strong> {html.escape(top_h.suggested_corrective_action)}</p>
        </div>
        """
    else:
        top_cause_html = "<p>No conclusive root cause identified.</p>"

    # Tests Table Rows
    test_rows = []
    for test in session.test_results:
        status_class = f"status-{test.status.value.lower()}"
        evidence_list = "".join(f"<li>{html.escape(e)}</li>" for e in test.evidence)
        test_rows.append(f"""
        <tr>
            <td><strong>{html.escape(test.test_name)}</strong><br><small>{html.escape(test.stage.value)}</small></td>
            <td><span class="status-pill {status_class}">{html.escape(test.status.value)}</span></td>
            <td>{html.escape(test.human_explanation)}</td>
            <td><ul class="evidence-list">{evidence_list}</ul></td>
        </tr>
        """)
    test_table_html = "".join(test_rows)

    # Recommendations Rows
    rec_cards = []
    for rec in session.recommendations:
        steps_html = "".join(f"<li>{html.escape(s)}</li>" for s in rec.steps_to_follow)
        rec_cards.append(f"""
        <div class="rec-card">
            <h4>{html.escape(rec.observed_issue)}</h4>
            <p><em>{html.escape(rec.why_it_helps)}</em></p>
            <strong>Steps to remediate:</strong>
            <ol>{steps_html}</ol>
            <p><strong>Verification:</strong> {html.escape(rec.how_to_verify)}</p>
            <p><small><strong>Caution:</strong> {html.escape(rec.risks_and_limitations)}</small></p>
        </div>
        """)
    recs_html = "".join(rec_cards)

    # Verification outcome
    verif_html = ""
    if session.verification_outcome:
        verif_html = f"""
        <div class="verification-box">
            <h4>Remediation Verification Result: <span>{html.escape(session.verification_outcome.value)}</span></h4>
            <p>{html.escape(session.verification_notes or 'Diagnostic checks re-evaluated after user remediation attempt.')}</p>
        </div>
        """

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Network Diagnostic Report - {session_id_esc}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 30px;
        }}
        .container {{
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        .header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 26px;
            color: #0f172a;
        }}
        .badge {{
            padding: 6px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge-live {{ background-color: #e0f2fe; color: #0369a1; }}
        .badge-sim {{ background-color: #fef3c7; color: #b45309; }}
        .badge-high {{ background-color: #fee2e2; color: #b91c1c; }}
        .badge-medium {{ background-color: #ffedd5; color: #c2410c; }}
        .badge-low {{ background-color: #f1f5f9; color: #475569; }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 30px;
            background-color: #f1f5f9;
            padding: 18px;
            border-radius: 6px;
            font-size: 14px;
        }}
        .card-alert {{
            background-color: #fff1f2;
            border-left: 6px solid #e11d48;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .card-header h3 {{
            margin: 0;
            color: #9f1239;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #f8fafc;
            color: #475569;
        }}
        .status-pill {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-pass {{ background-color: #dcfce7; color: #15803d; }}
        .status-fail {{ background-color: #fee2e2; color: #b91c1c; }}
        .status-warning {{ background-color: #fef9c3; color: #a16207; }}
        .status-skipped {{ background-color: #f1f5f9; color: #64748b; }}
        .status-error {{ background-color: #fce7f3; color: #be185d; }}
        .evidence-list {{
            margin: 0;
            padding-left: 18px;
            font-size: 12px;
            color: #475569;
        }}
        .rec-card {{
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 15px;
        }}
        .rec-card h4 {{
            margin-top: 0;
            color: #0284c7;
        }}
        .verification-box {{
            background-color: #ecfdf5;
            border: 1px solid #6ee7b7;
            padding: 15px;
            border-radius: 6px;
            margin-top: 25px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
            color: #94a3b8;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Network Diagnostic Report</h1>
                <small>Session ID: {session_id_esc}</small>
            </div>
            <div>{mode_badge}</div>
        </div>

        <div class="meta-grid">
            <div><strong>Symptom:</strong> {symptom_esc}</div>
            <div><strong>Target Host:</strong> {host_esc}:{port_esc}</div>
            <div><strong>Execution Date:</strong> {start_time_esc}</div>
        </div>

        <h2>Diagnostic Assessment</h2>
        {top_cause_html}

        <h2>Executed Tests & Evidence</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 25%;">Test Stage</th>
                    <th style="width: 12%;">Status</th>
                    <th style="width: 33%;">Observed Findings</th>
                    <th style="width: 30%;">Technical Evidence</th>
                </tr>
            </thead>
            <tbody>
                {test_table_html}
            </tbody>
        </table>

        <h2>Actionable Remediations</h2>
        {recs_html}

        {verif_html}

        <div class="footer">
            Generated autonomously by Network Troubleshooting Assistant &bull; Read-only diagnostics &bull; RFC compliant
        </div>
    </div>
</body>
</html>"""
    return html_template
