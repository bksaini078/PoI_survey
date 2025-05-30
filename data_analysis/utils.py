"""Utility functions for data processing pipeline."""

import pandas as pd
import glob
import os
from typing import List, Tuple
import ast

def load_survey_responses(directory: str, pattern: str) -> pd.DataFrame:
    """
    Load and combine all survey response files.
    
    Args:
        directory: Directory containing the files
        pattern: File pattern to match
        
    Returns:
        Combined DataFrame of all survey responses
    """
    files = glob.glob(os.path.join(directory, pattern))
    dfs = []
    
    for file in files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)

def process_survey_responses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process survey responses data.
    
    Args:
        df: Raw survey responses DataFrame
        
    Returns:
        Processed DataFrame
    """
    # Convert string lists to actual lists
    list_columns = ['hobbies', 'interests', 'preferred_travel_style']
    for col in list_columns:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Add derived columns
    df['response_date'] = df['timestamp'].dt.date
    df['response_time'] = df['timestamp'].dt.time
    
    # Calculate preference scores
    preference_cols = ['engaging_preference', 'relevant_preference', 'eager_preference',
                      'title_preference', 'description_preference']
    
    for col in preference_cols:
        df[f'{col}_score'] = df[col].map({
            'Version A': 1,  # Manual version
            'Version B': -1,  # AI version
            'Both equally': 0
        })
    
    return df

def process_final_responses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process final responses data.
    
    Args:
        df: Raw final responses DataFrame
        
    Returns:
        Processed DataFrame
    """
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Add derived columns
    df['response_date'] = df['timestamp'].dt.date
    df['response_time'] = df['timestamp'].dt.time
    
    # Convert ratings to numeric
    rating_cols = ['overall_rating', 'adaptation_rating', 'ai_comfort_rating']
    for col in rating_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def aggregate_user_responses(survey_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate responses by user.
    
    Args:
        survey_df: Processed survey responses DataFrame
        
    Returns:
        DataFrame with user-level aggregations
    """
    # Group by user_id and calculate aggregations
    user_aggs = survey_df.groupby('user_id').agg({
        'age': 'first',
        'gender': 'first',
        'nationality': 'first',
        'city': 'first',
        'travel_experience': 'first',
        'engaging_preference_score': 'mean',
        'relevant_preference_score': 'mean',
        'eager_preference_score': 'mean',
        'title_preference_score': 'mean',
        'description_preference_score': 'mean',
        'manual_significance': lambda x: x.map({
            'Strongly Agree': 5, 'Agree': 4, 'Neutral': 3,
            'Disagree': 2, 'Strongly Disagree': 1
        }).mean(),
        'ai_significance': lambda x: x.map({
            'Strongly Agree': 5, 'Agree': 4, 'Neutral': 3,
            'Disagree': 2, 'Strongly Disagree': 1
        }).mean()
    }).reset_index()
    
    return user_aggs
