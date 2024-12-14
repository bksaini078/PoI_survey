"""Data models for the POI survey application."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class POIResponse(BaseModel):
    """Model for POI content response."""
    title: str = Field(..., description="A catchy and informative title for the POI")
    description: str = Field(..., description="An engaging and detailed description of the POI")

class UserData(BaseModel):
    """Model for user demographic and preference data."""
    user_id: str
    age: int
    gender: str
    marital_status: str
    has_children: str
    nationality: str
    disability: str
    pets: str
    profession: str
    hobbies: List[str]
    interests: List[str]
    travel_experience: str
    preferred_travel_style: List[str]

class SurveyResponse(BaseModel):
    """Model for individual POI comparison responses."""
    user_id: str
    poi_id: str
    poi_title: str
    is_manual_first: bool
    manual_significance: str
    manual_trust: str
    manual_clarity: str
    ai_significance: str
    ai_trust: str
    ai_clarity: str
    engaging_preference: str
    relevant_preference: str
    eager_preference: str
    title_preference: str
    description_preference: str
    timestamp: datetime

class FinalSurveyResponse(BaseModel):
    """Model for final survey feedback."""
    timestamp: datetime
    overall_rating: int
    comments: Optional[str]
    adaptation_rating: int
    ai_comfort_rating: int
    final_feedback: Optional[str]
    lottery_email: Optional[str]

class POIData(BaseModel):
    """Model for POI data."""
    id: str
    title: str
    description: str
    imagesrc: str

class POICategory(BaseModel):
    """Model for POI category."""
    name: str
    color: str
    pois: List[POIData]
