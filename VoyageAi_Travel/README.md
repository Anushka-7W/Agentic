# VoyageAI — Constraint-Aware Travel Planner

VoyageAI is an educational travel-planning project demonstrating a modular agentic workflow: collect requirements, validate constraints, research bundled destination data, build a day-wise plan, calculate costs, evaluate budget fit, and optionally request LLM-generated travel tips.

## Features
- Interactive Streamlit UI
- Interest- and pace-based day-by-day itinerary
- Cost breakdown with transparent arithmetic
- Budget evaluation and warnings
- Local preference memory with opt-in saving
- JSON export
- Optional Groq LLM travel tips, with deterministic fallback
- Unit tests for common and invalid inputs

## Requirements
Python 3.10+. The core planner runs on bundled sample data. An internet connection is needed to install packages. Groq is optional and uses Python's standard library HTTP client.

## Install and run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional LLM setup
Set `GROQ_API_KEY` as an environment variable before launching the app. Optionally set `GROQ_MODEL`. Never commit API keys. The optional LLM provides travel tips and a short summary; it does not set prices or claim to check availability. If the API is unavailable, the deterministic planner still works.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Architecture
- `app.py`: user interface and interaction
- `agents/researcher.py`: bundled destination and route estimate lookup
- `agents/planner.py`: itinerary construction and cost aggregation
- `agents/evaluator.py`: budget and itinerary checks
- `services/planning_service.py`: validates and coordinates the workflow
- `services/llm_service.py`: optional LLM suggestions
- `services/validation.py`: input validation
- `data/destination_data.py`: illustrative local data
- `memory/preference_store.py`: local preference persistence
- `models/schemas.py`: request data model
- `tests/`: automated tests

## Agentic workflow
1. Receive structured trip requirements.
2. Validate fields and reject invalid requests.
3. Look up destination activities and route estimates from bundled data.
4. Match activities to the interests and pace.
5. Calculate transport, accommodation, food, local transport, and activity estimates.
6. Evaluate the plan against the budget and report issues.
7. Optionally obtain extra language-model tips, while keeping numeric budget calculations deterministic.
8. Present the draft itinerary and allow JSON export.

## Limitations and honest scope
- Bundled prices are illustrative estimates, not live quotes.
- No live flight, hotel, weather, map, or opening-hours API is connected.
- No bookings or payments are made.
- The LLM integration is optional and only supplies tips/summary; the core planner is deterministic.
- Unknown destinations use generic activity templates and fallback estimates.
- Preferences are stored in a local JSON file on the machine running the app.
- This is a modular agent-style workflow, not a multi-agent framework implementation such as CrewAI or LangGraph.

## Suggested academic demonstration
1. Create a 3-day trip with beach and food interests.
2. Change the daily pace and compare activity density.
3. Reduce the budget to trigger the review state.
4. Enter the same origin and destination to demonstrate validation.
5. Run the tests and explain the cost calculation and evaluator.
6. If a Groq API key is configured, enable optional AI tips; otherwise demonstrate fallback behavior.

## Viva preparation topics
- Agentic workflow versus a simple chatbot
- Separation of concerns and modular architecture
- Input validation and structured request data
- Deterministic cost calculations versus probabilistic LLM output
- Budget constraints and evaluation
- API failure fallback and safe handling of secrets
- Unit tests, limitations, and honest claims
