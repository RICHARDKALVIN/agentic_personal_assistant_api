from langgraph.graph import END, StateGraph
from app.schemas.graph_state import AgentState
from app.graph.nodes.graph_nodes import intent_router_node,general_conv_node,field_check_node,list_hotel_node,book_hotel_node
from app.graph.nodes.graph_helper_functions import intent_checker,feild_checker

builder = StateGraph(AgentState)

builder.add_node("intent_router",intent_router_node)
builder.add_node("general_conv",general_conv_node)
builder.add_node("field_check",field_check_node)
builder.add_node("list_hotel",list_hotel_node)
builder.follow_up("follow_up",book_hotel_node)


builder.add_conditional_edges("intent_router",intent_checker,["general_conv_node", "field_check","follow_up",END])
builder.add_conditional_edges("field_check",feild_checker,["list_hotel",END])
builder.add_edge("list_hotel",END)
builder.add_edge("general_conv",END)
builder.add_edge("follow_up",END)


builder.set_entry_point("router")

app = builder.compile()