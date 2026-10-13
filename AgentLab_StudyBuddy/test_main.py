"""Automated tests for AgentLab StudyBuddy's offline functions."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import main


class StudyBuddyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp.name)
        self.notes_original = main.NOTES_FILE
        self.quiz_original = main.QUIZ_FILE
        self.history_original = main.HISTORY_FILE
        main.NOTES_FILE = self.temp_path / "study_notes.md"
        main.QUIZ_FILE = self.temp_path / "quiz_bank.csv"
        main.HISTORY_FILE = self.temp_path / "progress.csv"
        main.NOTES_FILE.write_text("# RAG\\nRetrieval helps answer questions.\\n", encoding="utf-8")
        with main.QUIZ_FILE.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=[
                "question", "A", "B", "C", "D", "answer", "explanation"
            ])
            writer.writeheader()
            writer.writerow({
                "question": "What does RAG stand for?",
                "A": "Retrieval-Augmented Generation",
                "B": "Random Agent Game",
                "C": "Rapid Audio Generator",
                "D": "None of these",
                "answer": "A",
                "explanation": "It retrieves context for generation.",
            })

    def tearDown(self):
        main.NOTES_FILE = self.notes_original
        main.QUIZ_FILE = self.quiz_original
        main.HISTORY_FILE = self.history_original
        self.temp.cleanup()

    def test_load_notes(self):
        self.assertIn("Retrieval helps", main.load_notes())

    def test_load_question_bank(self):
        questions = main.load_questions()
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["answer"], "A")

    def test_record_and_read_progress(self):
        main.record_result(1, 1, [])
        self.assertTrue(main.HISTORY_FILE.exists())
        with main.HISTORY_FILE.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]["score"], "1")
        self.assertEqual(rows[0]["total"], "1")

    def test_quiz_invalid_count_does_not_crash(self):
        with patch("builtins.input", return_value="not-a-number"), patch("builtins.print"):
            main.take_quiz()

    def test_quiz_retries_invalid_answer_then_records_score(self):
        answers = iter(["1", "Z", "A"])
        with patch("builtins.input", side_effect=lambda _prompt="": next(answers)), patch("builtins.print"):
            main.take_quiz()
        with main.HISTORY_FILE.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[-1]["score"], "1")

    def test_missing_progress_is_handled(self):
        with patch("builtins.print") as printer:
            main.show_progress()
        printer.assert_called()


if __name__ == "__main__":
    unittest.main()
