"""Configuration constants for the POI survey application."""

# List of nationalities for the survey form
NATIONALITIES = [
    "German","Afghan", "Albanian", "Algerian", "American", "Andorran", "Angolan", "Antiguan", "Argentine", 
    "Armenian", "Australian", "Austrian", "Azerbaijani", "Bahamian", "Bahraini", "Bangladeshi", 
    "Barbadian", "Belarusian", "Belgian", "Belizean", "Beninese", "Bhutanese", "Bolivian", 
    "Bosnian", "Brazilian", "British", "Bruneian", "Bulgarian", "Burkinabe", "Burmese", 
    "Burundian", "Cambodian", "Cameroonian", "Canadian", "Cape Verdean", "Central African", 
    "Chadian", "Chilean", "Chinese", "Colombian", "Comoran", "Congolese", "Costa Rican", 
    "Croatian", "Cuban", "Cypriot", "Czech", "Danish", "Djiboutian", "Dominican", "Dutch", 
    "East Timorese", "Ecuadorian", "Egyptian", "Emirati", "English", "Equatorial Guinean", 
    "Eritrean", "Estonian", "Ethiopian", "Fijian", "Filipino", "Finnish", "French", "Gabonese", 
    "Gambian", "Georgian", "Ghanaian", "Greek", "Grenadian", "Guatemalan", "Guinean", 
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

# Form options for profession types
PROFESSION_TYPES = [
    "Student", "Academic/Professor", "Engineer", "Doctor/Healthcare", 
    "Business/Finance", "Artist/Creative", "Government/Public Service",
    "Self-employed", "Retired", "Other"
]

# Form options for hobbies
HOBBIES = [
    "Reading", "Writing", "Sports", "Music", "Cooking", "Gaming",
    "Photography", "Art", "Dancing", "Gardening", "Traveling",
    "Movies/TV", "Technology", "Fashion", "Fitness", "Other"
]

# Form options for travel styles
TRAVEL_STYLES = [
    "Luxury", "Budget", "Adventure", "Cultural", "Relaxation",
    "Family-friendly", "Solo", "Group Tours", "Road Trips",
    "Backpacking", "Eco-tourism"
]

# Form options for travel interests
TRAVEL_INTERESTS = [
    "History & Culture", "Nature & Outdoors", "Food & Cuisine", 
    "Architecture", "Art & Museums", "Shopping", "Local Experiences",
    "Family Activities", "Adventure Sports", "Relaxation", 
    "Photography", "Religious Sites", "Nightlife", "Festivals"
]

# Form options for travel experience levels
TRAVEL_EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Experienced", "Expert"]

# Form options for gender
GENDER_OPTIONS = ["Male", "Female", "Non-binary", "Prefer not to say"]

# Form options for marital status
MARITAL_STATUS_OPTIONS = [
    "Single", "Married", "In a Relationship", "Divorced", "Widowed", "Prefer not to say"
]

# Form options for yes/no questions
YES_NO_OPTIONS = ["No", "Yes"]

# Rating scale options
RATING_SCALE = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
TRUST_SCALE = ["Not at all", "Slightly", "Moderately", "Very", "Extremely"]
CLARITY_SCALE = ["Very Unclear", "Unclear", "Neutral", "Clear", "Very Clear"]

# Custom CSS styles
CUSTOM_CSS = """
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
"""
