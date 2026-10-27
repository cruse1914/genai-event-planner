import streamlit as st
import json
import os
from google import genai
from google.genai import types

# Page Config
st.set_page_config(page_title="AI Event Planner", page_icon="🎉", layout="wide")

st.title("🎉 GenAI Celebration & Event Planning Assistant")
st.write("Plan Weddings, Birthdays, and Community Events with AI-powered budgets, timelines, and checklists.")

# Cached Client for Efficiency
@st.cache_resource
def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)

# Sidebar Configuration & Security Handling
st.sidebar.header("Configuration")
env_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Enter Gemini API Key", value=env_key, type="password")

st.sidebar.markdown("---")
st.sidebar.info("Challenge 5 Hack2skill Submission | Built with Gemini API")

# Inputs
col1, col2 = st.columns(2)

with col1:
    event_type = st.selectbox("Event Type", ["Wedding", "Birthday Party", "Community Event", "Corporate Meetup"])
    guest_count = st.number_input("Number of Guests", min_value=10, max_value=5000, value=100)
    
with col2:
    budget = st.number_input("Total Budget (in local currency)", min_value=500, value=50000, step=500)
    theme = st.text_input("Event Theme / Style", value="Modern & Elegant")

special_requests = st.text_area("Special Notes / Preferences", value="Focus on outdoor seating and live music.")

def validate_inputs(guests, bg):
    return guests > 0 and bg > 0

if st.button("🚀 Generate Complete Event Plan", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar or secrets.")
    elif not validate_inputs(guest_count, budget):
        st.error("Please enter valid positive numbers for guests and budget.")
    else:
        try:
            with st.spinner("GenAI is crafting your custom event plan..."):
                client = get_gemini_client(api_key)
                
                prompt = f"""
                You are an expert event planner. Create a structured event plan for a {event_type}.
                Guest Count: {guest_count}
                Total Budget: {budget}
                Theme: {theme}
                Special Notes: {special_requests}

                Provide a JSON response with:
                1. "budget_breakdown": Dictionary mapping categories (Venue, Catering, Decor, Entertainment, Logistics) to estimated costs (numeric).
                2. "timeline": List of objects with "time" and "activity".
                3. "checklist": List of milestone tasks categorized by weeks leading up to the event.
                4. "creative_ideas": List of 5 unique theme, food, or activity ideas.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                
                data = json.loads(response.text)
                st.success("Event Plan Generated Successfully!")
                
                t1, t2, t3, t4 = st.tabs(["💰 Budget", "⏱️ Day-of Timeline", "📋 Checklist", "💡 Creative Ideas"])
                
                with t1:
                    st.subheader("Estimated Budget Breakdown")
                    st.json(data.get("budget_breakdown", {}))
                    
                with t2:
                    st.subheader("Day-of Schedule")
                    for item in data.get("timeline", []):
                        st.markdown(f"**{item.get('time', '')}**: {item.get('activity', '')}")
                        
                with t3:
                    st.subheader("Vendor & Task Checklist")
                    for task in data.get("checklist", []):
                        st.checkbox(str(task), value=False)
                        
                with t4:
                    st.subheader("Personalized Ideas")
                    for idea in data.get("creative_ideas", []):
                        st.markdown(f"* {idea}")

        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
