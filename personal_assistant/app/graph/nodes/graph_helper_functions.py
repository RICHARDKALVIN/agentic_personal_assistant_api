from app.schemas.graph_state import AgentState
from langgraph.graph import END


def intent_checker(state : AgentState):
    intent = state["intent"]
    if intent["is_follow_up"]:
        return "follow_up"
    if intent["is_general"]:
        return "general_conv"
    elif intent["is_reservation"]:
        return "field_check"
    elif intent["need_web_search"]:
        return "web_search"
    else:
        return END

def retry_router(state : AgentState):
    
    if state["action"] == "book_hotel":
        return "hotel_search"
    else:
        return END
    
def task_router(state : AgentState):
    
    if state["action"] == "book_hotel":
        return "book_hotel"
    else:
        return END


  