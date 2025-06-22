# streamlit_app.py
import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Lead Qualifier Demo", page_icon="🤖", layout="centered"
)

# --- App Title ---
st.title("🤖 AI-Powered Lead Qualifier")
st.write(
    "This demo showcases an AI agent that classifies, enriches, and scores new business leads. "
    "Enter a lead's details below to see the agent in action. The FastAPI backend and LangGraph agent "
    "are running separately."
)

# --- Input Form ---
with st.form(key="lead_form"):
    st.subheader("Enter New Lead Details")
    name = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message", height=150)

    submit_button = st.form_submit_button(label="Qualify Lead")

# --- Processing Logic ---
if submit_button:
    if not name or not email or not message:
        st.error("Please fill in all fields.")
    else:
        # Define the API endpoint
        api_url = "http://127.0.0.1:8000/qualify-lead"

        # Prepare the data payload for the API
        lead_data = {"name": name, "email": email, "message": message}

        with st.spinner("The AI agent is thinking... This may take a moment."):
            try:
                # Make the POST request to the FastAPI backend
                response = requests.post(api_url, json=lead_data, timeout=60)

                # Check for a successful response
                if response.status_code == 200:
                    result = response.json()
                    st.success("Lead processed successfully!")

                    # Display the results in a structured way
                    st.subheader("Agent Analysis Results")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Status", result.get("status", "N/A").split(" - ")[-1])
                    col2.metric("Classification", result.get("classification", "N/A"))
                    col3.metric("Score", f"{result.get('score', 0)}/100")

                    st.info(
                        f"**Company/Website Title:** {result.get('company_title', 'N/A')}"
                    )

                    st.subheader("AI-Drafted Reply")
                    st.code(result.get("drafted_reply", "N/A"), language="text")

                else:
                    st.error(f"Error from API: Status code {response.status_code}")
                    st.text(response.text)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Connection Error: Could not connect to the FastAPI backend. "
                    "Please ensure the `uvicorn main:app --reload` server is running in a separate terminal."
                )
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
