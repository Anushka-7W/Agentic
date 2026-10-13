import json
import streamlit as st
from services.planning_service import build_trip_plan
from services.llm_service import is_configured
from memory.preference_store import load_preferences, save_preferences
from models.schemas import TripRequest

st.set_page_config(page_title="VoyageAI | Smart Trip Planner", page_icon="🧭", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem;}
.hero {padding: 1.6rem 1.8rem; border-radius: 18px; background: linear-gradient(120deg,#102a43,#176b87); color:white; margin-bottom:1.2rem;}
.hero h1 {font-size:2.4rem; margin:0;}
.hero p {font-size:1.05rem; opacity:.9; margin:.4rem 0 0;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>VoyageAI</h1><p>Constraint-aware travel planning with transparent estimates and optional AI tips.</p></div>', unsafe_allow_html=True)
st.caption("Educational prototype · sample prices only · no live availability or booking")

prefs = load_preferences()
with st.sidebar:
    st.header("Travel preferences")
    travel_style = st.selectbox("Travel style", ["Balanced", "Adventure", "Culture", "Relaxation", "Food-focused"],
                                index=["Balanced","Adventure","Culture","Relaxation","Food-focused"].index(prefs.get("travel_style","Balanced")))
    hotel_style = st.selectbox("Stay preference", ["Any", "Beach", "City centre", "Quiet area"],
                               index=["Any","Beach","City centre","Quiet area"].index(prefs.get("hotel_style","Any")))
    save_pref = st.checkbox("Remember these preferences", value=True)
    use_llm = st.checkbox("Add AI-generated travel tips (optional)", value=False,
                          help="Requires GROQ_API_KEY. The itinerary and budget work without it.")
    st.caption("Preferences are stored locally in memory/preferences.json.")
    st.caption("Groq API configured: " + ("yes" if is_configured() else "no"))

st.subheader("Build your trip")
with st.form("trip_form"):
    c1, c2 = st.columns(2)
    with c1:
        origin = st.text_input("Starting city", value="Bengaluru")
        destination = st.text_input("Destination", value="Goa")
        start_date = st.date_input("Departure date")
        days = st.slider("Trip length (days)", 1, 14, 3)
    with c2:
        travelers = st.number_input("Travelers", min_value=1, max_value=12, value=2)
        budget = st.number_input("Total budget (₹)", min_value=1000, max_value=1000000, value=25000, step=1000)
        interests = st.multiselect("Interests", ["Nature", "Beaches", "History", "Culture", "Food", "Adventure", "Shopping", "Nightlife"],
                                   default=["Beaches", "Food"])
        pace = st.select_slider("Daily pace", options=["Relaxed", "Balanced", "Packed"], value="Balanced")
    submitted = st.form_submit_button("Create itinerary", type="primary", use_container_width=True)

if submitted:
    if not origin.strip() or not destination.strip():
        st.error("Enter both a starting city and a destination.")
    elif origin.strip().casefold() == destination.strip().casefold():
        st.error("Starting city and destination must be different.")
    else:
        request = TripRequest(origin=origin.strip(), destination=destination.strip(),
            departure_date=start_date.isoformat(), duration_days=int(days), travelers=int(travelers),
            budget=float(budget), interests=interests, pace=pace, travel_style=travel_style, hotel_style=hotel_style)
        if save_pref:
            save_preferences({"travel_style": travel_style, "hotel_style": hotel_style})
        with st.spinner("Building itinerary and checking constraints..."):
            result = build_trip_plan(request, use_llm=use_llm)
        st.session_state["last_plan"] = result

if "last_plan" in st.session_state:
    result = st.session_state["last_plan"]
    st.divider()
    if result["status"] == "needs_review":
        st.warning(result["message"])
    elif result["status"] == "error":
        st.error(result["message"])
        for error in result.get("validation_errors", []):
            st.write("- " + error)
    else:
        st.success("Draft created within the estimated budget. Verify details before travel.")
    a, b, c = st.columns(3)
    a.metric("Estimated total", f"₹{result['total_cost']:,.0f}")
    b.metric("Budget remaining", f"₹{result['budget_remaining']:,.0f}")
    c.metric("Budget used", f"{result['budget_percent']:.1f}%")
    if result["status"] != "error":
        st.subheader("Plan overview")
        st.write(result["summary"])
        if result.get("llm_used"):
            st.info(result.get("llm_summary") or "AI travel tips added.")
            for tip in result.get("llm_tips", []):
                st.write("- " + tip)
        st.subheader("Day-by-day itinerary")
        for day in result["itinerary"]:
            with st.expander(f"Day {day['day']}: {day['theme']}", expanded=day["day"] == 1):
                for item in day["activities"]:
                    st.markdown(f"**{item['time']} · {item['title']}**")
                    st.write(item["description"])
                    st.caption(f"{item.get('duration', '1–2 hours')} · Estimated cost: ₹{item['cost']:,.0f} for the group")
        st.subheader("Estimated budget breakdown")
        st.bar_chart({"Amount (₹)": result["cost_breakdown"]})
        st.subheader("Notes and assumptions")
        for note in result["notes"]:
            st.write("- " + note)
        with st.expander("View plan evaluation"):
            st.json(result.get("evaluation", {}))
        st.download_button("Download itinerary (JSON)", data=json.dumps(result, indent=2, ensure_ascii=False),
                           file_name="voyageai_itinerary.json", mime="application/json")
