"""PDF Report Generator using ReportLab with clean fallback handling."""

import io
from typing import Optional
from diagnostics.models import DiagnosticSession


def generate_pdf_report(session: DiagnosticSession) -> Optional[bytes]:
    """
    Generates a clean PDF diagnostic report bytes using ReportLab.
    Returns bytes or None if ReportLab is missing/fails without crashing.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=6
        )

        meta_style = ParagraphStyle(
            'MetaStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=12
        )

        heading2_style = ParagraphStyle(
            'Heading2Style',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#334155'),
            spaceAfter=4
        )

        bold_style = ParagraphStyle(
            'BoldStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0f172a')
        )

        # Header
        mode_text = "SIMULATION LAB" if session.is_simulated else "LIVE ENVIRONMENT"
        story.append(Paragraph("Network Troubleshooting Assistant - Diagnostic Report", title_style))
        story.append(Paragraph(f"Session ID: {session.session_id} | Mode: {mode_text} | Date: {session.start_time}", meta_style))
        story.append(Spacer(1, 8))

        # Meta table
        meta_data = [
            [Paragraph("<b>Symptom:</b>", bold_style), Paragraph(session.user_symptom, body_style)],
            [Paragraph("<b>Target Host:</b>", bold_style), Paragraph(f"{session.target_host or 'N/A'}:{session.target_port or 'N/A'}", body_style)],
        ]
        meta_table = Table(meta_data, colWidths=[100, 440])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 12))

        # Primary Diagnosis
        story.append(Paragraph("Primary Diagnostic Assessment", heading2_style))
        if session.hypotheses:
            top_h = session.hypotheses[0]
            diag_text = f"<b>{top_h.title}</b> ({top_h.confidence.value} Confidence)<br/>{top_h.probable_root_cause}<br/><br/><b>Action:</b> {top_h.suggested_corrective_action}"
            diag_p = Paragraph(diag_text, body_style)
            diag_table = Table([[diag_p]], colWidths=[540])
            diag_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fff1f2')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f43f5e')),
                ('PADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(diag_table)
        else:
            story.append(Paragraph("No conclusive root cause identified.", body_style))

        story.append(Spacer(1, 12))

        # Executed Tests
        story.append(Paragraph("Executed Diagnostic Checks & Evidence", heading2_style))
        test_rows = [
            [Paragraph("<b>Stage</b>", bold_style),
             Paragraph("<b>Status</b>", bold_style),
             Paragraph("<b>Observation</b>", bold_style),
             Paragraph("<b>Evidence</b>", bold_style)]
        ]

        for t in session.test_results:
            ev_summary = "<br/>".join([f"• {e}" for e in t.evidence[:2]])
            test_rows.append([
                Paragraph(t.test_name, body_style),
                Paragraph(t.status.value, bold_style),
                Paragraph(t.human_explanation, body_style),
                Paragraph(ev_summary, body_style)
            ])

        test_table = Table(test_rows, colWidths=[130, 50, 180, 180])
        test_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(test_table)
        story.append(Spacer(1, 12))

        # Recommendations
        if session.recommendations:
            story.append(Paragraph("Actionable Recommendations", heading2_style))
            for rec in session.recommendations[:2]:
                rec_steps = "<br/>".join([f"{i+1}. {s}" for i, s in enumerate(rec.steps_to_follow)])
                rec_content = f"<b>{rec.observed_issue}</b><br/>{rec_steps}<br/><i>Verify: {rec.how_to_verify}</i>"
                rec_p = Paragraph(rec_content, body_style)
                rec_box = Table([[rec_p]], colWidths=[540])
                rec_box.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
                    ('PADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(rec_box)
                story.append(Spacer(1, 6))

        # Verification if present
        if session.verification_outcome:
            story.append(Spacer(1, 8))
            v_text = f"<b>Verification Outcome:</b> {session.verification_outcome.value}<br/>{session.verification_notes or ''}"
            v_p = Paragraph(v_text, body_style)
            v_box = Table([[v_p]], colWidths=[540])
            v_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ecfdf5')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#10b981')),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(v_box)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    except Exception:
        return None
