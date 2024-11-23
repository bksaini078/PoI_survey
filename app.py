import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from typing import Optional

# Define the response model
class POIResponse(BaseModel):
    title: str = Field(..., description="A catchy and informative title for the POI")
    description: str = Field(..., description="An engaging and detailed description of the POI")

# Initialize Azure OpenAI client
@st.cache_resource
def get_openai_client():
    return AzureOpenAI(
        api_version="2024-08-01-preview",
        api_key="f3b476351d86408589ac63c6a8e3cb21",  # Add your API key here
        azure_endpoint="https://fhgenie-api-iao-idt13200.openai.azure.com/"
    )

# Generate AI content for POI
def generate_ai_content(poi_data):
    client = get_openai_client()
    
    system_prompt = """You are an expert travel writer and content creator. Your task is to create engaging, 
    informative titles and descriptions for Points of Interest (POIs) that capture attention and provide value to potential visitors.
    Focus on unique aspects, cultural significance, and visitor experience."""
    
    prompt = f"""Create a title and description for this Point of Interest:
    Original Title: {poi_data['title']}
    Original Description: {poi_data['description']}
    
    Please provide a fresh perspective while maintaining accuracy and highlighting key attractions and experiences."""
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format=POIResponse,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        st.error(f"Error generating AI content: {str(e)}")
        return POIResponse(
            title="[Error generating title]",
            description="[Error generating description]"
        )

# Set page config
st.set_page_config(
    page_title="POI Survey Application",
    page_icon="🏰",
    layout="wide"
)

# Custom CSS for font sizes
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: 500;
    }
    .question-font {
        font-size:18px !important;
        margin-bottom: 10px;
    }
    .stRadio > label {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
            st.rerun()

# POI comparison page
def show_poi_comparison(poi_data, poi_index):
    poi = poi_data["pois"][poi_index]
    
    # Generate AI content
    ai_content = generate_ai_content(poi)
    
    st.title(f"POI Comparison - {poi_index + 1}/{len(poi_data['pois'])}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("POI A")
        st.image(poi["imagesrc"], caption="POI Image", width=1000)  
        st.markdown(f'<p class="big-font"><b>Title:</b> <br> <b> {poi["title"]} </b> </p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font"><b>Description: <br> </b> {poi["description"]}</p>', unsafe_allow_html=True)

        st.markdown('<hr style="height:3px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)

        st.markdown('<p class="big-font"><b>Value and Services Assessment</b></p>', unsafe_allow_html=True)
        
        st.markdown('<p class="question-font">Does the description effectively communicate the significance and offerings of the place?</p>', unsafe_allow_html=True)
        manual_significance = st.radio(
            "",  
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"manual_significance_{poi_index}",
            horizontal=True
        )
        
        st.write("")
        st.markdown('<p class="big-font"><b>Trustworthiness</b></p>', unsafe_allow_html=True)
        st.markdown('<p class="question-font">Do you trust that this description provides accurate and reliable information about the place?</p>', unsafe_allow_html=True)
        manual_trust = st.radio(
            "",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"manual_trust_{poi_index}",
            horizontal=True
        )
        
        st.write("")
        st.markdown('<p class="big-font"><b>Clarity and Completeness</b></p>', unsafe_allow_html=True)
        st.markdown('<p class="question-font">Is the description clear and easy to understand without omitting important details?</p>', unsafe_allow_html=True)
        manual_clarity = st.radio(
            "",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"manual_clarity_{poi_index}",
            horizontal=True
        )
    
    with col2:
        st.subheader("POI B")
        st.image(poi["imagesrc"], caption="POI Image", width=1000)  
        st.markdown(f'<p class="big-font"><b>Title:</b> <br> <b>{ai_content.title}</b></p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font"><b>Description:</b> <br> {ai_content.description}</p>', unsafe_allow_html=True)
        
        st.markdown('<hr style="height:3px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)
        st.markdown('<p class="big-font"><b>Value and Services Assessment</b></p>', unsafe_allow_html=True)
        st.markdown('<p class="question-font">Does the description effectively communicate the significance and offerings of the place?</p>', unsafe_allow_html=True)
        ai_significance = st.radio(
            "",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"ai_significance_{poi_index}",
            horizontal=True
        )
        
        st.write("")
        st.markdown('<p class="big-font"><b>Trustworthiness</b></p>', unsafe_allow_html=True)
        st.markdown('<p class="question-font">Do you trust that this description provides accurate and reliable information about the place?</p>', unsafe_allow_html=True)
        ai_trust = st.radio(
            "",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"ai_trust_{poi_index}",
            horizontal=True
        )
        
        st.write("")
        st.markdown('<p class="big-font"><b>Clarity and Completeness</b></p>', unsafe_allow_html=True)
        st.markdown('<p class="question-font">Is the description clear and easy to understand without omitting important details?</p>', unsafe_allow_html=True)
        ai_clarity = st.radio(
            "",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"ai_clarity_{poi_index}",
            horizontal=True
        )
    
    st.write("")
    st.markdown('<hr style="height:3px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)
    
    st.write("")
    st.markdown('<p class="big-font"><b>Comparison Questions</b></p>', unsafe_allow_html=True)
    
    st.write("")
    st.markdown('<p class="question-font">Which description did you find more engaging and appealing (captured your attention more)?</p>', unsafe_allow_html=True)
    engaging_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"engaging_{poi_index}",
        horizontal=True
    )
    
    st.write("")
    st.markdown('<p class="question-font">Which description did you find more relevant to your interests?</p>', unsafe_allow_html=True)
    relevant_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"relevant_{poi_index}",
        horizontal=True
    )
    
    st.write("")
    st.markdown('<p class="question-font">Which description makes you more eager to visit the POI?</p>', unsafe_allow_html=True)
    eager_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"eager_{poi_index}",
        horizontal=True
    )
    
    st.write("")
    st.markdown('<p class="question-font">Which Title do you prefer?</p>', unsafe_allow_html=True)
    title_preference = st.radio(
        "",
        options=["Title A", "Title B"],
        key=f"title_{poi_index}",
        horizontal=True
    )
    
    st.write("")
    st.markdown('<p class="question-font">Which Description do you prefer?</p>', unsafe_allow_html=True)
    description_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"description_{poi_index}",
        horizontal=True
    )
    
    st.write("")
    st.markdown('<hr style="height:3px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)
    
    st.write("---")  # Separation line after comparison questions
    
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
                "engaging_preference": engaging_preference,
                "relevant_preference": relevant_preference,
                "eager_preference": eager_preference,
                "title_preference": title_preference,
                "description_preference": description_preference,
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
