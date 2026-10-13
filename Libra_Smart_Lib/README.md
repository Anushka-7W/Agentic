# Libra Smart Library Assistant

A student-friendly library assistant built with Python, Streamlit, SQLite, and an optional Groq-powered language model. It demonstrates practical software development alongside an AI assistant interface.

## Features

- Search books by title, author, or category.
- Filter catalogue by category.
- Persistent SQLite catalogue and borrowing records.
- Borrowing and returns through explicit UI forms.
- Three active loans per borrower and a 14-day loan period.
- Overdue status based on due dates.
- Catalogue statistics and library guide.
- Optional AI-powered natural-language answers.
- Local search fallback when the AI key or service is unavailable.
- Automated unit tests.

> This is an educational demonstration using sample book data. It is not connected to a real college library and does not verify student identity.

## Project structure

```text
smart_library_assistant/
├── app.py
├── library_service.py
├── ai_agent.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── tests/
    └── test_library_service.py
```

## Requirements

- Python 3.10 or newer
- VS Code or another Python IDE
- Internet access only if you want to use the optional hosted Groq AI service

## Setup

1. Extract the ZIP and open the project folder in VS Code.
2. Create and activate a virtual environment:

   **Windows**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Optional AI setup:
   - Copy `.env.example` to `.env`.
   - Put your own Groq API key in `GROQ_API_KEY`.
   - Never commit `.env` or share the API key.

   The app can still run without a key; Ask Libra will use the local search fallback.

5. Start the application:

   ```bash
   streamlit run app.py
   ```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Run tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests use a temporary database and do not alter your normal `library.db`.

## Design overview

- `app.py` presents the Streamlit pages and forms.
- `library_service.py` contains catalogue and circulation rules and persists data in SQLite.
- `ai_agent.py` provides optional natural-language responses using Groq. The model receives the current catalogue as context.
- `tests/test_library_service.py` checks search, borrowing, return, limits, invalid IDs, duplicate loans, and persistence.

## Data model

**books** stores each title, author, category, and total number of copies.

**borrowings** stores borrower label, book ID, borrowing date, due date, and optional return date. An active loan has no return date.

Available copies are calculated from the number of active borrowing records rather than stored separately. This reduces the chance of stock counts drifting out of sync.

## Borrowing rules

- Maximum 3 active loans per borrower label.
- Loan duration is 14 days.
- A borrower cannot hold two active loans for the same title.
- A book cannot be borrowed if all copies are already checked out.
- Returns close a borrowing record and restore availability automatically.

## Limitations and future work

- The demo borrower label is not authentication; users can type any label.
- The catalogue starts with sample data, not a college's official inventory.
- AI answers depend on the configured model and API availability.
- Current AI chat context is not persisted after a browser session ends.
- A production deployment should add authentication, role-based access, audit logs, database migrations, rate limits, and stronger privacy controls.

## Academic use

Use this project to learn and explain the design. Review the code, run the tests, take screenshots of your own running application, and adapt the catalogue or features to your assignment requirements. Be prepared to explain the database schema, borrowing validation, and AI fallback.
