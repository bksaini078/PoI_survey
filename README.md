# POI Survey Web Application

A Streamlit-based web application for collecting user preferences on Points of Interest (POIs) descriptions and titles.

## Features

- User details collection form
- Dynamic POI comparison pages
- Side-by-side comparison of manual and AI-generated content
- User feedback collection through ratings
- Automatic response saving in CSV format

## Prerequisites

- Python 3.8 or higher
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Data Structure

Place your POI data in `data/pois.json` with the following structure:

```json
{
  "name": "Category Name",
  "color": "color-code",
  "pois": [
    {
      "id": 1,
      "position": [lat, long],
      "title": "POI Title",
      "description": "POI Description",
      "imagesrc": "path/to/image",
      "source": "source-url"
    }
  ]
}
```

## Running the Application

1. Ensure your POI data is in place at `data/pois.json`
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. Open your browser and navigate to the provided URL (typically http://localhost:8501)

## Survey Results

Survey responses are automatically saved in the `survey_results` directory with timestamps in CSV format.

## Project Structure

```
poi_survey/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── data/              # Directory for input data
│   └── pois.json      # POI data file
└── survey_results/    # Directory for survey responses
```

## Contributing

Feel free to submit issues and enhancement requests!
