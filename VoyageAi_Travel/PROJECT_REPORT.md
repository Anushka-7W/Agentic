# VoyageAI — Agentic AI Software Development Project Report

## 1. Title
**VoyageAI: A Constraint-Aware Travel Planning Assistant**

## 2. Abstract
VoyageAI is an educational travel-planning application that accepts a traveler's route, dates, group size, budget, interests, and preferred pace. It validates the request, selects activities from bundled demonstration data, generates a day-by-day itinerary, calculates an itemized cost estimate, and evaluates whether the estimate fits the stated budget. An optional Groq API integration can generate additional travel tips and a short summary. Numeric estimates remain deterministic and transparent. The system is designed to demonstrate modular agent-style planning, evaluation, memory, optional LLM use, and automated testing.

## 3. Problem Statement
Planning a trip involves balancing time, interests, cost, and the needs of multiple travelers. A conversational answer alone may be difficult to verify or compare. VoyageAI structures the request and exposes its itinerary and cost assumptions so that users can review the result before making travel decisions.

## 4. Objectives
- Collect trip requirements through an interactive interface.
- Validate input fields before starting the planning workflow.
- Select destination activities based on interests and travel pace.
- Estimate transport, accommodation, food, local transport, and activity costs.
- Compare the estimated total with the user's budget.
- Keep planning, research, evaluation, memory, and UI responsibilities modular.
- Offer optional LLM-generated tips without relying on the LLM for arithmetic.
- Test expected behavior and invalid inputs.
- Clearly communicate that bundled prices are illustrative, not live quotes.

## 5. Technologies
- **Python:** application logic and data processing.
- **Streamlit:** interactive web interface.
- **JSON:** preference persistence and itinerary export.
- **Python unittest:** automated tests.
- **Groq-compatible chat completions API (optional):** natural-language travel tips and summary.

The core planner does not require an API key. Optional LLM requests use `GROQ_API_KEY` from the environment; credentials should never be committed to source control.

## 6. System Architecture
The project uses separate modules:
- `app.py` collects input and displays results.
- `services/validation.py` checks the request.
- `agents/researcher.py` retrieves bundled destination and route estimates.
- `agents/planner.py` creates the itinerary and computes cost categories.
- `agents/evaluator.py` checks budget fit and itinerary completeness.
- `services/planning_service.py` coordinates validation and planning.
- `services/llm_service.py` optionally requests tips from an LLM.
- `memory/preference_store.py` stores user-selected preferences locally.
- `data/destination_data.py` contains sample destination data.
- `tests/test_planner.py` checks the core workflow.

## 7. Workflow / Algorithm
1. Read the origin, destination, departure date, duration, traveler count, budget, interests, pace, and preferences.
2. Validate the fields. If any required constraint is invalid, return an error rather than planning.
3. Retrieve the destination's bundled activity data and a route estimate.
4. Filter activities by selected interests. If no exact category matches, use the general activity pool and disclose that fallback.
5. Choose activities according to the requested pace and distribute them across the trip days.
6. Calculate each budget category:
   - Transport = route estimate per traveler × traveler count.
   - Accommodation = illustrative group rate per night × number of nights.
   - Food = estimated daily amount per traveler × travelers × days.
   - Local transport = estimated group amount per day × days.
   - Activities = sum of activity costs for all travelers.
7. Sum the categories and compare the total with the budget.
8. Return either a ready draft or a needs-review result, including assumptions.
9. If requested and configured, call the LLM for additional tips. If the call fails, keep the deterministic itinerary and report that optional tips were unavailable.
10. Display the result and allow the user to export it as JSON.

## 8. Testing
Run the test suite from the project directory:

```bash
python -m unittest discover -s tests -v
```

The included tests cover:
- Plan output structure and cost aggregation.
- Rejection of identical origin and destination.
- Rejection of a non-positive budget.
- Non-negative cost output.
- Rejection of invalid date formats.
- Rejection of an unsupported travel pace.
- Generic fallback behavior for an unknown destination.
- Core planning when optional LLM functionality is disabled.

The delivered version was tested locally: **8 tests passed**.

## 9. Expected Demonstration
1. Launch the Streamlit app and plan a three-day Bengaluru-to-Goa trip.
2. Change interests from beaches and food to history and nature.
3. Change pace from Relaxed to Packed and compare activity density.
4. Lower the budget to demonstrate the needs-review state.
5. Enter the same city for origin and destination to demonstrate validation.
6. Run the test suite and explain how cost totals are aggregated.
7. Optionally configure a Groq key and request LLM tips; then disable the option to show that the core planner still works independently.

## 10. Limitations and Responsible Use
- Bundled transport, accommodation, food, and activity amounts are examples, not current quotes.
- The application does not query live flight, hotel, weather, map, or attraction-opening data.
- It does not make reservations, payments, or other external transactions.
- The LLM is used only for optional text suggestions; its output is not treated as verified facts.
- The current workflow is modular and agent-style but is not a CrewAI or LangGraph multi-agent deployment.
- Preference data is saved in a local JSON file on the machine hosting the app. Users should avoid storing sensitive personal information.
- A production version would need verified data providers, stronger data validation, observability, rate limiting, secure deployment, and privacy review.

## 11. Future Enhancements
- Connect trusted live transport and accommodation APIs.
- Add a calendar-aware itinerary optimizer and travel-time constraints.
- Add a map view backed by a verified map provider.
- Support alternate plans and explicit cost-saving strategies.
- Add configurable lodging tiers and accessibility preferences.
- Add persistent storage with a user-controlled deletion flow.
- Add integration tests for external APIs and more property-based tests for budget arithmetic.

## 12. Conclusion
VoyageAI demonstrates a structured travel-planning workflow that combines input validation, modular research and planning components, transparent cost estimation, budget evaluation, optional LLM assistance, local preference memory, and automated tests. Its most important design choice is separating generated language from numeric cost calculations and clearly marking sample estimates as unverified. This makes the prototype suitable for a classroom demonstration while leaving clear next steps for a real-world implementation.
