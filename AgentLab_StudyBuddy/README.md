# AgentLab StudyBuddy — Agentic AI Learning Assistant

**Project domain:** Generative AI, AI agents, prompt engineering, RAG, tool calling, and responsible AI.

AgentLab StudyBuddy is an offline-first Python learning application. It includes a learning guide, randomized multiple-choice quiz, note search, local progress history, and an optional conversational AI tutor.

## Features

- **Learning guide:** Reads the course notes from `study_notes.md`.
- **Knowledge quiz:** Loads questions from `quiz_bank.csv`, randomizes them, validates answers, and provides explanations.
- **Search:** Finds terms in the learning guide.
- **Progress history:** Stores attempts and missed questions locally in `progress.csv`.
- **Optional AI tutor:** Uses the Groq API when configured. The offline features do not require an API key.
- **Input and file-error handling:** Provides helpful messages for invalid choices and missing or malformed data files.

## Requirements

- Python 3.10 or newer recommended.
- A terminal or command prompt.
- Internet access and a Groq API key only for the optional AI tutor.

## Run offline features

1. Extract the project folder.
2. Open a terminal in the `AgentLab_StudyBuddy` folder.
3. Run:

   ```bash
   python main.py
   ```

The notes, search, quiz, and progress features use the Python standard library.

## Enable the optional AI tutor

1. Install optional packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env`.
3. Add your own API key to `.env`. Never publish the `.env` file.
4. Run `python main.py` and choose option 5.

Model availability can change, so if the default model is unavailable, set `GROQ_MODEL` to a model currently available to your account.

## Project structure

```text
AgentLab_StudyBuddy/
├── main.py
├── study_notes.md
├── quiz_bank.csv
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── test_main.py
```

## Test the project

Run the automated tests:

```bash
python -m unittest -v
```

Also manually check:
- Choose option 1 to display the learning guide.
- Search for `RAG` using option 3.
- Take a quiz with a small number of questions and enter an invalid answer once.
- Choose option 4 before and after a quiz to inspect progress history.
- Choose option 5 without configuring an API key; the program should explain how to configure it.

## Design choices

The content is stored separately from application logic. This makes it possible to update the notes and quiz bank without editing the main Python program. Small functions separate loading, search, quiz delivery, persistence, and optional AI interaction. The AI feature is optional so the project remains useful when offline.

## Academic integrity and presentation

Before submitting, read the code, run the tests, adapt the project to the actual assignment rubric, and be ready to explain each feature. Add screenshots from your own run and describe any changes you personally make.
