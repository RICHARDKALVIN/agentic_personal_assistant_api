from typing import TypedDict,Optional


class AgentState(TypedDict):
    query : str
    session_id : str
    final_reply : str
    intent : dict
    message_to_next : str
    conv_history : str
    search_results: Optional[list]
    selected_hotel: Optional[dict]
    action: Optional[str]