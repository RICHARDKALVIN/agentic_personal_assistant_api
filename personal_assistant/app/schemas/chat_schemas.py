from pydantic import BaseModel,Field
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str
    session_id :str
    message: str

class ChatResponse(BaseModel):
    user_id: str
    session_id: str
    response: str


class Hotel_details(BaseModel):
    id: str = Field(...,description="hotel id for booking")
    name: str = Field(...,description="hotel name for booking")

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
    preferences: Optional[str] = Field(
        default=None, description="User preferences about the hotel, e.g., 'romantic', 'budget-friendly'."
    )
    budget: Optional[int] = Field(
        default=None, description="Budget for the stay, e.g., 500."
    )
    
    check_in: Optional[str] = Field(
        default=None, description="ISO 8601 formatted date and time for the stay."
    )
    check_out: Optional[str] = Field(
        default=None, description="ISO 8601 formatted date and time for the stay."
    )
    guests: Optional[int] = Field(
        default=None, description="Number of guests."
    )
    selected_hotel: Optional[Hotel_details] = Field(
        default=None, description="Hotel details for booking"
    )


