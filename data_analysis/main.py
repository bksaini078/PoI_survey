"""Main script for processing survey response data."""

import os
import pandas as pd
from utils import (
    load_survey_responses,
    process_survey_responses,
    process_final_responses,
    aggregate_user_responses
)
import config

def main():
    """Main function to process survey data."""
    # Create output directory if it doesn't exist
    os.makedirs('processed_data', exist_ok=True)
    
    # Load and process survey responses
    print("Loading survey responses...")
    survey_df = load_survey_responses(
        config.SURVEY_RESULTS_DIR,
        config.SURVEY_RESPONSES_PATTERN
    )
    
    print("Processing survey responses...")
    processed_survey_df = process_survey_responses(survey_df)
    
    # Load and process final responses
    print("Loading final responses...")
    final_df = load_survey_responses(
        config.SURVEY_RESULTS_DIR,
        config.FINAL_RESPONSES_PATTERN
    )
    
    print("Processing final responses...")
    processed_final_df = process_final_responses(final_df)
    
    # Generate user-level aggregations
    print("Generating user aggregations...")
    user_aggs_df = aggregate_user_responses(processed_survey_df)
    
    # Save processed data
    print("Saving processed data...")
    processed_survey_df.to_csv(
        os.path.join('processed_data', config.SURVEY_RESPONSES_OUTPUT),
        index=False
    )
    processed_final_df.to_csv(
        os.path.join('processed_data', config.FINAL_RESPONSES_OUTPUT),
        index=False
    )
    
    # Print summary statistics
    print("\nProcessing complete! Summary:")
    print(f"Total survey responses: {len(processed_survey_df['user_id'].unique())}")
    print(f"Total final responses: {len(processed_final_df)}")
    
    # Calculate and print preference statistics
    preference_cols = [col for col in processed_survey_df.columns if col.endswith('_score')]
    print("\nPreference Statistics:")
    for col in preference_cols:
        scores = processed_survey_df[col].mean()
        print(f"{col}: {scores:.2f} (-1 = AI preferred, 1 = Manual preferred)")
    
    print("\nFiles saved in processed_data/")

if __name__ == "__main__":
    main()
