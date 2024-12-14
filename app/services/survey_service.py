"""Services for handling POI survey business logic."""

import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional
import streamlit as st
from openai import AzureOpenAI

from app.models.survey_model import (
    POIResponse, POIData, POICategory,
    UserData, SurveyResponse, FinalSurveyResponse
)

class POIService:
    """Service for handling POI data operations."""
    
    @staticmethod
    def load_poi_data() -> Optional[Dict]:
        """
        Load POI data from the JSON file.
        
        Returns:
            Optional[Dict]: Dictionary containing POI data including categories and descriptions
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

class AIService:
    """Service for handling AI content generation."""
    
    @staticmethod
    @st.cache_resource
    def get_openai_client() -> AzureOpenAI:
        """
        Initialize Azure OpenAI client with API key and endpoint.
        
        Returns:
            AzureOpenAI: Azure OpenAI client instance
        """
        return AzureOpenAI(
            api_version=st.secrets['secrets']["AZURE_OPENAI_API_VERSION"],
            api_key=st.secrets['secrets']["AZURE_OPENAI_API_KEY"],
            azure_endpoint=st.secrets['secrets']["AZURE_OPENAI_ENDPOINT"]
        )

    @classmethod
    def generate_ai_content(cls, poi_data: Dict, user_data: Dict) -> POIResponse:
        """
        Generate AI content for a given POI and user data.
        
        Uses Azure OpenAI client to generate title and description based on user preferences.
        
        Args:
            poi_data (Dict): Dictionary containing POI information
            user_data (Dict): Dictionary containing user demographic information and preferences
        
        Returns:
            POIResponse: POIResponse instance containing generated title and description
        """
        client = cls.get_openai_client()
        
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
        - Your title MUST be {max_title_length} characters or less"""
        
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format=POIResponse,
            )
            
            generated_content = completion.choices[0].message.parsed
            
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

    @classmethod
    def generate_all_poi_content(cls, pois: List[Dict], user_data: Dict) -> Dict:
        """
        Generate AI content for all POIs and save to temporary file.
        
        Args:
            pois (List[Dict]): List of POI dictionaries
            user_data (Dict): Dictionary containing user demographic information and preferences
        
        Returns:
            Dict: Dictionary containing generated AI content for each POI
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
                content = cls.generate_ai_content(poi, user_data)
                ai_content[poi['id']] = {
                    'title': content.title,
                    'description': content.description
                }
                # Update progress
                progress_bar.progress((i + 1) / len(pois))
        
        # Save to temporary file
        with open(temp_file, 'w') as f:
            json.dump(ai_content, f)
        
        progress_bar.empty()
        return ai_content

class SurveyResponseService:
    """Service for handling survey response operations."""
    
    @staticmethod
    def save_response(responses: List[Dict]) -> None:
        """
        Save survey responses to a CSV file.
        Creates a new CSV file with timestamp in the filename.
        
        Args:
            responses (List[Dict]): List of survey response dictionaries
        """
        if not responses:
            return
        
        df = pd.DataFrame(responses)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("survey_results")
        output_dir.mkdir(exist_ok=True)
        df.to_csv(output_dir / f"survey_responses_{timestamp}.csv", index=False)

    @staticmethod
    def save_final_response(response: FinalSurveyResponse) -> None:
        """
        Save final survey response to CSV.
        
        Args:
            response (FinalSurveyResponse): Final survey response data
        """
        csv_filename = f"survey_results/final_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        Path("survey_results").mkdir(exist_ok=True)
        
        response_dict = response.dict()
        df = pd.DataFrame([response_dict])
        df.to_csv(csv_filename, index=False)
