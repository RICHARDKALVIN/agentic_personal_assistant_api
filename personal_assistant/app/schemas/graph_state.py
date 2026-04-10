from typing import TypedDict


class AgentState(TypedDict):
    query : str
    final_reply : str
    intent : dict
    message_to_next : str
    conv_history : str
    
