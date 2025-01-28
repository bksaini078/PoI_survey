"""Configuration settings for the data processing pipeline."""

# Input directories
SURVEY_RESULTS_DIR = "../survey_results"

# Output files
SURVEY_RESPONSES_OUTPUT = "processed_survey_responses.csv"
FINAL_RESPONSES_OUTPUT = "processed_final_responses.csv"

# File patterns
SURVEY_RESPONSES_PATTERN = "survey_responses_*.csv"
FINAL_RESPONSES_PATTERN = "final_responses_*.csv"

# Column configurations
DEMOGRAPHIC_COLS = [
    'user_id', 'age', 'gender', 'marital_status', 'has_children',
    'nationality', 'city', 'disability', 'pets', 'profession',
    'hobbies', 'interests', 'travel_experience', 'preferred_travel_style'
]

POI_RESPONSE_COLS = [
    'poi_id', 'poi_title', 'is_manual_first',
    'manual_significance', 'manual_trust', 'manual_clarity',
    'ai_significance', 'ai_trust', 'ai_clarity',
    'engaging_preference', 'relevant_preference', 'eager_preference',
    'title_preference', 'description_preference', 'already_visited'
]

FINAL_RESPONSE_COLS = [
    'timestamp', 'overall_rating', 'comments', 'adaptation_rating',
    'ai_comfort_rating', 'final_feedback', 'lottery_email'
]
