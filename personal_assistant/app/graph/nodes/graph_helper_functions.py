from app.schemas.graph_state import AgentState
from langgraph.graph import END


def intent_checker(state : AgentState):
    intent = state["intent"]
    if intent["is_follow_up"]:
        return "follow_up"
    if intent["is_general"]:
        return "general_conv"
    elif intent["is_reservation"]:
        return "hotel_check"
    else:
        return END

def feild_checker(state : AgentState):
    
    if state["message_to_next"] == "continue":
        return "next"
    else:
        return END


  