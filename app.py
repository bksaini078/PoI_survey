import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid

# Set page config
st.set_page_config(
    page_title="POI Survey Application",
    page_icon="🏰",
    layout="wide"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'user_id': str(uuid.uuid4())
    }
if 'survey_responses' not in st.session_state:
    st.session_state.survey_responses = []

# Load POI data
def load_poi_data():
    try:
        with open('data/pois.json', 'r') as f:
            data = json.load(f)
        
        # Flatten the POIs from all categories
        all_pois = []
        for category in data.get('categories', []):
            all_pois.extend(category['pois'])
        
        # Create a new data structure with all POIs
        return {
            "name": "All POIs",
            "color": "purple",
            "pois": all_pois
        }
    except FileNotFoundError:
        st.error("POI data file not found. Please ensure 'data/pois.json' exists.")
        return None

# Save survey response
def save_response():
    if not st.session_state.survey_responses:
        return
    
    df = pd.DataFrame(st.session_state.survey_responses)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("survey_results")
    output_dir.mkdir(exist_ok=True)
    df.to_csv(output_dir / f"survey_responses_{timestamp}.csv", index=False)

# User details form
def show_user_details_form():
    st.title("Welcome to the POI Survey")
    st.write("Please provide your details before starting the survey.")
    
    with st.form("user_details"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=18, max_value=100)
        marital_status = st.selectbox(
            "Marital Status",
            ["Single", "Married", "Divorced", "Widowed"]
        )
        children_details = st.text_area("Children Details")
        education = st.selectbox(
            "Education Level",
            ["High School", "Bachelor's", "Master's", "PhD", "Other"]
        )
        hobbies = st.multiselect(
            "Hobbies",
            ["Traveling", "Reading", "Sports", "Music", "Cooking", "Gaming", "Other"]
        )
        
        submit = st.form_submit_button("Start Survey")
        
        if submit:
            if not name or not age:
                st.error("Please fill in all required fields.")
                return
            
            st.session_state.user_data = {
                "user_id": st.session_state.user_data['user_id'],  # Preserve the user_id
                "name": name,
                "age": age,
                "marital_status": marital_status,
                "children_details": children_details,
                "education": education,
                "hobbies": hobbies
            }
            st.session_state.page += 1
            st.experimental_rerun()

# POI comparison page
def show_poi_comparison(poi_data, poi_index):
    poi = poi_data["pois"][poi_index]
    st.title(f"POI Comparison - {poi_index + 1}/{len(poi_data['pois'])}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Manual Version")
        st.image(poi["imagesrc"], caption="POI Image", use_column_width=True)
        st.write(f"**Title:** {poi['title']}")
        st.write(f"**Description:** {poi['description']}")
        
        st.write("---")
        st.write("**Value and Services Assessment**")
        
        manual_significance = st.radio(
            "Does the description effectively communicate the significance and offerings of the place?",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"manual_significance_{poi_index}",
            horizontal=True
        )
        
        st.write("")  # Add some spacing
        manual_trust = st.radio(
            "Do you trust that this description provides accurate and reliable information about the place?",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"manual_trust_{poi_index}",
            horizontal=True
        )
        
        st.write("")  # Add some spacing
        manual_clarity = st.radio(
            "Is the description clear and easy to understand without omitting important details?",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"manual_clarity_{poi_index}",
            horizontal=True
        )
    
    with col2:
        st.subheader("AI Generated Version")
        st.image(poi["imagesrc"], caption="POI Image", use_column_width=True)
        st.write("**Title:** [AI Generated Title]")
        st.write("**Description:** [AI Generated Description]")
        
        st.write("---")
        st.write("**Value and Services Assessment**")
        
        ai_significance = st.radio(
            "Does the description effectively communicate the significance and offerings of the place?",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"ai_significance_{poi_index}",
            horizontal=True
        )
        
        st.write("")  # Add some spacing
        ai_trust = st.radio(
            "Do you trust that this description provides accurate and reliable information about the place?",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"ai_trust_{poi_index}",
            horizontal=True
        )
        
        st.write("")  # Add some spacing
        ai_clarity = st.radio(
            "Is the description clear and easy to understand without omitting important details?",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"ai_clarity_{poi_index}",
            horizontal=True
        )
    
    st.write("")  # Add some spacing
    visit_likelihood = st.radio(
        "How likely are you to visit this POI?",
        options=["Very Unlikely", "Unlikely", "Neutral", "Likely", "Very Likely"],
        key=f"visit_{poi_index}",
        horizontal=True
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("Next" if poi_index < len(poi_data["pois"]) - 1 else "Finish"):
            # Save response
            response = {
                **st.session_state.user_data,
                "poi_id": poi["id"],
                "poi_title": poi["title"],
                "manual_significance": manual_significance,
                "manual_trust": manual_trust,
                "manual_clarity": manual_clarity,
                "ai_significance": ai_significance,
                "ai_trust": ai_trust,
                "ai_clarity": ai_clarity,
                "visit_likelihood": visit_likelihood,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.survey_responses.append(response)
            
            if poi_index < len(poi_data["pois"]) - 1:
                st.session_state.page += 1
            else:
                save_response()
                st.session_state.page = -1
            st.experimental_rerun()

# Thank you page
def show_thank_you():
    st.title("Thank You!")
    st.write("Your responses have been recorded. Thank you for participating in the survey!")
    if st.button("Start New Survey"):
        st.session_state.page = 0
        st.session_state.user_data = {
            'user_id': str(uuid.uuid4())
        }
        st.session_state.survey_responses = []
        st.experimental_rerun()

# Main app logic
def main():
    poi_data = load_poi_data()
    if not poi_data:
        return
    
    if st.session_state.page == 0:
        show_user_details_form()
    elif st.session_state.page == -1:
        show_thank_you()
    else:
        show_poi_comparison(poi_data, st.session_state.page - 1)

if __name__ == "__main__":
    main()
