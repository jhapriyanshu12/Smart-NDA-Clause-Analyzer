import os
import gradio as gr
from dotenv import load_dotenv

from analyzer import (
    analyze_nda,
    answer_nda_question,
    compare_ndas,
    extract_document_text,
)
from report_generator import create_report

load_dotenv()

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


with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # Smart NDA Clause Analyzer
        **A student-built tool for preliminary contract review**

        Upload a Non-Disclosure Agreement to review clauses, spot items that may need attention,
        ask questions about the text, and export a report.
        """
    )

    with gr.Tab("Review an NDA"):
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
            version_a = gr.File(label="Original version", file_types=[".pdf", ".docx", ".txt"], type="filepath")
            version_b = gr.File(label="Revised version", file_types=[".pdf", ".docx", ".txt"], type="filepath")
        compare_button = gr.Button("Compare documents", variant="primary")
        compare_output = gr.Markdown()
        compare_button.click(compare_uploads, inputs=[version_a, version_b], outputs=[compare_output])

    run_button.click(
        analyze_upload,
        inputs=[upload],
        outputs=[analysis_state, output, download, status, document_state, chatbot],
    )

    gr.Markdown(
        """
        ---
        **Privacy and limitations:** The document text is sent to Groq's API for processing.
        Do not upload confidential material unless you are authorized and have reviewed the provider's
        data-handling terms. This prototype does not provide guaranteed deletion, OCR, or legal advice.
        """
    )


if __name__ == "__main__":
    demo.launch()
