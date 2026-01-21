from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatStartResponse(BaseModel):
    session_id: str
    message: str


class ChatMessageRequest(BaseModel):
    session_id: str
    user_message: str


class ChatMessageResponse(BaseModel):
    session_id: str
    message: str
    state: str
    data_collected: Dict[str, Any] = Field(default_factory=dict)
    user_data: Optional[Dict[str, Any]] = None  # For dashboard updates


class RecommendationRequest(BaseModel):
    # If you want to bypass chat flow and directly request recommendations
    name: str
    sex: str
    age: int
    height_m: float
    weight_kg: float
    hypertension: str  # "Yes"/"No"
    diabetes: str      # "Yes"/"No"
    wants_videos: bool = True


class WorkoutItem(BaseModel):
    id: int
    title: str
    youtube_link: str
    channel: str
    duration: int
    difficulty: str
    category: str
    equipment: List[str]
    calories_burned: int
    goal: str
    muscle_groups: List[str]
    description: str


class RecommendationResponse(BaseModel):
    name: str
    bmi: float
    level: str
    plan: Dict[str, Any]
    workouts: List[WorkoutItem]
    safety_note: str
