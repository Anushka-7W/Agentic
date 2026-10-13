import os
import streamlit as st
from dotenv import load_dotenv
from library_service import LibraryService
from ai_agent import LibraryAIAgent

load_dotenv()
st.set_page_config(page_title="Libra | Smart Library", page_icon="📚", layout="wide")

@st.cache_resource
def get_service():
    return LibraryService("library.db")

service = get_service()

def get_agent():
    try:
        return LibraryAIAgent(service)
    except Exception:
        return None

st.markdown("""
<style>
.block-container {padding-top: 1.8rem; padding-bottom: 2rem;}
.hero {padding: 1.3rem 1.5rem; border-radius: 16px; background: linear-gradient(120deg,#14213d,#315b86); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin:0;}
.small-muted {color:#6b7280; font-size:.92rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>📚 Libra Smart Library Assistant</h1><p>Find books, manage circulation, and ask questions in plain language.</p></div>', unsafe_allow_html=True)

stats = service.statistics()
c1,c2,c3,c4 = st.columns(4)
c1.metric("Book titles", stats["titles"])
c2.metric("Total copies", stats["total_copies"])
c3.metric("Available copies", stats["available_copies"])
c4.metric("Checked out", stats["borrowed_copies"])

page = st.sidebar.radio("Navigation", ["Ask Libra", "Browse & Search", "Borrow / Return", "My Borrowings", "Library Guide"])
st.sidebar.caption("Demo app • SQLite storage")
st.sidebar.info("Borrowing limit: 3 books per demo user\n\nLoan period: 14 days")

if page == "Ask Libra":
    st.subheader("Ask the library assistant")
    st.write("Ask about titles, authors, categories, availability, borrowing rules, or library statistics.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role":"assistant","content":"Hello! I'm Libra. Ask me to find a book, check availability, or explain library rules."}]
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    prompt = st.chat_input("For example: Find books about algorithms")
    if prompt:
        st.session_state.chat_history.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            agent = get_agent()
            if agent:
                answer = agent.respond(prompt)
            else:
                answer = service.answer_without_ai(prompt)
                answer += "\n\n*AI service is not configured; answered using the local library search fallback.*"
            st.markdown(answer)
        st.session_state.chat_history.append({"role":"assistant","content":answer})

elif page == "Browse & Search":
    st.subheader("Browse the catalogue")
    query = st.text_input("Search by title, author, or category", placeholder="e.g. Python, networking, algorithms")
    category_options = ["All"] + service.categories()
    category = st.selectbox("Category filter", category_options)
    books = service.search_books(query=query, category=None if category == "All" else category)
    if books:
        st.dataframe([{
            "ID": b["id"], "Title": b["title"], "Author": b["author"],
            "Category": b["category"], "Available": f'{b["available"]}/{b["total"]}',
            "Status": "Available" if b["available"] else "All copies borrowed"
        } for b in books], use_container_width=True, hide_index=True)
    else:
        st.warning("No matching books. Try a different title, author, or category.")

elif page == "Borrow / Return":
    st.subheader("Circulation desk")
    tab_borrow, tab_return = st.tabs(["Borrow a book", "Return a book"])
    with tab_borrow:
        available = [b for b in service.list_books() if b["available"] > 0]
        if available:
            options = {f'{b["title"]} — {b["author"]} (ID {b["id"]})': b["id"] for b in available}
            with st.form("borrow_form"):
                borrower = st.text_input("Your name or demo user ID", value="student")
                selected = st.selectbox("Choose a book", list(options))
                submitted = st.form_submit_button("Borrow book")
            if submitted:
                result = service.borrow_book(options[selected], borrower.strip() or "student")
                (st.success if result["success"] else st.error)(result["message"])
                if result["success"]:
                    st.info(f'Due date: {result["due_date"]}')
        else:
            st.info("No books are currently available.")
    with tab_return:
        borrowed = service.list_borrowings()
        if borrowed:
            options = {f'{b["title"]} — {b["borrower"]} (due {b["due_date"]})': b["borrowing_id"] for b in borrowed}
            with st.form("return_form"):
                selected_return = st.selectbox("Choose a borrowing record", list(options))
                submitted_return = st.form_submit_button("Return book")
            if submitted_return:
                result = service.return_book(options[selected_return])
                (st.success if result["success"] else st.error)(result["message"])
        else:
            st.info("There are no active borrowing records.")

elif page == "My Borrowings":
    st.subheader("Active borrowing records")
    borrower = st.text_input("Filter by borrower (optional)")
    records = service.list_borrowings(borrower=borrower.strip() or None)
    if records:
        st.dataframe([{
            "Borrower": b["borrower"], "Title": b["title"], "Author": b["author"],
            "Borrowed on": b["borrow_date"], "Due date": b["due_date"],
            "Status": "Overdue" if b["overdue"] else "On loan"
        } for b in records], use_container_width=True, hide_index=True)
    else:
        st.info("No active borrowings match this filter.")

elif page == "Library Guide":
    st.subheader("Library information")
    st.markdown("""
    **Opening hours**
    - Monday–Friday: 9:00 AM – 5:00 PM
    - Saturday: 9:00 AM – 1:00 PM
    - Sunday: Closed

    **Borrowing rules**
    - Each demo borrower can hold up to 3 books at a time.
    - Standard loan period: 14 days.
    - Only available copies can be borrowed.
    - Returning a book closes the active borrowing record.
    """)
    st.caption("This educational demo uses sample catalogue data. It is not connected to a real college library.")
