# Smart NDA Clause Analyzer

## About the Project
The Smart NDA Clause Analyzer is an application based on Python which analyzes Non-Disclosure Agreements. It utilizes the AI to detect clauses that can require more analysis from the user.
- I developed this project to practice more Python programming language, using AI APIs and applications development using Gradio.

## Features
- Uploading NDA documents in formats such as PDF, DOCX and TXT.
- Analysis of NDA Clauses and detection of possible risks.
- Making inquiries about the document.
- Comparing two documents.
- User-friendly GUI built using Gradio.

## Technologies Used
- Python
- Gradio
- Groq API

## How to run the Project
1. Clone/download this repository to your system.
2. Open the project folder in VS Code.
3. Install all the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project directory.
5. Add your Groq API KEY in .env:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

6. Start the application by executing `app.py` script:
   ```bash
   python app.py
   ```
7. Access the application via the local link in the console.

## Important Information
It should be noted that the project serves educational and training purposes. The

## Limitations
This is an educational prototype, not a legal service. AI output can be incomplete or inaccurate and is not legal advice. It does not determine whether an agreement is enforceable. Scanned PDFs need OCR, which is not included. Documents are limited to 45,000 extracted characters and 15 MB per upload in the interface. Review the report and consult a qualified legal professional before relying on any finding or signing an agreement.

## Developer
**JHA PRIYANSHU**
