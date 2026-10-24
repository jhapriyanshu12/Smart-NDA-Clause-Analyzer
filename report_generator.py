import os
import tempfile
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def create_report(analysis):
    """Create a downloadable PDF report in a temporary directory."""
    folder = tempfile.mkdtemp(prefix="smart_nda_report_")
    output_path = os.path.join(folder, "nda_review_report.pdf")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle", parent=styles["Title"], alignment=TA_CENTER,
        textColor=colors.HexColor("#263B53"), spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle", parent=styles["Heading2"],
        textColor=colors.HexColor("#263B53"), spaceBefore=12, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="ReportBody", parent=styles["BodyText"], fontSize=9,
        leading=13, spaceAfter=6,
    ))

    def safe(value):
        return escape(str(value or "")).replace("\n", "<br/>")

    story = [
        Paragraph("Smart NDA Clause Analyzer", styles["CoverTitle"]),
        Paragraph("Preliminary AI-assisted review", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph(
            f"<b>Overall review priority:</b> {safe(analysis.get('overall_priority'))}",
            styles["ReportBody"],
        ),
        Paragraph(
            f"<b>Reason:</b> {safe(analysis.get('priority_reason'))}",
            styles["ReportBody"],
        ),
        Paragraph("Summary", styles["SectionTitle"]),
        Paragraph(safe(analysis.get("summary")), styles["ReportBody"]),
        Paragraph("Clause findings", styles["SectionTitle"]),
    ]

    findings = analysis.get("findings", [])
    if not findings:
        story.append(Paragraph(
            "No findings were returned. This does not establish that the NDA is risk-free.",
            styles["ReportBody"],
        ))

    for index, item in enumerate(findings, 1):
        story.extend([
            Paragraph(f"{index}. {safe(item.get('clause_type', 'Clause'))}", styles["Heading3"]),
            Paragraph(f"<b>Priority:</b> {safe(item.get('risk_level'))}", styles["ReportBody"]),
            Paragraph(f"<b>Evidence:</b> {safe(item.get('clause_text'))}", styles["ReportBody"]),
            Paragraph(f"<b>Explanation:</b> {safe(item.get('explanation'))}", styles["ReportBody"]),
            Paragraph(f"<b>Suggested next step:</b> {safe(item.get('recommendation'))}", styles["ReportBody"]),
        ])
        if item.get("quote_verified") is False:
            story.append(Paragraph(
                "<b>Evidence note:</b> The quotation did not match the extracted text exactly; verify it manually.",
                styles["ReportBody"],
            ))
        story.append(Spacer(1, 5))

    story.append(Paragraph("Missing or unclear provisions", styles["SectionTitle"]))
    missing_items = analysis.get("missing_or_unclear", [])
    if not missing_items:
        story.append(Paragraph(
            "No items were returned in this category. Completeness has not been established.",
            styles["ReportBody"],
        ))
    for item in missing_items:
        story.append(Paragraph(
            f"<b>{safe(item.get('item'))}:</b> {safe(item.get('reason'))}",
            styles["ReportBody"],
        ))

    story.append(Paragraph("Questions for a reviewer", styles["SectionTitle"]))
    for question in analysis.get("questions_for_reviewer", []):
        story.append(Paragraph("• " + safe(question), styles["ReportBody"]))

    story.extend([
        Spacer(1, 12),
        Paragraph(
            "<b>Notice:</b> This AI-generated report is for preliminary informational review only. "
            "It may be incomplete or inaccurate, is not legal advice, and does not determine whether "
            "an agreement is enforceable. Consult a qualified legal professional before relying on "
            "the findings or signing an agreement.",
            styles["ReportBody"],
        ),
    ])

    doc = SimpleDocTemplate(
        output_path, pagesize=A4, rightMargin=1.8 * cm, leftMargin=1.8 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    )
    doc.build(story)
    return output_path
