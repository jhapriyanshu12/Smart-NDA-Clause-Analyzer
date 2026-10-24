# Smart NDA Clause Analyzer — Groq Edition

A student-built Python and Gradio prototype for preliminary NDA text review. It supports PDF, DOCX, and TXT extraction, Groq-assisted clause analysis, document Q&A, version comparison, and PDF report export.

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10 or newer (Python 3.11 is a good choice)
- Internet connection for Groq API requests
- A Groq API key from [Groq Console](https://console.groq.com/keys)

## Setup on Windows / VS Code

1. Extract this ZIP. In VS Code, choose **File → Open Folder** and open the extracted `Smart-NDA-Analyzer` folder.
2. Open **Terminal → New Terminal**. Check that `dir` shows `app.py` and `requirements.txt`.
3. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
4. Install dependencies:
   ```powershell
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
5. Create a file named `.env` in the same folder. Copy the contents of `.env.example` into it and replace `paste_your_key_here` with your private Groq API key. Keep the `GROQ_MODEL` line unless that model is unavailable for your account.
6. Start the app:
   ```powershell
   .venv\Scripts\python.exe app.py
   ```
7. Open the local URL printed in the terminal, usually `http://127.0.0.1:7860`.

If you already have a `.venv` folder, you do not need to create it again. Run the install command above from the project folder.

## API key and privacy

Create a key at [Groq Console](https://console.groq.com/keys). Check Groq's current pricing, usage limits, and data-handling terms before use. Free-tier access and rate limits can change. Never commit `.env` or share your API key; `.gitignore` excludes `.env`.

The text of uploaded documents is sent to Groq's API for processing. Use the included fictional sample NDA for your college demonstration. Do not upload confidential or real legal documents unless you have permission and have reviewed the provider's current data-handling terms.

## Features

- PDF, DOCX, and TXT text extraction
- Preliminary clause risk review and missing/unclear provision checklist
- Questions about the loaded NDA
- Comparison of two NDA versions
- Downloadable PDF review report

## Limitations

This is an educational prototype, not a legal service. AI output can be incomplete or inaccurate and is not legal advice. It does not determine whether an agreement is enforceable. Scanned PDFs need OCR, which is not included. Documents are limited to 45,000 extracted characters and 15 MB per upload in the interface. Review the report and consult a qualified legal professional before relying on any finding or signing an agreement.
