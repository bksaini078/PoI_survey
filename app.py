"""
POI Survey Application

This application conducts a survey comparing original and AI-generated Point of Interest (POI) descriptions.
It collects user demographic information and preferences, then presents pairs of descriptions for comparison.

The application uses Streamlit for the UI and stores responses in CSV format.
"""

import streamlit as st
from app.utils.helpers import (
    set_page_config,
    add_custom_css,
    initialize_session_state,
    add_imprint_link
)
from app.routes.survey_routes import (
    show_consent_page,
    show_user_details_form,
    show_poi_comparison,
    show_thank_you
)
from app.services.survey_service import POIService, AIService

def main():
    """
    Main function to run the POI survey application.
    
    Handles the flow of the survey:
    1. Consent page
    2. User details collection
    3. POI comparisons
    4. Thank you page
    
    Also manages session state and navigation between pages.
    """
    # Configure page settings
    set_page_config()
    add_custom_css()
    initialize_session_state()
    
    # Display Fraunhofer logo
    st.image("logo/fraunhofer_logo.png", width=200)
    
    # Add imprint link
    add_imprint_link()

    # Handle different pages based on session state
    if st.session_state.page == -2:
        if show_consent_page():
            st.session_state.page = 0
            st.rerun()
            
    elif st.session_state.page == 0:
        if not st.session_state.consent_given:
            st.session_state.page = -2
            st.rerun()
            
        st.title("Welcome to the POI Survey")
        st.write("Please provide information about yourself to get POI descriptions.")
        
        if show_user_details_form():
            # Load POI data
            poi_data = POIService.load_poi_data()
            if not poi_data:
                return
            
            # Show a message before starting content generation
            st.info("Thank you for providing your details! We'll now generate content for your survey...")
            
            # Generate personalized content
            st.session_state.ai_content = AIService.generate_all_poi_content(
                poi_data['pois'],
                st.session_state.user_data
            )
            
            # Move to first POI
            st.session_state.page = 1
            st.rerun()
            
    elif st.session_state.page == -1:
        show_thank_you()
        
    else:
        if not st.session_state.consent_given:
            st.session_state.page = -2
            st.rerun()
            
        poi_data = POIService.load_poi_data()
        if not poi_data:
            return
        show_poi_comparison(poi_data, st.session_state.page - 1)

if __name__ == "__main__":
    main()
