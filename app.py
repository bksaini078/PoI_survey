"""
POI Survey Application

This application conducts a survey comparing original and AI-generated Point of Interest (POI) descriptions.
It collects user demographic information and preferences, then presents pairs of descriptions for comparison.

The application uses Streamlit for the UI and stores responses in CSV format.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import uuid
from pathlib import Path
import pandas as pd
from pydantic import BaseModel, Field
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import time
import base64
import random


load_dotenv()

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
      img_to_bytes(img_path)
    )
    return img_html

# Constants
NATIONALITIES = [
    "Afghan", "Albanian", "Algerian", "American", "Andorran", "Angolan", "Antiguan", "Argentine", 
    "Armenian", "Australian", "Austrian", "Azerbaijani", "Bahamian", "Bahraini", "Bangladeshi", 
    "Barbadian", "Belarusian", "Belgian", "Belizean", "Beninese", "Bhutanese", "Bolivian", 
    "Bosnian", "Brazilian", "British", "Bruneian", "Bulgarian", "Burkinabe", "Burmese", 
    "Burundian", "Cambodian", "Cameroonian", "Canadian", "Cape Verdean", "Central African", 
    "Chadian", "Chilean", "Chinese", "Colombian", "Comoran", "Congolese", "Costa Rican", 
    "Croatian", "Cuban", "Cypriot", "Czech", "Danish", "Djiboutian", "Dominican", "Dutch", 
    "East Timorese", "Ecuadorian", "Egyptian", "Emirati", "English", "Equatorial Guinean", 
    "Eritrean", "Estonian", "Ethiopian", "Fijian", "Filipino", "Finnish", "French", "Gabonese", 
    "Gambian", "Georgian", "German", "Ghanaian", "Greek", "Grenadian", "Guatemalan", "Guinean", 
    "Guyanese", "Haitian", "Honduran", "Hungarian", "Icelandic", "Indian", "Indonesian", 
    "Iranian", "Iraqi", "Irish", "Israeli", "Italian", "Ivorian", "Jamaican", "Japanese", 
    "Jordanian", "Kazakhstani", "Kenyan", "Korean", "Kuwaiti", "Kyrgyz", "Laotian", "Latvian", 
    "Lebanese", "Liberian", "Libyan", "Lithuanian", "Luxembourg", "Macedonian", "Malagasy", 
    "Malawian", "Malaysian", "Maldivian", "Malian", "Maltese", "Mauritanian", "Mauritian", 
    "Mexican", "Moldovan", "Monacan", "Mongolian", "Montenegrin", "Moroccan", "Mozambican", 
    "Namibian", "Nepalese", "New Zealand", "Nicaraguan", "Nigerian", "Norwegian", "Omani", 
    "Pakistani", "Panamanian", "Papua New Guinean", "Paraguayan", "Peruvian", "Polish", 
    "Portuguese", "Qatari", "Romanian", "Russian", "Rwandan", "Saint Lucian", "Salvadoran", 
    "Samoan", "Saudi", "Scottish", "Senegalese", "Serbian", "Seychellois", "Sierra Leonean", 
    "Singaporean", "Slovak", "Slovenian", "Solomon Islander", "Somali", "South African", 
    "Spanish", "Sri Lankan", "Sudanese", "Surinamese", "Swazi", "Swedish", "Swiss", "Syrian", 
    "Taiwanese", "Tajik", "Tanzanian", "Thai", "Togolese", "Tongan", "Trinidadian", "Tunisian", 
    "Turkish", "Turkmen", "Tuvaluan", "Ugandan", "Ukrainian", "Uruguayan", "Uzbekistani", 
    "Venezuelan", "Vietnamese", "Welsh", "Yemeni", "Zambian", "Zimbabwean"
]

# Define the response model
class POIResponse(BaseModel):
    title: str = Field(..., description="A catchy and informative title for the POI")
    description: str = Field(..., description="An engaging and detailed description of the POI")

# Initialize Azure OpenAI client
@st.cache_resource
def get_openai_client():
    """
    Initialize Azure OpenAI client with API key and endpoint.
    
    Returns:
        AzureOpenAI: Azure OpenAI client instance
    """
    return AzureOpenAI(
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

def generate_ai_content(poi_data, user_data):
    """
    Generate AI content for a given POI and user data.
    
    Uses Azure OpenAI client to generate title and description based on user preferences.
    
    Args:
        poi_data (dict): Dictionary containing POI information
        user_data (dict): Dictionary containing user demographic information and preferences
    
    Returns:
        POIResponse: POIResponse instance containing generated title and description
    """
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
    
    
    prompt = f"""Create a title and description for this Point of Interest, personalized for the following user:
    User Age: {user_data.get('age', 'Not specified')}
    User Gender: {user_data.get('gender', 'Not specified')}
    Marital Status: {user_data.get('marital_status', 'Not specified')}
    Have Children: {user_data.get('has_children', 'Not specified')}
    User Interests: {user_data.get('interests', 'Not specified')}
    User Travel Experience: {user_data.get('travel_experience', 'Not specified')}
    Education Level: {user_data.get('education', 'Not specified')}
    Profession: {user_data.get('profession', 'Not specified')}
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
        # if len(generated_content.title) > max_title_length:
        #     generated_content.title = generated_content.title[:max_title_length].rsplit(' ', 1)[0]
        
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
    """
    Generate AI content for all POIs and save to temporary file.
    
    Args:
        pois (list): List of POI dictionaries
        user_data (dict): Dictionary containing user demographic information and preferences
    
    Returns:
        dict: Dictionary containing generated AI content for each POI
    """
    # Create temp_data directory if it doesn't exist
    temp_dir = Path('temp_data')
    temp_dir.mkdir(exist_ok=True)
    
    temp_file = temp_dir / f'temp_poi_content_{user_data["user_id"]}.json'
    
    # Show loading page with progress
    st.header("Generating Point of Interest Content")
    st.write("Please wait while we create title and descriptions for each Point of Interest...")
    
    # Show progress bar
    progress_text = "Generating content for all POIs..."
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
    """
    Load POI data from the JSON file.
    
    Returns:
        dict: Dictionary containing POI data including categories and descriptions
    """
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
    """
    Save survey responses to a CSV file.
    Creates a new CSV file with timestamp in the filename.
    """
    if not st.session_state.survey_responses:
        return
    
    df = pd.DataFrame(st.session_state.survey_responses)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("survey_results")
    output_dir.mkdir(exist_ok=True)
    df.to_csv(output_dir / f"survey_responses_{timestamp}.csv", index=False)

# User details form
def show_user_details_form():
    """
    Display and process the user details form.
    
    Collects demographic information, preferences, and travel experience.
    Form includes personal information, additional details, and travel preferences.
    
    Returns:
        bool: True if form is submitted successfully, False otherwise
    """
    with st.form("user_details_form"):
        # Personal Information
        # st.markdown('<p class="big-font"><b>Personal Information</b></p>', unsafe_allow_html=True)
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
            has_children = st.selectbox(
                "Do you have children?",
                ["No", "Yes"]
            )
            nationality = st.selectbox(
                "Nationality",
                NATIONALITIES
            )
        
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
            marital_status = st.selectbox(
                "Marital Status",
                ["Single", "Married", "In a Relationship", "Divorced", "Widowed", "Prefer not to say"]
            )
        
        # Additional Information
        # st.markdown('<p class="big-font"><b>Additional Information</b></p>', unsafe_allow_html=True)
        st.subheader("Additional Information")
        col3, col4 = st.columns(2)
        
        with col3:
            disability = st.selectbox(
                "Do you have any disability/accessibility needs?",
                ["No", "Yes"]
            )
            pets = st.selectbox(
                "Do you travel with pets?",
                ["No", "Yes"],
                index=0  # Default to "No"
            )
        
        with col4:
            profession_type = st.selectbox(
                "Profession",
                ["Student", "Academic/Professor", "Engineer", "Doctor/Healthcare", 
                 "Business/Finance", "Artist/Creative", "Government/Public Service",
                 "Self-employed", "Retired", "Other"]
            )
            if profession_type == "Other":
                profession = st.text_input(
                    "Please specify your occupation",
                    help="Enter your specific occupation"
                )
            else:
                profession = profession_type
        
        # Interests and Hobbies
        #st.markdown('<p class="big-font"><b>Interests and Preferences</b></p>', unsafe_allow_html=True)
        st.subheader("Interests and Preferences")
        col5, col6 = st.columns(2)
        
        with col5:
            hobbies = st.multiselect(
                "Hobbies",
                ["Reading", "Writing", "Sports", "Music", "Cooking", "Gaming",
                 "Photography", "Art", "Dancing", "Gardening", "Traveling",
                 "Movies/TV", "Technology", "Fashion", "Fitness", "Other"]
            )
            
            preferred_travel_style = st.multiselect(
                "Preferred Travel Style",
                ["Luxury", "Budget", "Adventure", "Cultural", "Relaxation",
                 "Family-friendly", "Solo", "Group Tours", "Road Trips",
                 "Backpacking", "Eco-tourism"]
            )
        
        with col6:
            interests = st.multiselect(
                "Travel Interests",
                ["History & Culture", "Nature & Outdoors", "Food & Cuisine", 
                 "Architecture", "Art & Museums", "Shopping", "Local Experiences",
                 "Family Activities", "Adventure Sports", "Relaxation", 
                 "Photography", "Religious Sites", "Nightlife", "Festivals"]
            )
            
            travel_experience = st.radio(
                "Travel Experience Level",
                options=["Beginner", "Intermediate", "Experienced", "Expert"],
                help="Select the option that best describes your travel experience level",
                horizontal=True
            )
        st.markdown("""<span style='color: red;'>Please verify if you have filled all required fields before you click submit button</span>""", unsafe_allow_html=True)
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            st.session_state.user_data = {
                'user_id': str(uuid.uuid4()),
                'age': age,
                'gender': gender,
                'marital_status': marital_status,
                'has_children': has_children,
                'nationality': nationality,
                'disability': disability,
                'pets': pets,
                'profession': profession,
                'hobbies': hobbies,
                'interests': interests,
                'travel_experience': travel_experience,
                'preferred_travel_style': preferred_travel_style
            }
            return True
        return False

# POI comparison page
def show_poi_comparison(poi_data, poi_index):
    """
    Display POI comparison page for evaluation.
    
    Shows original and AI-generated descriptions side by side for comparison.
    Collects user ratings and preferences through various assessment criteria.
    
    Args:
        poi_data (dict): Dictionary containing POI information
        poi_index (int): Index of the current POI being compared
    """
    poi = poi_data["pois"][poi_index]
    ai_content = st.session_state.ai_content.get(poi['id'], {
        'title': '[Error loading title]',
        'description': '[Error loading description]'
    })
    
    # Randomly decide which description (manual or AI) appears first
    is_manual_first = random.choice([True, False])
    
    # Store the order in session state for this POI
    if f'order_poi_{poi["id"]}' not in st.session_state:
        st.session_state[f'order_poi_{poi["id"]}'] = is_manual_first
    else:
        is_manual_first = st.session_state[f'order_poi_{poi["id"]}']
    
    # Prepare content based on random order
    description_a = {
        "title": poi["title"] if is_manual_first else ai_content["title"],
        "description": poi["description"] if is_manual_first else ai_content["description"],
        "imagesrc": poi["imagesrc"]
    }
    
    description_b = {
        "title": ai_content["title"] if is_manual_first else poi["title"],
        "description": ai_content["description"] if is_manual_first else poi["description"],
        "imagesrc": poi["imagesrc"]
    }
    
    st.title(f"Point of Interest  - {poi_index + 1}/{len(poi_data['pois'])}")
    
    st.markdown("""
        <style>
        .content-box {
            border: 2px solid #189c7d;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("POI A")
        st.markdown(f"""
            <div style="
                border: 1px solid #189c7d; 
                border-radius: 10px; 
                padding: 20px; 
                background-color: #f9f9f9; 
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
                text-align: center;
                margin-bottom: 20px;">
                {img_to_html(description_a["imagesrc"])}
                <p style="font-size: 24px; color: #189c7d; font-weight: bold; margin: 15px 0;">{description_a["title"]}</p>
                <p style="font-size: 18px; text-align: justify; margin-bottom: 20px;">{description_a["description"]}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="custom-divider" />', unsafe_allow_html=True)
        st.subheader("Assesment for POI A")
        # Assessment Container
        with st.container():
            # st.markdown('<p class="big-font"><b>Value and Services Assessment</b></p>', unsafe_allow_html=True)
            st.markdown('<p class="question-font">Does the description effectively communicate the significance and offerings of the place?</p>', unsafe_allow_html=True)
            manual_significance = st.radio(
                "Significance",
                options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                key=f"manual_significance_{poi_index}",
                horizontal=True,
                label_visibility="collapsed"
            )
        
        with st.container():
            st.markdown('<p class="question-font">How trustworthy does this description appear to be?</p>', unsafe_allow_html=True)
            manual_trust = st.radio(
                "Trust",
                options=["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
                key=f"manual_trust_{poi_index}",
                horizontal=True,
                label_visibility="collapsed"
            )
        
        with st.container():
            st.markdown('<p class="question-font">How clear and complete is the information provided?</p>', unsafe_allow_html=True)
            manual_clarity = st.radio(
                "Clarity",
                options=["Very Unclear", "Unclear", "Neutral", "Clear", "Very Clear"],
                key=f"manual_clarity_{poi_index}",
                horizontal=True,
                label_visibility="collapsed"
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("POI B")
        st.markdown(f"""
            <div style="
                border: 1px solid #189c7d; 
                border-radius: 10px; 
                padding: 20px; 
                background-color: #f9f9f9; 
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
                text-align: center;
                margin-bottom: 20px;">
                {img_to_html(description_b["imagesrc"])}
                <p style="font-size: 24px; color: #189c7d; font-weight: bold; margin: 15px 0;">{description_b["title"]}</p>
                <p style="font-size: 18px; text-align: justify; margin-bottom: 20px;">{description_b["description"]}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="custom-divider" />', unsafe_allow_html=True)
        st.subheader("Assesment for POI B")
        # Assessment Container
        with st.container():
            # st.markdown('<p class="big-font"><b>Value and Services Assessment</b></p>', unsafe_allow_html=True)
            st.markdown('<p class="question-font">Does the description effectively communicate the significance and offerings of the place?</p>', unsafe_allow_html=True)
            ai_significance = st.radio(
                "Significance",
                options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                key=f"ai_significance_{poi_index}",
                horizontal=True,
                label_visibility="collapsed"
            )
        
        with st.container():
            st.markdown('<p class="question-font">How trustworthy does this description appear to be?</p>', unsafe_allow_html=True)
            ai_trust = st.radio(
                "Trust",
                options=["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
                key=f"ai_trust_{poi_index}",
                horizontal=True,
                label_visibility="collapsed"
            )
        
        with st.container():
            st.markdown('<p class="question-font">How clear and complete is the information provided?</p>', unsafe_allow_html=True)
            ai_clarity = st.radio(
                "Clarity",
                options=["Very Unclear", "Unclear", "Neutral", "Clear", "Very Clear"],
                key=f"ai_clarity_{poi_index}",
                horizontal=True,
                label_visibility="collapsed"
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Comparison Questions Section
    st.markdown('<hr class="custom-divider" />', unsafe_allow_html=True)
    st.subheader("Comparison Questions")
    # st.markdown('<p class="big-font"><b>Comparison Questions</b></p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<p class="question-font">Which description did you find more engaging and appealing (captured your attention more)?</p>', unsafe_allow_html=True)
        engaging_preference = st.radio(
            "",
            options=["Description A", "Description B"],
            key=f"engaging_{poi_index}",
            horizontal=True,
            label_visibility="collapsed"
        )
    
    st.markdown('<p class="question-font">Which description did you find more relevant to your interests?</p>', unsafe_allow_html=True)
    relevant_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"relevant_{poi_index}",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown('<p class="question-font">Which description makes you more eager to visit the POI?</p>', unsafe_allow_html=True)
    eager_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"eager_{poi_index}",
        horizontal=True,
        label_visibility="collapsed"
    )
    # st.text("Which Title do you prefer?")
    st.markdown('<p class="question-font">Which Title do you prefer?</p>', unsafe_allow_html=True)
    title_preference = st.radio(
        "",
        options=["Title A", "Title B"],
        key=f"title_{poi_index}",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown('<p class="question-font">Which Description do you prefer?</p>', unsafe_allow_html=True)
    description_preference = st.radio(
        "",
        options=["Description A", "Description B"],
        key=f"description_{poi_index}",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.write("")
    st.markdown("""<span style='color: red;'>Please verify if all required fields are entered.</span>""", unsafe_allow_html=True)
    st.markdown('<hr class="custom-divider" />', unsafe_allow_html=True)

    col1, col2, col3,col4,col5 = st.columns([1, 1, 1, 1, 1])

    with col3:
        # Add page numbers
        st.markdown(f"""
            <div style='
                text-align: left;
                padding: 10px;
                margin-bottom: 10px;
                color: #189c7d;
                font-weight: bold;
                font-size: 1.1em;
            '>
                Page {poi_index + 1} of {len(poi_data["pois"])}
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Next" if poi_index < len(poi_data["pois"]) - 1 else "Finish", type="primary", use_container_width=False):
            # Save response
            response = {
                **st.session_state.user_data,
                "poi_id": poi["id"],
                "poi_title": poi["title"],
                "is_manual_first": is_manual_first,  # Add this to track which description was shown first
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
            st.rerun()

# Thank you page
def show_thank_you():
    """
    Display thank you page after survey completion.
    Shows appreciation message and confirms response recording.
    """
    st.title("Thank You!")
    st.write("Your responses have been recorded. Thank you for participating in the survey!")
    if st.button("Start New Survey", type="primary", use_container_width=False):
        st.session_state.page = 0
        st.session_state.user_data = {}
        st.session_state.survey_responses = []
        st.rerun()

# Set page config
st.set_page_config(
    page_title="POI Survey Application",
    page_icon="logo/icon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add imprint link in top right
col1, col2 = st.columns([0.9, 0.1])
with col2:
    st.markdown('<div style="text-align: right;"><a href="https://www.iao.fraunhofer.de/de/impressum.html" target="_blank" style="color: #189c7d; text-decoration: none;">Imprint</a></div>', unsafe_allow_html=True)

# Custom CSS for theme color and containers
st.markdown("""
    <style>
    /* Primary theme color */
    div.stButton > button:first-child {
        background-color: #189c7d !important;
        color: white !important;
        padding: 0.75rem 2.5rem;
        font-size: 1.1rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        width: auto;
        transition: background-color 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #147c63 !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    div.stButton > button:active {
        background-color: #126e58 !important;
        border-color: #126e58 !important;
    }

    div.stButton > button:focus {
        box-shadow: none;
        outline: none;
        border-color: #189c7d !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #189c7d;
    }
    
    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        border-color: #189c7d;
    }
    
    /* Radio buttons */
    .stRadio > label input[type="radio"]:checked + span::before {
        background-color: #189c7d;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #189c7d;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: rgba(24, 156, 125, 0.1);
        border-left-color: #189c7d;
    }
    
    .big-font {
        font-size: 20px !important;
        font-weight: 500;
    }
    .question-font {
        font-size: 18px !important;
        margin-bottom: 10px;
    }
    .stRadio > label {
        font-size: 16px !important;
    }
    .content-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        min-height: 200px;
        border: 1px solid rgba(24, 156, 125, 0.2);
    }
    .assessment-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid rgba(24, 156, 125, 0.2);
    }
    .custom-divider {
        height: 3px;
        background-color: #189c7d;
        border: none;
        margin: 20px 0;
    }
    
    /* Links */
    a {
        color: #189c7d;
    }
    a:hover {
        color: #148268;
    }
    
    /* Submit button specific styling */
    div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
        background-color: #189c7d;
        color: white;
        border: none;
        font-size: 18px !important;
        padding: 15px 30px !important;
        min-width: 150px;
        height: auto !important;
        border-radius: 5px;
        margin: 10px 0;
    }
    div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {
        background-color: #148268;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Custom styling for image captions */
    .stImage > img + div {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #189c7d !important;
        margin-top: 10px !important;
    }
    button.st-emotion-cache-19rxjzo {
        background-color: #189c7d !important;
        border: 1px solid #189c7d !important;
        padding: 0.75rem 2.5rem !important;
        color: white !important;
    }

    button.st-emotion-cache-19rxjzo:hover {
        background-color: #147c63 !important;
        border-color: #147c63 !important;
        color: white !important;
    }

    button.st-emotion-cache-19rxjzo:active {
        background-color: #126e58 !important;
        border-color: #126e58 !important;
        color: white !important;
    }

    /* Style for form submit button */
    button[kind="primaryFormSubmit"] {
        background-color: #189c7d !important;
        border: 1px solid #189c7d !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = 0

if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

if 'ai_content' not in st.session_state:
    st.session_state.ai_content = {}

if 'survey_responses' not in st.session_state:
    st.session_state.survey_responses = []

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Main app logic
def main():
    """
    Main function to run the POI survey application.
    
    Handles the flow of the survey:
    1. User details collection
    2. POI comparisons
    3. Thank you page
    
    Also manages session state and navigation between pages.
    """
    st.logo("logo/fraunhofer_logo.png",size="large", link=None, icon_image=None)
    if st.session_state.page == 0:
        st.title("Welcome to the POI Survey")
        st.write("Please provide information about yourself to get POI descriptions.")
        
        if show_user_details_form():
            # Load POI data
            poi_data = load_poi_data()
            if not poi_data:
                return
            
            # Show a message before starting content generation
            st.info("Thank you for providing your details! We'll now generate content for your survey...")
            
            # Generate personalized content
            st.session_state.ai_content = generate_all_poi_content(poi_data['pois'], st.session_state.user_data)
            
            # Move to first POI
            st.session_state.page = 1
            st.rerun()
    elif st.session_state.page == -1:
        show_thank_you()
    else:
        poi_data = load_poi_data()
        if not poi_data:
            return
        show_poi_comparison(poi_data, st.session_state.page - 1)
    
if __name__ == "__main__":
    main()
