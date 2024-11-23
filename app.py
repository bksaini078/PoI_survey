import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from typing import Optional
import time
import os

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

def generate_ai_content(poi_data, user_data):
    client = get_openai_client()
    
    # Calculate maximum length for the description
    max_description_length = len(poi_data['description'])
    max_title_length = len(poi_data['title'])
    
    system_prompt = f"""You are an expert travel writer and content creator. Your task is to create engaging, 
    informative titles and descriptions for Points of Interest (POIs) that capture attention and provide value to potential visitors.
    Focus on unique aspects, cultural significance, and visitor experience. Consider the visitor's family situation and adapt the content
    to highlight relevant aspects (e.g., family-friendly features, romantic spots for couples, etc.).
    
    IMPORTANT LENGTH CONSTRAINTS:
    - The description MUST NOT exceed {max_description_length} characters
    - The title MUST NOT exceed {max_title_length} characters
    - Be concise while maintaining informativeness"""
    
    # Process children details for better prompt formatting
    children_info = user_data.get('children_details', 'None')
    if children_info and children_info.strip().lower() not in ['none', 'no', '']:
        family_context = f"Has children: {children_info}"
    else:
        family_context = "No children"
    
    prompt = f"""Create a title and description for this Point of Interest, personalized for the following user:
    User Age: {user_data.get('age', 'Not specified')}
    User Gender: {user_data.get('gender', 'Not specified')}
    Marital Status: {user_data.get('marital_status', 'Not specified')}
    Family Context: {family_context}
    User Interests: {user_data.get('interests', 'Not specified')}
    User Travel Experience: {user_data.get('travel_experience', 'Not specified')}
    Education Level: {user_data.get('education', 'Not specified')}
    Profession: {user_data.get('profession', 'Not specified')}
    Industry: {user_data.get('industry', 'Not specified')}
    Hobbies: {user_data.get('hobbies', 'Not specified')}
    Preferred Travel Style: {user_data.get('preferred_travel_style', 'Not specified')}

    Point of Interest:
    Original Title: {poi_data['title']}
    Original Description: {poi_data['description']}
    
    STRICT LENGTH REQUIREMENTS:
    - Your description MUST be {max_description_length} characters or less
    - Your title MUST be {max_title_length} characters or less
    
    Please provide a fresh perspective while maintaining accuracy and highlighting key attractions and experiences.
    Tailor the content to match the user's interests, experience level, and family situation. Consider:
    - If married/with children: Include family-friendly aspects, activities suitable for children, and practical information for families
    - If single: Focus more on social aspects, individual experiences, and meeting points
    - If married without children: Highlight romantic aspects and couple-oriented experiences
    
    Ensure the description resonates with their life situation while maintaining broad appeal."""
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format=POIResponse,
        )
        
        # Verify and truncate content if necessary
        generated_content = completion.choices[0].message.parsed
        
        # Ensure title length constraint
        if len(generated_content.title) > max_title_length:
            generated_content.title = generated_content.title[:max_title_length].rsplit(' ', 1)[0]
        
        # Ensure description length constraint
        if len(generated_content.description) > max_description_length:
            generated_content.description = generated_content.description[:max_description_length].rsplit(' ', 1)[0]
        
        return generated_content
        
    except Exception as e:
        st.error(f"Error generating AI content: {str(e)}")
        return POIResponse(
            title="[Error generating title]",
            description="[Error generating description]"
        )

def generate_all_poi_content(pois, user_data):
    """Generate AI content for all POIs and save to temporary file"""
    temp_file = Path(f"temp_poi_content_{user_data['user_id']}.json")
    
    # Show loading page with progress
    st.title("Generating Personalized Content")
    st.write("Please wait while we create personalized descriptions for each location...")
    
    # Show progress bar
    progress_text = "Generating AI content for all POIs..."
    progress_bar = st.progress(0)
    
    ai_content = {}
    for i, poi in enumerate(pois):
        with st.spinner(f'Generating content for POI {i+1}/{len(pois)}...'):
            content = generate_ai_content(poi, user_data)
            ai_content[poi['id']] = {
                'title': content.title,
                'description': content.description
            }
            # Update progress
            progress_bar.progress((i + 1) / len(pois))
            time.sleep(0.1)  # Small delay for smooth progress bar
    
    # Save to temporary file
    with open(temp_file, 'w') as f:
        json.dump(ai_content, f)
    
    progress_bar.empty()
    return ai_content

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
    
    with st.form("user_details_form"):
        st.write("Please provide some information about yourself:")
        
        # Personal Information
        st.markdown('<p class="big-font"><b>Personal Information</b></p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=18, max_value=100)
            gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
            marital_status = st.selectbox(
                "Marital Status",
                ["Single", "Married", "In a Relationship", "Divorced", "Widowed", "Prefer not to say"]
            )
            children_details = st.text_input(
                "Children Details",
                help="Please specify ages of children, if any. Example: '2 children - ages 5 and 8' or 'No children'"
            )
        
        # Professional Information
        st.markdown('<p class="big-font"><b>Professional Information</b></p>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        
        with col3:
            education = st.selectbox(
                "Education Level",
                ["High School", "Bachelor's", "Master's", "PhD","Professor", "Other"]
            )
            profession = st.text_input(
                "Current Profession",
                help="Your current job title or role"
            )
        
        with col4:
            industry = st.selectbox(
                "Industry",
                ["Technology", "Healthcare", "Education", "Finance", "Manufacturing",
                 "Retail", "Government", "Non-profit", "Other"]
            )
        # Interests and Hobbies
        st.markdown('<p class="big-font"><b>Interests and Hobbies</b></p>', unsafe_allow_html=True)
        col5, col6 = st.columns(2)
        
        with col5:
            hobbies = st.multiselect(
                "Hobbies",
                ["Reading", "Writing", "Sports", "Music", "Cooking", "Gaming",
                 "Photography", "Art", "Dancing", "Gardening", "Traveling",
                 "Movies/TV", "Technology", "Fashion", "Fitness", "Other"]
            )
            
            interests = st.multiselect(
                "Travel Interests",
                ["History & Culture", "Nature & Outdoors", "Food & Cuisine", 
                 "Architecture", "Art & Museums", "Shopping", "Local Experiences",
                 "Family Activities", "Adventure Sports", "Relaxation", 
                 "Photography", "Religious Sites", "Nightlife", "Festivals"]
            )
        
        with col6:
            travel_experience = st.radio(
                "How would you rate your travel experience?",
                options=["Beginner", "Intermediate", "Experienced", "Expert"],
                help="Select the option that best describes your travel experience level"
            )
            
            preferred_travel_style = st.multiselect(
                "Preferred Travel Style",
                ["Luxury", "Budget", "Adventure", "Relaxation", "Cultural",
                 "Solo Travel", "Group Tours", "Family-oriented", "Business"]
            )
        
        submitted = st.form_submit_button("Start Survey")
        
        if submitted and name and age and gender and interests and marital_status and profession:
            st.session_state.user_data.update({
                'name': name,
                'age': age,
                'gender': gender,
                'marital_status': marital_status,
                'children_details': children_details,
                'education': education,
                'profession': profession,
                'industry': industry,
                'hobbies': hobbies,
                'interests': interests,
                'travel_experience': travel_experience,
                'preferred_travel_style': preferred_travel_style
            })
            
            # Load POI data
            poi_data = load_poi_data()
            if not poi_data:
                return
            
            # Show a message before starting content generation
            st.info("Thank you for providing your details! We'll now generate personalized content for your survey...")
            
            # Generate personalized content
            st.session_state.ai_content = generate_all_poi_content(poi_data['pois'], st.session_state.user_data)
            
            # Move to first POI
            st.session_state.page = 1
            st.rerun()
        elif submitted:
            st.error("Please fill in all required fields (name, age, gender, interests, marital status, and profession are required).")

# POI comparison page
def show_poi_comparison(poi_data, poi_index):
    poi = poi_data["pois"][poi_index]
    ai_content = st.session_state.ai_content.get(poi['id'], {
        'title': '[Error loading title]',
        'description': '[Error loading description]'
    })
    
    st.title(f"POI Comparison - {poi_index + 1}/{len(poi_data['pois'])}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("POI A")
        st.image(poi["imagesrc"], caption="POI Image", width=1000)
        
        # Title container
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.markdown('<div class="title-container">', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font"><b>Title:</b> <br> <b>{poi["title"]}</b></p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Description container
        st.markdown('<div class="description-container">', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font"><b>Description:</b> <br> {poi["description"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Assessment section
        st.markdown('<div class="assessment-container">', unsafe_allow_html=True)
        st.markdown('<p class="big-font"><b>Value and Services Assessment</b></p>', unsafe_allow_html=True)
        
        st.markdown('<p class="question-font">Does the description effectively communicate the significance and offerings of the place?</p>', unsafe_allow_html=True)
        manual_significance = st.radio(
            "",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"manual_significance_{poi_index}",
            horizontal=True
        )
        
        st.markdown('<p class="question-font">How trustworthy does this description appear to be?</p>', unsafe_allow_html=True)
        manual_trust = st.radio(
            "",
            options=["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
            key=f"manual_trust_{poi_index}",
            horizontal=True
        )
        
        st.markdown('<p class="question-font">How clear and complete is the information provided?</p>', unsafe_allow_html=True)
        manual_clarity = st.radio(
            "",
            options=["Very Unclear", "Unclear", "Neutral", "Clear", "Very Clear"],
            key=f"manual_clarity_{poi_index}",
            horizontal=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("POI B")
        st.image(poi["imagesrc"], caption="POI Image", width=1000)
        
        # Title container
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.markdown('<div class="title-container">', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font"><b>Title:</b> <br> <b>{ai_content["title"]}</b></p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Description container
        st.markdown('<div class="description-container">', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font"><b>Description:</b> <br> {ai_content["description"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Assessment section
        st.markdown('<div class="assessment-container">', unsafe_allow_html=True)
        st.markdown('<p class="big-font"><b>Value and Services Assessment</b></p>', unsafe_allow_html=True)
        
        st.markdown('<p class="question-font">Does the description effectively communicate the significance and offerings of the place?</p>', unsafe_allow_html=True)
        ai_significance = st.radio(
            "",
            options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            key=f"ai_significance_{poi_index}",
            horizontal=True
        )
        
        st.markdown('<p class="question-font">How trustworthy does this description appear to be?</p>', unsafe_allow_html=True)
        ai_trust = st.radio(
            "",
            options=["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
            key=f"ai_trust_{poi_index}",
            horizontal=True
        )
        
        st.markdown('<p class="question-font">How clear and complete is the information provided?</p>', unsafe_allow_html=True)
        ai_clarity = st.radio(
            "",
            options=["Very Unclear", "Unclear", "Neutral", "Clear", "Very Clear"],
            key=f"ai_clarity_{poi_index}",
            horizontal=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Comparison Questions Section
    st.markdown('<hr class="custom-divider" />', unsafe_allow_html=True)
    st.markdown('<p class="big-font"><b>Comparison Questions</b></p>', unsafe_allow_html=True)
    
    st.markdown('<p class="question-font">Which description did you find more engaging and appealing (captured your attention more)?</p>', unsafe_allow_html=True)
    engaging_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"engaging_{poi_index}",
        horizontal=True
    )
    
    st.markdown('<p class="question-font">Which description did you find more relevant to your interests?</p>', unsafe_allow_html=True)
    relevant_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"relevant_{poi_index}",
        horizontal=True
    )
    
    st.markdown('<p class="question-font">Which description makes you more eager to visit the POI?</p>', unsafe_allow_html=True)
    eager_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"eager_{poi_index}",
        horizontal=True
    )
    
    st.markdown('<p class="question-font">Which Title do you prefer?</p>', unsafe_allow_html=True)
    title_preference = st.radio(
        "",
        options=["Title A", "Title B"],
        key=f"title_{poi_index}",
        horizontal=True
    )
    
    st.markdown('<p class="question-font">Which Description do you prefer?</p>', unsafe_allow_html=True)
    description_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"description_{poi_index}",
        horizontal=True
    )
    
    st.write("")
    st.markdown('<hr class="custom-divider" />', unsafe_allow_html=True)
    
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

# Set page config
st.set_page_config(
    page_title="POI Survey Application",
    page_icon="🏰",
    layout="wide"
)

# Custom CSS for font sizes and containers
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
    .content-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        min-height: 200px;  /* Minimum height for content containers */
    }
    .title-container {
        min-height: 80px;  /* Fixed height for title section */
        display: flex;
        flex-direction: column;
    }
    .description-container {
        min-height: 150px;  /* Fixed height for description section */
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
    }
    .assessment-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .custom-divider {
        height: 3px;
        background-color: #333;
        border: none;
        margin: 20px 0;
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

# Main app logic
def main():
    if st.session_state.page == 0:
        show_user_details_form()
    elif st.session_state.page == -1:
        show_thank_you()
    else:
        poi_data = load_poi_data()
        if not poi_data:
            return
        show_poi_comparison(poi_data, st.session_state.page - 1)

if __name__ == "__main__":
    main()
