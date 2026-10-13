"""SQLite-backed library catalogue and circulation service."""
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DEFAULT_BOOKS = [
    ("Python Crash Course", "Eric Matthes", "Programming", 5),
    ("Clean Code", "Robert C. Martin", "Software Engineering", 4),
    ("Computer Networks", "Andrew S. Tanenbaum", "Networking", 4),
    ("Database System Concepts", "Abraham Silberschatz", "Database", 3),
    ("Operating System Concepts", "Abraham Silberschatz", "Operating Systems", 4),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Algorithms", 3),
    ("Java: The Complete Reference", "Herbert Schildt", "Programming", 5),
    ("Artificial Intelligence: A Modern Approach", "Stuart Russell", "Artificial Intelligence", 3),
    ("Computer Organization and Design", "David A. Patterson", "Computer Science", 3),
    ("The Pragmatic Programmer", "Andrew Hunt", "Software Engineering", 4),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "Data Engineering", 2),
    ("Hands-On Machine Learning", "Aurélien Géron", "Machine Learning", 3),
]

class LibraryService:
    def __init__(self, db_path="library.db"):
        self.db_path = str(db_path)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self):
        with self._connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL,
                total INTEGER NOT NULL CHECK(total >= 0)
            );
            CREATE TABLE IF NOT EXISTS borrowings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL REFERENCES books(id),
                borrower TEXT NOT NULL,
                borrow_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                returned_date TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
            CREATE INDEX IF NOT EXISTS idx_borrowings_active ON borrowings(returned_date, borrower);
            """)
            count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            if count == 0:
                conn.executemany(
                    "INSERT INTO books(title,author,category,total) VALUES(?,?,?,?)",
                    DEFAULT_BOOKS
                )

    def list_books(self):
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT b.id,b.title,b.author,b.category,b.total,
                b.total - (SELECT COUNT(*) FROM borrowings r WHERE r.book_id=b.id AND r.returned_date IS NULL) AS available
                FROM books b ORDER BY b.title COLLATE NOCASE
            """).fetchall()
        return [dict(row) for row in rows]

    def categories(self):
        with self._connect() as conn:
            return [r[0] for r in conn.execute("SELECT DISTINCT category FROM books ORDER BY category")]

    def search_books(self, query="", category=None):
        books = self.list_books()
        words = (query or "").strip().casefold()
        results = []
        for book in books:
            haystack = f'{book["title"]} {book["author"]} {book["category"]}'.casefold()
            if words and words not in haystack:
                continue
            if category and book["category"] != category:
                continue
            results.append(book)
        return results

    def book_details(self, book_id):
        return next((b for b in self.list_books() if b["id"] == int(book_id)), None)

    def borrow_book(self, book_id, borrower="student", today=None):
        borrower = (borrower or "").strip()
        if not borrower:
            return {"success": False, "message": "Enter a borrower name or demo user ID."}
        today = today or date.today()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            book = conn.execute("SELECT * FROM books WHERE id=?", (int(book_id),)).fetchone()
            if not book:
                return {"success": False, "message": "That book ID does not exist."}
            active_for_user = conn.execute(
                "SELECT COUNT(*) FROM borrowings WHERE borrower=? AND returned_date IS NULL", (borrower,)
            ).fetchone()[0]
            if active_for_user >= 3:
                return {"success": False, "message": "Borrowing limit reached: one borrower may hold at most 3 books."}
            already_has_title = conn.execute(
                "SELECT COUNT(*) FROM borrowings WHERE book_id=? AND borrower=? AND returned_date IS NULL",
                (int(book_id), borrower)
            ).fetchone()[0]
            if already_has_title:
                return {"success": False, "message": "This borrower already has this title checked out."}
            active_count = conn.execute(
                "SELECT COUNT(*) FROM borrowings WHERE book_id=? AND returned_date IS NULL", (int(book_id),)
            ).fetchone()[0]
            if active_count >= book["total"]:
                return {"success": False, "message": f'"{book["title"]}" has no available copies.'}
            due = today + timedelta(days=14)
            conn.execute(
                "INSERT INTO borrowings(book_id,borrower,borrow_date,due_date) VALUES(?,?,?,?)",
                (int(book_id), borrower, today.isoformat(), due.isoformat())
            )
        return {"success": True, "message": f'"{book["title"]}" borrowed successfully.', "due_date": due.isoformat()}

    def return_book(self, borrowing_id):
        with self._connect() as conn:
            row = conn.execute("""
                SELECT r.id,b.title FROM borrowings r JOIN books b ON b.id=r.book_id
                WHERE r.id=? AND r.returned_date IS NULL
            """, (int(borrowing_id),)).fetchone()
            if not row:
                return {"success": False, "message": "Active borrowing record not found."}
            conn.execute("UPDATE borrowings SET returned_date=? WHERE id=?", (date.today().isoformat(), int(borrowing_id)))
        return {"success": True, "message": f'"{row["title"]}" returned successfully.'}

    def list_borrowings(self, borrower=None):
        query = """
            SELECT r.id AS borrowing_id,r.borrower,r.book_id,b.title,b.author,
                   r.borrow_date,r.due_date,r.returned_date
            FROM borrowings r JOIN books b ON b.id=r.book_id
            WHERE r.returned_date IS NULL
        """
        params = []
        if borrower:
            query += " AND lower(r.borrower)=lower(?)"
            params.append(borrower)
        query += " ORDER BY r.due_date"
        today = date.today().isoformat()
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["overdue"] = item["due_date"] < today
            result.append(item)
        return result

    def statistics(self):
        books = self.list_books()
        records = self.list_borrowings()
        return {
            "titles": len(books),
            "total_copies": sum(b["total"] for b in books),
            "available_copies": sum(b["available"] for b in books),
            "borrowed_copies": len(records),
        }

    def answer_without_ai(self, prompt):
        prompt = (prompt or "").strip()
        if not prompt:
            return "Please enter a question."
        lowered = prompt.casefold()
        if any(word in lowered for word in ["hour", "timing", "open", "close"]):
            return "Library hours: Monday–Friday 9 AM–5 PM; Saturday 9 AM–1 PM; Sunday closed."
        if any(word in lowered for word in ["statistic", "how many", "total"]):
            s = self.statistics()
            return f'Catalogue: {s["titles"]} titles, {s["total_copies"]} copies, {s["available_copies"]} available, {s["borrowed_copies"]} currently borrowed.'
        results = self.search_books(prompt)
        if results:
            return "Here are the closest catalogue matches:\n\n" + "\n".join(
                f'- **{b["title"]}** by {b["author"]} ({b["category"]}) — {b["available"]}/{b["total"]} copies available'
                for b in results[:8]
            )
        return "I couldn't find a matching title, author, or category in the local catalogue. Try a shorter keyword such as “Python”, “AI”, or “networking”."
