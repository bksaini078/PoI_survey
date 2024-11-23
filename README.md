# POI Survey Application

A sophisticated survey application that compares original Point of Interest (POI) descriptions with AI-generated alternatives, collecting user feedback and preferences.

## Features

### User Profiling
- Comprehensive demographic information collection
- Travel preferences and experience level assessment
- Accessibility needs consideration
- Pet travel preferences
- Professional background collection

### POI Comparison System
- Side-by-side comparison of original and AI-generated descriptions
- Multiple assessment criteria:
  - Communication effectiveness
  - Trust level
  - Clarity of information
  - Engagement level
  - Relevance to user interests
  - Visit motivation
  - Title and description preferences

### AI Integration
- Azure OpenAI integration for content generation
- Personalized POI descriptions based on user profile
- Dynamic content adaptation to match original description length

### Data Collection
- UUID-based user tracking
- Comprehensive response storage in CSV format
- Timestamp-based file organization

## Technical Stack

- **Frontend**: Streamlit
- **AI Service**: Azure OpenAI (GPT-4)
- **Data Storage**: CSV, JSON
- **Language**: Python 3.x

## Dependencies

```
streamlit
pandas
openai
python-dotenv
uuid
pathlib
```

## Project Structure

```
PoI_survey/
├── app.py              # Main application file
├── data/
│   └── pois.json      # POI descriptions and metadata
├── survey_results/     # Survey response storage
├── assets/
│   └── images/        # POI images
├── temp_data/         # Temporary AI-generated content
└── .env               # Environment variables
```

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bksaini078/PoI_survey.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with:
   ```
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **User Information Collection**
   - Fill in demographic details
   - Select travel preferences
   - Indicate experience level

2. **POI Comparison**
   - View original and AI-generated descriptions
   - Rate various aspects of each description
   - Indicate preferences between versions

3. **Data Collection**
   - Responses automatically saved to CSV
   - Unique session ID assigned to each survey
   - Timestamps added to all responses

## Styling

The application uses a consistent color theme (#189c7d) and responsive design elements:
- Large, readable fonts for descriptions
- Horizontal radio buttons for easy comparison
- Clear section dividers
- Responsive image sizing

## Data Security

- No personal identifying information stored
- UUID-based session tracking
- Secure API key management
- Local data storage

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Stuttgart Tourism Board for POI information
- Streamlit team for the framework
- Azure OpenAI team for API support
