"""Route handlers for the POI survey application."""

import streamlit as st
import random
from datetime import datetime
from typing import Dict, Optional, Tuple

from config.constants import (
    NATIONALITIES, PROFESSION_TYPES, HOBBIES, TRAVEL_STYLES,
    TRAVEL_INTERESTS, TRAVEL_EXPERIENCE_LEVELS, GENDER_OPTIONS,
    MARITAL_STATUS_OPTIONS, YES_NO_OPTIONS, RATING_SCALE,
    TRUST_SCALE, CLARITY_SCALE
)
from app.models.survey_model import FinalSurveyResponse
from app.services.survey_service import POIService, AIService, SurveyResponseService
from app.utils.helpers import img_to_html

def show_consent_page() -> bool:
    """
    Display the consent page and handle user agreement.
    
    Returns:
        bool: True if user agrees to consent, False otherwise
    """
    st.title("Research Study Consent Form")
    
    st.markdown("""
    ### Purpose of the Study

    The goal of this study is to see how well descriptions of tourist spots, called Points of Interest (POIs), 
    can be customized to match people's preferences and interests. Your feedback will help us understand which 
    methods work best for creating engaging and personalized descriptions. This study is being carried out in 
    partnership with Fraunhofer IAO, Stuttgart, and KU Leuven, Belgium.

    ### What you will do:

    * Share some basic information about yourself, such as your interests and background.
    * For each POI (tourist spot), you will see two versions, A and B, of descriptions created using different methods. Rate how well each version aligns with your preferences.
    * The entire process will take about 20-30 minutes, including a few seconds for loading each page.

    Your participation in this study is entirely voluntary. As a token of appreciation, three participants will be 
    randomly selected to receive a €25 Amazon voucher each.

    All data collected will be kept confidential and used solely for research purposes. Your responses will be 
    anonymized and will not be linked to your identity in any reports or publications.
    """)

    agree = st.button("Agree and Continue")
    
    if agree:
        st.session_state.consent_given = True
        return True
    
    return False

def show_user_details_form() -> bool:
    """
    Display and process the user details form.
    
    Returns:
        bool: True if form is submitted successfully, False otherwise
    """
    with st.form("user_details_form"):
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
            has_children = st.selectbox("Do you have children?", YES_NO_OPTIONS)
            nationality = st.selectbox("Nationality", NATIONALITIES)
            # st.markdown("**Current City** :red[*]")  # Required field indicator
            livein_city = st.text_input(label="Current City*", label_visibility="visible")
        
        with col2:
            gender = st.selectbox("Gender", GENDER_OPTIONS)
            marital_status = st.selectbox("Marital Status", MARITAL_STATUS_OPTIONS)
        
        st.subheader("Additional Information")
        col3, col4 = st.columns(2)
        
        with col3:
            disability = st.selectbox(
                "Do you have any disability/accessibility needs?",
                YES_NO_OPTIONS
            )
            pets = st.selectbox("Do you travel with pets?", YES_NO_OPTIONS)
        
        with col4:
            profession_type = st.selectbox("Profession", PROFESSION_TYPES)
            profession = (
                st.text_input("Please specify your occupation")
                if profession_type == "Other"
                else profession_type
            )
        
        st.subheader("Interests and Preferences")
        col5, col6 = st.columns(2)
        
        with col5:
            # st.markdown("**Hobbies** :red[*] (Select at least 3)")
            hobbies = st.multiselect("Hobbies* (Select at least 3)", HOBBIES, label_visibility="visible")
            # st.markdown("**Preferred Travel Style** :red[*] (Select at least 3)")
            preferred_travel_style = st.multiselect("Preferred Travel Style* (Select at least 3)", TRAVEL_STYLES, label_visibility="visible")
        
        with col6:
            # st.markdown("**Travel Interests** :red[*] (Select at least 3)")
            interests = st.multiselect("Travel Interests* (Select at least 3)", TRAVEL_INTERESTS, label_visibility="visible")
            travel_experience = st.radio(
                "Travel Experience Level",
                options=TRAVEL_EXPERIENCE_LEVELS,
                horizontal=True
            )
        
        st.markdown(
            """
            <div style='color: red; font-size: 0.8em; margin-bottom: 10px;'>
                * Required fields (minimum 3 selections for Hobbies, Travel Style, and Travel Interests)
            </div>
            """,
            unsafe_allow_html=True
        )
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            # Validate required fields
            validation_errors = []
            
            if not livein_city.strip():
                validation_errors.append("Current City is required")
            
            if len(hobbies) < 3:
                validation_errors.append("Please select at least 3 hobbies")
                
            if len(preferred_travel_style) < 3:
                validation_errors.append("Please select at least 3 Preferred Travel Styles")
                
            if len(interests) < 3:
                validation_errors.append("Please select at least 3 Travel Interests")
            
            # Display validation errors if any
            if validation_errors:
                error_message = "Please correct the following errors:\n" + "\n".join(f"- {error}" for error in validation_errors)
                st.error(error_message)
                return False
            
            # If validation passes, save the data
            st.session_state.user_data = {
                'user_id': st.session_state.user_id,
                'age': age,
                'gender': gender,
                'marital_status': marital_status,
                'has_children': has_children,
                'nationality': nationality,
                'city': livein_city,
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

def show_poi_comparison(poi_data: Dict, poi_index: int) -> None:
    """
    Display POI comparison page for evaluation.
    
    Args:
        poi_data (Dict): Dictionary containing POI information
        poi_index (int): Index of the current POI being compared
    """
    poi = poi_data["pois"][poi_index]
    ai_content = st.session_state.ai_content.get(poi['id'], {
        'title': '[Error loading title]',
        'description': '[Error loading description]'
    })
    
    # Randomly decide which description appears first if not already set
    if f'order_poi_{poi["id"]}' not in st.session_state:
        st.session_state[f'order_poi_{poi["id"]}'] = random.choice([True, False])
    
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
    
    _show_poi_descriptions(description_a, description_b, poi_index)
    _show_assessment_forms(poi_index)
    _show_navigation_buttons(poi_data, poi_index, poi, is_manual_first)

def _show_poi_descriptions(description_a: Dict, description_b: Dict, poi_index: int) -> None:
    """Helper function to display POI descriptions."""
    col1, col2 = st.columns(2)

    for col, desc, label in [(col1, description_a, "A"), (col2, description_b, "B")]:
        with col:
            st.subheader(f"Version {label}")
            st.markdown(f"""
                        <div style="border: 1px solid #189c7d; 
                        border-radius: 10px; 
                        padding: 20px; 
                        background-color: #f9f9f9; 
                        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); 
                        text-align: center; 
                        margin-bottom: 20px; 
                        font-family: Arial, sans-serif;">
                        <div style="max-width: 100%; margin: 0 auto;">
                            {img_to_html(desc["imagesrc"])}
                        </div>
                        <p style="
                            font-size: 1.5em; 
                            color: #189c7d; 
                            font-weight: bold; 
                            margin: 15px 0;">
                            {desc["title"]}
                        </p>
                        <p style="
                            font-size: 1em; 
                            text-align: justify; 
                            color: #333333; 
                            line-height: 1.5; 
                            margin-bottom: 20px;">
                            {desc["description"]}
                        </p>
                    </div>""",
                    unsafe_allow_html=True)

            st.markdown('<hr class="custom-divider" />', unsafe_allow_html=True)
            _show_assessment_section(label, poi_index)

def _show_assessment_section(label: str, poi_index: int) -> None:
    """Helper function to display assessment section for a POI description."""
    st.subheader(f"Assessment for version {label}")
    
    with st.container():
        st.markdown(
            '<p class="question-font">Does the description effectively communicate the significance and offerings of the place?</p>',
            unsafe_allow_html=True
        )
        options = ["No Selection"] + list(RATING_SCALE)
        st.radio(
            "Significance",
            options=options,
            key=f"{'manual' if label == 'A' else 'ai'}_significance_{poi_index}",
            horizontal=True,
            label_visibility="collapsed",
            index=0  # Set "No Selection" as default
        )
    
    with st.container():
        st.markdown(
            '<p class="question-font">How trustworthy does this description appear to be?</p>',
            unsafe_allow_html=True
        )
        options = ["No Selection"] + list(TRUST_SCALE)
        st.radio(
            "Trust",
            options=options,
            key=f"{'manual' if label == 'A' else 'ai'}_trust_{poi_index}",
            horizontal=True,
            label_visibility="collapsed",
            index=0  # Set "No Selection" as default
        )
    
    with st.container():
        st.markdown(
            '<p class="question-font">How clear and complete is the information provided?</p>',
            unsafe_allow_html=True
        )
        options = ["No Selection"] + list(CLARITY_SCALE)
        st.radio(
            "Clarity",
            options=options,
            key=f"{'manual' if label == 'A' else 'ai'}_clarity_{poi_index}",
            horizontal=True,
            label_visibility="collapsed",
            index=0  # Set "No Selection" as default
        )

def _show_assessment_forms(poi_index: int) -> None:
    """Helper function to display comparative assessment forms."""
    st.markdown("---")
    st.subheader("Comparative Assessment")
    
    # More engaging description
    st.markdown('<p class="question-font">Which description was more engaging?</p>', unsafe_allow_html=True)
    st.radio(
        "Engaging",
        options=["No Selection", "Version A", "Version B", "Both equally"],
        key=f"engaging_{poi_index}",
        horizontal=True,
        label_visibility="collapsed",
        index=0  # Set "No Selection" as default
    )
    
    # More relevant description
    st.markdown('<p class="question-font">Which description provided more relevant information?</p>', unsafe_allow_html=True)
    st.radio(
        "Relevant",
        options=["No Selection", "Version A", "Version B", "Both equally"],
        key=f"relevant_{poi_index}",
        horizontal=True,
        label_visibility="collapsed",
        index=0  # Set "No Selection" as default
    )
    
    # More eager to visit
    st.markdown('<p class="question-font">Based on which description would you be more eager to visit this place?</p>', unsafe_allow_html=True)
    st.radio(
        "Eager",
        options=["No Selection", "Version A", "Version B", "Both equally"],
        key=f"eager_{poi_index}",
        horizontal=True,
        label_visibility="collapsed",
        index=0  # Set "No Selection" as default
    )
    
    # Better title
    st.markdown('<p class="question-font">Which title was more appealing?</p>', unsafe_allow_html=True)
    st.radio(
        "Title",
        options=["No Selection", "Version A", "Version B", "Both equally"],
        key=f"title_{poi_index}",
        horizontal=True,
        label_visibility="collapsed",
        index=0  # Set "No Selection" as default
    )
    
    # Better description
    st.markdown('<p class="question-font">Overall, which description was better?</p>', unsafe_allow_html=True)
    st.radio(
        "Description",
        options=["No Selection", "Version A", "Version B", "Both equally"],
        key=f"description_{poi_index}",
        horizontal=True,
        label_visibility="collapsed",
        index=0  # Set "No Selection" as default
    )
    st.markdown("---")
    st.subheader("General Question")
    st.markdown('<p class="question-font">What is your familiarity with this place?</p>', unsafe_allow_html=True)
    st.radio(
        "Visited",
        options=["No Selection","I have visited it in person.", "I have seen/heard about it online or from others.", "I have never heard of it before."],
        key=f"isvisited_{poi_index}",
        horizontal=False,
        label_visibility="collapsed",
        index=0  # Set "No Selection" as default
    )

def _show_navigation_buttons(poi_data: Dict, poi_index: int, poi: Dict, is_manual_first: bool) -> None:
    """Helper function to display navigation buttons and handle navigation logic."""
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col3:
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
        
        if st.button("Next" if poi_index < len(poi_data["pois"]) - 1 else "Finish", type="primary"):
            _handle_navigation(poi_data, poi_index, poi, is_manual_first)

def _validate_responses(poi_index: int) -> Tuple[bool, list]:
    """Helper function to validate that all questions have been answered.
    
    Returns:
        Tuple[bool, list]: A tuple containing:
            - bool: True if all questions are answered, False otherwise
            - list: List of unanswered questions
    """
    fields_to_check = {
        f"manual_significance_{poi_index}": "Significance rating for Version A",
        f"manual_trust_{poi_index}": "Trust rating for Version A",
        f"manual_clarity_{poi_index}": "Clarity rating for Version A",
        f"ai_significance_{poi_index}": "Significance rating for Version B",
        f"ai_trust_{poi_index}": "Trust rating for Version B",
        f"ai_clarity_{poi_index}": "Clarity rating for Version B",
        f"engaging_{poi_index}": "Which description was more engaging",
        f"relevant_{poi_index}": "Which description provided more relevant information",
        f"eager_{poi_index}": "Which description would make you more eager to visit",
        f"title_{poi_index}": "Which title was more appealing",
        f"description_{poi_index}": "Overall better description",
        f"isvisited_{poi_index}": "Your familiarity with this place"
    }
    
    unanswered_questions = []
    for field, question_text in fields_to_check.items():
        if st.session_state[field] == "No Selection" :
            unanswered_questions.append(question_text)
    
    return len(unanswered_questions) == 0, unanswered_questions

def _handle_navigation(poi_data: Dict, poi_index: int, poi: Dict, is_manual_first: bool) -> None:
    """Helper function to handle navigation logic and response saving."""
    # Validate all questions have been answered
    is_valid, unanswered_questions = _validate_responses(poi_index)
    if not is_valid:
        error_message = "Please answer the following questions before proceeding:\n" + "\n".join(f"- {q}" for q in unanswered_questions)
        st.error(error_message)
        return
    
    response = {
        **st.session_state.user_data,
        "poi_id": poi["id"],
        "poi_title": poi["title"],
        "is_manual_first": is_manual_first,
        "manual_significance": st.session_state[f"manual_significance_{poi_index}"],
        "manual_trust": st.session_state[f"manual_trust_{poi_index}"],
        "manual_clarity": st.session_state[f"manual_clarity_{poi_index}"],
        "ai_significance": st.session_state[f"ai_significance_{poi_index}"],
        "ai_trust": st.session_state[f"ai_trust_{poi_index}"],
        "ai_clarity": st.session_state[f"ai_clarity_{poi_index}"],
        "engaging_preference": st.session_state[f"engaging_{poi_index}"],
        "relevant_preference": st.session_state[f"relevant_{poi_index}"],
        "eager_preference": st.session_state[f"eager_{poi_index}"],
        "title_preference": st.session_state[f"title_{poi_index}"],
        "description_preference": st.session_state[f"description_{poi_index}"],
        "already_visited":st.session_state[f"isvisited_{poi_index}"],
        "timestamp": datetime.now().isoformat()
    }
    
    st.session_state.survey_responses.append(response)
    
    if poi_index < len(poi_data["pois"]) - 1:
        st.session_state.page += 1
    else:
        SurveyResponseService.save_response(st.session_state.survey_responses)
        st.session_state.page = -1
    
    st.rerun()

def show_thank_you() -> None:
    """Display thank you page with final survey questions and lottery entry."""
    st.title("Final Survey")
    
    # Overall Experience
    st.subheader("Overall Experience")
    st.write("How would you rate your overall experience with the POI descriptions provided in this study?")
    overall_rating = st.radio(
        "Overall Experience Rating (1 = Very Poor, 5 = Excellent)",
        options=["No Selection", 1, 2, 3, 4, 5],
        horizontal=True,
        index=0  # Set "No Selection" as default
    )
    comments = st.text_area("Comments (optional)", height=68)
    
    # Perception of Automated Adaptation
    st.subheader("Perception of Automated Adaptation")
    st.write("What is your opinion on the idea of automatically adapting POI descriptions based on user interests?")
    adaptation_rating = st.radio(
        "Adaptation Rating (1 = Very negative, 5 = Very positive)",
        options=["No Selection", 1, 2, 3, 4, 5],
        horizontal=True,
        index=0  # Set "No Selection" as default
    )
    
    # Comfort with AI-Generated Content
    st.subheader("Comfort with AI-Generated Content")
    st.write("How comfortable are you with reading AI-generated descriptions when planning visits to new places?")
    ai_comfort_rating = st.radio(
        "AI Comfort Rating (1 = Not comfortable at all, 5 = Very comfortable)",
        options=["No Selection", 1, 2, 3, 4, 5],
        horizontal=True,
        index=0  # Set "No Selection" as default
    )
    
    # Final Feedback
    st.subheader("Final Feedback")
    st.write("Do you have any additional comments or suggestions regarding the descriptions, the concept of adaptation, or your overall experience during the study?")
    final_feedback = st.text_area("Additional Comments (Optional)", height=68)
    
    # Thank You Message and Email Collection
    st.markdown("---")
    st.subheader("Thank You for Your Participation!")
    st.write("We greatly appreciate your time and effort in completing this study.")
    st.write("As mentioned at the beginning, if you would like to enter the lottery for a chance to win a €25 Amazon voucher, please provide your contact email below:")
    
    email = st.text_input("Email")
    
    if st.button("Submit", type="primary"):
        # Convert "No Selection" to None for rating fields
        final_response = FinalSurveyResponse(
            timestamp=datetime.now(),
            overall_rating=None if overall_rating == "No Selection" else overall_rating,
            comments=comments,
            adaptation_rating=None if adaptation_rating == "No Selection" else adaptation_rating,
            ai_comfort_rating=None if ai_comfort_rating == "No Selection" else ai_comfort_rating,
            final_feedback=final_feedback,
            lottery_email=email
        )
        
        SurveyResponseService.save_final_response(final_response)
        st.success("Thank you! Your responses have been saved. You may now close this survey.")
