"""AgentLab StudyBuddy: an offline-first learning assistant for Agentic AI concepts."""
from __future__ import annotations

import csv
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTES_FILE = ROOT / "study_notes.md"
QUIZ_FILE = ROOT / "quiz_bank.csv"
HISTORY_FILE = ROOT / "progress.csv"


def load_notes() -> str:
    """Return the study notes, with a helpful message if the file is unavailable."""
    try:
        notes = NOTES_FILE.read_text(encoding="utf-8").strip()
        return notes or "The study notes file is empty."
    except OSError:
        return "Study notes could not be loaded. Check that study_notes.md exists."


def display_notes() -> None:
    print("\n" + "=" * 68)
    print("LEARNING GUIDE: AGENTIC AI")
    print("=" * 68)
    print(load_notes())
    print()


def search_notes() -> None:
    term = input("Enter a word or phrase to find: ").strip().casefold()
    if not term:
        print("Search cancelled: enter a non-empty phrase.")
        return
    matches = [
        line.strip().lstrip("#").strip()
        for line in load_notes().splitlines()
        if term in line.casefold() and line.strip()
    ]
    if matches:
        print("\nMatching note lines:")
        for line in matches:
            print(f"  • {line}")
    else:
        print(f"No matches found for {term!r}. Try a term such as 'agent' or 'prompt'.")


def load_questions() -> list[dict[str, str]]:
    """Load and validate multiple-choice questions from CSV."""
    questions: list[dict[str, str]] = []
    required = {"question", "A", "B", "C", "D", "answer", "explanation"}
    try:
        with QUIZ_FILE.open("r", newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                print("Quiz bank has an invalid header. Please check quiz_bank.csv.")
                return []
            for line_number, row in enumerate(reader, start=2):
                question = (row.get("question") or "").strip()
                answer = (row.get("answer") or "").strip().upper()
                options = {key: (row.get(key) or "").strip() for key in "ABCD"}
                if question and all(options.values()) and answer in options:
                    questions.append({
                        "question": question,
                        "A": options["A"], "B": options["B"],
                        "C": options["C"], "D": options["D"],
                        "answer": answer,
                        "explanation": (row.get("explanation") or "").strip(),
                    })
                else:
                    print(f"Skipping malformed quiz row at line {line_number}.")
    except OSError:
        print("Quiz bank could not be opened. Check that quiz_bank.csv exists.")
    return questions


def record_result(score: int, total: int, missed: list[str]) -> None:
    """Append a quiz attempt to local CSV history."""
    try:
        new_file = not HISTORY_FILE.exists()
        with HISTORY_FILE.open("a", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            if new_file:
                writer.writerow(["timestamp", "score", "total", "percentage", "missed_questions"])
            percentage = round(score * 100 / total) if total else 0
            writer.writerow([
                datetime.now().astimezone().isoformat(timespec="seconds"),
                score, total, percentage, " | ".join(missed),
            ])
    except OSError as exc:
        print(f"Note: your score could not be saved ({exc}).")


def take_quiz() -> None:
    bank = load_questions()
    if not bank:
        print("No valid quiz questions are available.")
        return
    raw_count = input(f"Number of questions (1–{len(bank)}, or Enter for all): ").strip()
    if raw_count == "":
        count = len(bank)
    else:
        try:
            count = int(raw_count)
        except ValueError:
            print("Please enter a whole number.")
            return
    if not 1 <= count <= len(bank):
        print(f"Choose a number between 1 and {len(bank)}.")
        return

    selected = random.sample(bank, count)
    score = 0
    missed: list[str] = []
    print("\nQuiz started. Choose A, B, C, or D.\n")
    for index, item in enumerate(selected, start=1):
        print(f"{index}. {item['question']}")
        for letter in "ABCD":
            print(f"   {letter}. {item[letter]}")
        while True:
            answer = input("Your answer: ").strip().upper()
            if answer in "ABCD" and len(answer) == 1:
                break
            print("Invalid answer. Enter A, B, C, or D.")
        if answer == item["answer"]:
            score += 1
            print("Correct.")
        else:
            missed.append(item["question"])
            print(f"Not quite. Correct answer: {item['answer']}. {item[item['answer']]}")
        if item["explanation"]:
            print(f"Explanation: {item['explanation']}")
        print()

    percent = round(score * 100 / len(selected))
    print(f"Final score: {score}/{len(selected)} ({percent}%)")
    if percent == 100:
        print("Excellent — every answer was correct.")
    elif percent >= 70:
        print("Good work. Review the explanations for any missed questions.")
    else:
        print("Review the learning guide, then try another quiz.")
    record_result(score, len(selected), missed)


def show_progress() -> None:
    try:
        with HISTORY_FILE.open("r", newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
    except FileNotFoundError:
        print("No attempts recorded yet. Complete a quiz to start your progress history.")
        return
    except OSError as exc:
        print(f"Could not read progress history: {exc}")
        return
    if not rows:
        print("No attempts recorded yet.")
        return
    print("\nYOUR RECENT PROGRESS")
    for row in rows[-10:]:
        print(f"{row.get('timestamp', 'Unknown date')} | "
              f"{row.get('score', '?')}/{row.get('total', '?')} "
              f"({row.get('percentage', '?')}%)")
        missed = row.get("missed_questions", "")
        if missed:
            print(f"  Review: {missed}")


def ask_ai_tutor() -> None:
    """Optional tutor using Groq. Offline learning tools do not depend on it."""
    try:
        from dotenv import load_dotenv
        from groq import Groq
    except ImportError:
        print("AI tutor dependencies are missing. Run: pip install -r requirements.txt")
        return

    import os
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        print("AI tutor is not configured. Copy .env.example to .env and add your API key.")
        return

    client = Groq(api_key=api_key)
    messages = [{
        "role": "system",
        "content": (
            "You are AgentLab StudyBuddy, a patient tutor for Agentic AI and software "
            "development. Use the supplied notes as the primary source. If you add "
            "outside knowledge, label it 'Extra context'. Be clear, accurate, concise, "
            "and encourage understanding rather than simply giving unexplained answers.\n\n"
            + load_notes()
        ),
    }]
    print("AI tutor ready. Type 'back' to return to the menu.")
    while True:
        prompt = input("\nYou: ").strip()
        if prompt.casefold() == "back":
            break
        if not prompt:
            continue
        messages.append({"role": "user", "content": prompt})
        try:
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
                messages=messages,
                temperature=0.3,
            )
            answer = response.choices[0].message.content or "No response was returned."
            print(f"\nStudyBuddy: {answer}\n")
            messages.append({"role": "assistant", "content": answer})
        except Exception as exc:
            messages.pop()
            print(f"AI request failed: {exc}")
            print("Check your network, API key, and configured model name.")


def main() -> None:
    options = {
        "1": ("Read learning guide", display_notes),
        "2": ("Take a knowledge quiz", take_quiz),
        "3": ("Search the guide", search_notes),
        "4": ("View quiz progress", show_progress),
        "5": ("Ask the optional AI tutor", ask_ai_tutor),
    }
    while True:
        print("\n" + "=" * 44)
        print("       AGENTLAB STUDYBUDDY")
        print("  Learn concepts. Test knowledge. Improve.")
        print("=" * 44)
        for key, (label, _) in options.items():
            print(f"{key}. {label}")
        print("0. Exit")
        choice = input("Select an option: ").strip()
        if choice == "0":
            print("Session complete. Keep learning!")
            return
        selected = options.get(choice)
        if selected:
            selected[1]()
        else:
            print("Invalid menu choice. Enter a number from 0 to 5.")


if __name__ == "__main__":
    main()
