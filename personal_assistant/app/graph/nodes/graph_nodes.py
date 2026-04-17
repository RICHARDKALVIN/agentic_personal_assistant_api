from app.schemas.graph_state import AgentState

from app.llm.provider import intent_llm_structured

from datetime import datetime, timezone
from app.utils.tools import get_restaurants
import json
from app.llm.provider import rest_llm
from app.web_search.search import web_search



now_utc = datetime.now(timezone.utc)



    
async def field_check_node(state: AgentState):

    intent = state["intent"]
    request ="To reserve a hotel, you need to provide the following information: "
    if not intent["city"] :
        request = request+"name of the city"
    if not intent["date_and_time"]:
        request = request+"date and time of the reservation"
    
    if request != "To reserve a hotel, you need to provide the following information: ":
        return {"final_reply" : request}
    return {"message_to_next" : "continue"}


async def general_conv_node(state: AgentState):

    intent = state["intent"]
    if intent["is_general"]:
        return {"final_reply" : intent["general_reply"]}
    else:
        return {"final_reply" : "something went wrong please try again later"}




async def intent_router_node(state: AgentState):

    prompt = f""" Role
You are an expert Intent Classification agent for a hospitality assistant. Your task is to analyze user queries and extract structured data based on the provided schema.

agent memory:
 {state["conv_history"]}
### Task Rules
1. **General Queries**: If the user is asking a general question (e.g., "How are you?", "Tell me a joke"), set `is_general` to true  and `general_reply` to give appropriate response.. All other fields should remain at their default values (null or empty).
3. **Follow Up Queries**:  set `is_follow_up` to true when user asked to book a particular restaurants or hotel and `is_general` to false.
4. **Reservation Queries**: If the user expresses intent to book or inquire about a specific hotel stay, set `is_reservation` to true and `is_general` to false.
5. **Web Search Queries**: If the user asks for information about a specific topic, set `need_web_search` to true and `is_general` to false.
6. **Data Extraction**:
   - **city**: Extract the city name (e.g., "Mumbai"). 
   - **locality**: Extract specific areas if mentioned (e.g., "Andheri West").
   - **hotel_name**: Extract the specific hotel name if provided.
   - **date_and_time**: Extract the intended check-in or reservation time.


### Date Handling (CRITICAL)
- Today's date is {now_utc}.
- Always provide the `date_and_time` in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
- If the user says "tomorrow," calculate it relative to today (April 11, 2026).
- If only a date is provided, default the time to 12:00:00 (noon).

### Output Requirement
Return only valid JSON that strictly follows the schema. Do not include conversational filler."""

    response = await intent_llm_structured.ainvoke(prompt)

    response_dict = response.model_dump()


    return {"intent" : response_dict}



async def list_hotel_node(state: AgentState):

    intent = state["intent"]
    city = intent["city"]
    locality = intent["locality"]
    hotel_name = intent["hotel_name"]
    date_and_time = intent["date_and_time"]

    response_json = get_restaurants(city, locality, hotel_name)

    json_string = json.dumps(response_json)

    prompt= f"""You are an part of expert hotel booking assistant. Your task is to sent response to the user based on the hotel availability.
     
     user query : {state["query"]}

    ### user Query 
    - City: {city}
    - Locality: {locality}
    - Hotel Name: {hotel_name}
    - Date and Time: {date_and_time}
    
    ### available hotels
    {json_string}
     ask the user to choose the hotel from the list .
     tell him/her ask for hotel name if you are unable to find the hotel in the list.
    """

    response = await rest_llm.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return {"final_reply" : response.choices[0].message.content}

async def book_hotel_node(state: AgentState):

    intent = state["intent"]
    city = intent["city"]
    locality = intent["locality"]
    hotel_name = intent["hotel_name"]
    date_and_time = intent["date_and_time"]

    prompt= f"""
    You are an part of expert hotel booking assistant. Your task is to sent final reply that the user has booked the hotel.
    hotel : {hotel_name} date and time : {date_and_time} city :{city}  
    -> be natural and be welcoming
    -> ask do you want any other help ?

    """

    response = await rest_llm.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )


    return {"final_reply" :  response.choices[0].message.content }


async def web_search_node(state: AgentState):

    response = await web_search(state["query"])

    return {"final_reply" : response}

