from langgraph.graph import END, StateGraph
from app.schemas.graph_state import AgentState
from app.graph.nodes.graph_nodes import intent_router_node,general_conv_node,field_check_node,hotel_search_node,book_hotel_node,web_search_node,human_verification_node,load_state_node
from app.graph.nodes.graph_helper_functions import intent_checker,retry_router,task_router

builder = StateGraph(AgentState)

builder.add_node("intent_router",intent_router_node)
builder.add_node("general_conv",general_conv_node)
builder.add_node("field_check",field_check_node)
builder.add_node("hotel_search",hotel_search_node)
builder.add_node("get_human_response",human_verification_node)
builder.add_node("follow_up",load_state_node)
builder.add_node("book_hotel",book_hotel_node)
builder.add_node("web_search",web_search_node)


builder.add_conditional_edges("intent_router",intent_checker,["web_search","general_conv", "field_check","follow_up",END])
builder.add_conditional_edges("field_check",retry_router,["hotel_search",END])
builder.add_edge("hotel_search","get_human_response")
builder.add_edge("get_human_response",END)

builder.add_conditional_edges("follow_up",task_router,["book_hotel",END])

builder.add_edge("book_hotel",END)
builder.add_edge("general_conv",END)
builder.add_edge("web_search",END)


builder.set_entry_point("intent_router")

app = builder.compile()