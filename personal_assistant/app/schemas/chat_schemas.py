from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str
    session_id :str
    message: str

class ChatResponse(BaseModel):
    response: str


class IntentResponse(BaseModel):
    is_general: bool = Field(
        ..., description="True if the user query is a general greeting, joke, or off-topic."
    )
    need_web_search: bool = Field(
        ..., description="True if the user query requires web search."
    )
    is_follow_up: bool = Field(
        ..., description="if query based on follow up "
    )
    general_reply: Optional[str] = Field(
        default=None, description="General greeting, joke, or off-topic reply."
    )
    is_reservation: bool = Field(
        default=False, description="True if the query is for booking or checking hotel availability."
    )
    city: Optional[str] = Field(
        default=None, description="City name, e.g., 'mumbai'."
    )
    hotel_name: Optional[str] = Field(
        default=None, description="Specific hotel name."
    )
    locality: Optional[str] = Field(
        default=None, description="Specific area within a city, e.g., 'bandra'."
    )
    
    date_and_time: Optional[datetime] = Field(
        default=None, description="ISO 8601 formatted date and time for the stay."
    )
