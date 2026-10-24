import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

# Load configuration from the app folder, falling back to its parent folder.
PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"
if not ENV_FILE.exists():
    ENV_FILE = PROJECT_DIR.parent / ".env"
load_dotenv(ENV_FILE)

from analyzer import (
    analyze_nda,
    answer_nda_question,
    compare_ndas,
    extract_document_text,
)
from report_generator import create_report

APP_TITLE = "Smart NDA Clause Analyzer"
MAX_UPLOAD_MB = 15


def _read_upload(file_path):
    if not file_path:
        raise ValueError("Upload an NDA document first.")
    if not os.path.isfile(file_path):
        raise ValueError("The uploaded file could not be found.")
    if os.path.getsize(file_path) > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"Please upload a file smaller than {MAX_UPLOAD_MB} MB.")
    return extract_document_text(file_path)


def analyze_upload(file_path):
    try:
        text = _read_upload(file_path)
        result = analyze_nda(text)
        report_path = create_report(result)
        return (
            result,
            render_report(result),
            report_path,
            f"Analysis completed. Extracted {len(text):,} characters. Please verify the cited text.",
            text,
            [],
        )
    except Exception as exc:
        return None, "", None, f"Could not analyze the document: {exc}", "", []


def render_report(result):
    if not result:
        return ""
    parts = [
        "# NDA review",
        f"**Overall review priority:** {result.get('overall_priority', 'Not assessed')}",
        f"**Why:** {result.get('priority_reason', 'Not provided')}",
        "",
        "## Summary",
        result.get("summary", "No summary returned."),
        "",
        "## Clause findings",
    ]
    findings = result.get("findings", [])
    if not findings:
        parts.append("No findings were returned. This does not mean the agreement is risk-free.")
    for number, item in enumerate(findings, 1):
        parts.extend([
            f"### {number}. {item.get('clause_type', 'Clause')}",
            f"**Priority:** {item.get('risk_level', 'Not assessed')}",
            f"**Evidence from the document:**",
            f"> {item.get('clause_text', 'No quotation supplied.')}",
            f"**Plain-English explanation:** {item.get('explanation', '')}",
            f"**Suggested next step:** {item.get('recommendation', '')}",
            "",
        ])
    parts.extend(["## Missing or unclear provisions", ""])
    missing = result.get("missing_or_unclear", [])
    if not missing:
        parts.append("No items were returned in this category. Completeness has not been established.")
    for item in missing:
        parts.append(f"- **{item.get('item', 'Item')}** — {item.get('reason', '')}")
    parts.extend(["", "## Questions for a reviewer", ""])
    for question in result.get("questions_for_reviewer", []):
        parts.append(f"- {question}")
    parts.extend([
        "",
        "---",
        "**Notice:** This is an AI-generated preliminary review, not legal advice. The model may be wrong or miss important details. Ask a qualified legal professional before relying on the findings or signing an agreement.",
    ])
    return "\n".join(parts)


def chat_turn(question, history, document_text):
    history = history or []
    if not document_text:
        return history + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": "Please analyze an NDA first."},
        ], ""
    if not question or not question.strip():
        return history, ""
    try:
        answer = answer_nda_question(document_text, question.strip(), history)
    except Exception as exc:
        answer = f"Unable to get an answer: {exc}"
    return history + [
        {"role": "user", "content": question.strip()},
        {"role": "assistant", "content": answer},
    ], ""


def compare_uploads(file_a, file_b):
    try:
        if not file_a or not file_b:
            return "Upload both versions of the NDA."
        text_a = _read_upload(file_a)
        text_b = _read_upload(file_b)
        return compare_ndas(text_a, text_b)
    except Exception as exc:
        return f"Comparison could not be completed: {exc}"


LANDING_CSS = """
.gradio-container {
    max-width: 1240px !important;
    margin: 0 auto !important;
}

.nda-hero {
    position: relative;
    overflow: hidden;
    text-align: center;
    padding: 62px 24px;
    border-radius: 26px;
    margin: 16px 0 34px;
    color: #f8fafc;
    background:
        radial-gradient(circle at 85% 10%, rgba(99, 102, 241, .58), transparent 34%),
        radial-gradient(circle at 8% 95%, rgba(14, 165, 233, .22), transparent 35%),
        linear-gradient(135deg, #0b1224 0%, #172554 60%, #312e81 100%);
    border: 1px solid rgba(148, 163, 184, .25);
}

.nda-hero .nda-badge {
    display: inline-block;
    padding: 8px 14px;
    border: 1px solid rgba(191, 219, 254, .4);
    border-radius: 999px;
    color: #dbeafe;
    background: rgba(15, 23, 42, .35);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.4px;
}

.nda-hero h1 {
    margin: 20px 0 16px;
    font-size: clamp(34px, 5vw, 58px);
    font-weight: 850;
    letter-spacing: -1.6px;
    line-height: 1.08;
    color: #ffffff;
}

.nda-hero p {
    max-width: 730px;
    margin: 0 auto 24px;
    color: #dbeafe;
    font-size: 17px;
    line-height: 1.75;
}

.nda-cta {
    display: inline-block;
    padding: 14px 23px;
    border-radius: 12px;
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: #ffffff !important;
    font-weight: 750;
    text-decoration: none !important;
    box-shadow: 0 10px 28px rgba(79, 70, 229, .28);
    transition: transform .2s ease, box-shadow .2s ease;
}

.nda-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 32px rgba(79, 70, 229, .38);
}

.nda-hero .nda-file-note {
    margin-top: 18px;
    margin-bottom: 0;
    color: #bfdbfe;
    font-size: 13px;
}

.nda-section-title {
    text-align: center;
    margin: 26px 0 8px;
}

.nda-section-subtitle {
    text-align: center;
    opacity: .76;
    margin: 0 auto 22px;
}

.nda-feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin: 22px 0 34px;
}

.nda-feature-card {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid var(--border-color-primary);
    background: var(--background-fill-secondary);
    min-height: 148px;
    transition: transform .2s ease, border-color .2s ease;
}

.nda-feature-card:hover {
    transform: translateY(-3px);
    border-color: #818cf8;
}

.nda-feature-card .feature-icon {
    font-size: 25px;
    margin-bottom: 12px;
}

.nda-feature-card h3 {
    margin: 0 0 8px;
    font-size: 17px;
}

.nda-feature-card p {
    margin: 0;
    opacity: .78;
    line-height: 1.6;
}

.nda-notice {
    border-radius: 14px;
    border: 1px solid var(--border-color-primary);
    padding: 15px 18px;
    margin-top: 28px;
    font-size: 13px;
    line-height: 1.65;
    opacity: .88;
}

#document-upload {
    scroll-margin-top: 24px;
}
"""

with gr.Blocks(title=APP_TITLE, css=LANDING_CSS) as demo:
    gr.HTML("""
    <section class="nda-hero">
        <div class="nda-badge">AI-POWERED LEGAL ASSISTANCE</div>
        <h1>Understand Your NDA<br>Before You Sign</h1>
        <p>
            Review confidentiality agreements, spot clauses that may need
            closer attention, ask questions about the wording, and compare
            document versions — all in one place.
        </p>
        <a class="nda-cta" href="#document-upload">Analyze My NDA &#8594;</a>
        <p class="nda-file-note">PDF · DOCX · TXT support · Maximum file size: 15 MB</p>
    </section>

    <h2 class="nda-section-title">Everything You Need for a First Review</h2>
    <p class="nda-section-subtitle">
        Practical AI-assisted tools to help you understand the document.
    </p>

    <section class="nda-feature-grid">
        <article class="nda-feature-card">
            <div class="feature-icon">&#128737;</div>
            <h3>Clause Risk Review</h3>
            <p>Highlight clauses that may deserve closer attention, with plain-English explanations.</p>
        </article>
        <article class="nda-feature-card">
            <div class="feature-icon">&#128172;</div>
            <h3>Ask Questions</h3>
            <p>Ask questions about an analyzed NDA and get answers grounded in its text.</p>
        </article>
        <article class="nda-feature-card">
            <div class="feature-icon">&#8644;</div>
            <h3>Compare Versions</h3>
            <p>Compare two document versions and review meaningful changes.</p>
        </article>
        <article class="nda-feature-card">
            <div class="feature-icon">&#128196;</div>
            <h3>Export a Report</h3>
            <p>Download a review report to save or discuss with a qualified professional.</p>
        </article>
    </section>
    """)

    gr.Markdown("## Start Analyzing Your Document")

    with gr.Column(elem_id="document-upload"):
        upload = gr.File(
            label="NDA document",
            file_types=[".pdf", ".docx", ".txt"],
            type="filepath",
        )
        run_button = gr.Button("Analyze document", variant="primary")
        status = gr.Markdown("Choose a PDF, DOCX, or TXT document to begin.")
        output = gr.Markdown()
        download = gr.File(label="Download report (PDF)")
        analysis_state = gr.State(None)
        document_state = gr.State("")
        chat_state = gr.State([])

    with gr.Tabs():
        with gr.Tab("Ask questions"):
            gr.Markdown("Analyze a document first, then ask questions about its wording.")
            chatbot = gr.Chatbot(label="Document Q&A", height=360)
            question = gr.Textbox(
                label="Question",
                placeholder="For example: How long do the confidentiality obligations last?",
            )
            ask_button = gr.Button("Ask", variant="primary")
            ask_button.click(
                chat_turn,
                inputs=[question, chatbot, document_state],
                outputs=[chatbot, question],
            )
            question.submit(
                chat_turn,
                inputs=[question, chatbot, document_state],
                outputs=[chatbot, question],
            )

        with gr.Tab("Compare versions"):
            gr.Markdown("Compare two versions to identify meaningful changes. Review the result manually.")
            with gr.Row():
                version_a = gr.File(
                    label="Original version",
                    file_types=[".pdf", ".docx", ".txt"],
                    type="filepath",
                )
                version_b = gr.File(
                    label="Revised version",
                    file_types=[".pdf", ".docx", ".txt"],
                    type="filepath",
                )
            compare_button = gr.Button("Compare documents", variant="primary")
            compare_output = gr.Markdown()
            compare_button.click(
                compare_uploads,
                inputs=[version_a, version_b],
                outputs=[compare_output],
            )

    run_button.click(
        analyze_upload,
        inputs=[upload],
        outputs=[analysis_state, output, download, status, document_state, chatbot],
    )

    gr.HTML("""
    <div class="nda-notice">
        <strong>Privacy and limitations:</strong> Document text is sent to Groq's API for processing.
        Do not upload confidential material unless you are authorized and have reviewed the provider's
        data-handling terms. This prototype does not guarantee deletion, provide OCR for scanned documents,
        or replace advice from a qualified legal professional. AI findings may be incomplete or incorrect.
    </div>
    """)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        theme=gr.themes.Soft()
    )

