"""Optional Groq tool-calling layer; local catalogue still works without it."""
import json
import os

class LibraryAIAgent:
    def __init__(self, service):
        self.service = service
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("Install the groq package to enable AI mode") from exc
        self.client = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    def respond(self, prompt):
        # The model is used for intent interpretation and grounded catalogue responses.
        # Borrowing mutations are intentionally handled through explicit UI forms.
        catalogue = self.service.list_books()
        context = json.dumps(catalogue, ensure_ascii=False)
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {"role":"system","content":(
                        "You are Libra, a careful college library assistant. Answer using only the supplied catalogue "
                        "and the library rules: maximum 3 active loans per borrower, 14-day loan. Never claim a book "
                        "was borrowed or returned; those actions must be completed in the circulation page. If no "
                        "match is present, say so. Be concise and helpful. Current catalogue JSON follows:\n" + context
                    )},
                    {"role":"user","content":prompt}
                ]
            )
            return completion.choices[0].message.content or self.service.answer_without_ai(prompt)
        except Exception:
            return self.service.answer_without_ai(prompt) + "\n\n*The AI service was unavailable, so I used local search.*"
