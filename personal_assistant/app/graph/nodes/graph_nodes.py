from app.schemas.graph_state import AgentState
import httpx
from app.llm.provider import intent_llm_structured
from loguru import logger
from datetime import datetime, timezone
from app.utils.tools import get_restaurants
import json
from app.web_search.search import web_search
from app.core.redis import redis_client 
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = os.getenv("OPEN_ROUTER_URL")



now_utc = datetime.now(timezone.utc)



    
async def field_check_node(state: AgentState):

    intent = state["intent"]
    request ="To reserve a hotel, you need to provide the following information: "
    if not intent["city"] :
        request = request+"name of the city"
    if not intent["check_in"]:
        request = request+"date and time of the reservation"
    
    if request != "To reserve a hotel, you need to provide the following information: ":
        request= request+" you can also provide checkout date and time , budget for the hotel and the number of guests comming with you"
        return {"final_reply" : request}
    return {"action" : "book_hotel"}
    



async def general_conv_node(state: AgentState):

    intent = state["intent"]
    if intent["is_general"]:
        return {"final_reply" : intent["general_reply"]}
    else:
        return {"final_reply" : "something went wrong please try again later"}




async def intent_router_node(state: AgentState):

    prompt = f""" 
    Role : You are an expert Intent Classification agent for a personal assistant. Your task is to analyze user queries and extract structured data based on the provided schema.
    agent memory:
    {state["conv_history"]}

    ### Task Rules

    1. **General Queries**: If the user is asking a general question (e.g., "How are you?", "Tell me a joke"), set `is_general` to true  and `general_reply` to give professional appropriate response . All other fields should remain at their default values (null or empty).
    3. **Follow Up Queries**:  set `is_follow_up` to true if the user asked to book a particular hotel in the conversation.If its a normal follow up then false.
        if user selected the hotel for booking `selected_hotel` will be 
        id : hotel id
        name : hotel name
    4. **Reservation Queries**: If the user expresses intent to book or inquire about a specific hotel stay, set `is_reservation` to true and `is_general` to false.
    5. **Web Search Queries**: If the user asks for information can find from the web, set `need_web_search` to true and `is_general` to false.
    6. **Data Extraction**:
    - **city**: Extract the city name (e.g., "Mumbai"). 
    - **preferences**: User preferences about the hotel, e.g., 'romantic', 'budget-friendly'.
    - **budget**: Budget for the stay, e.g., 500.
    - **check_in**: date and time of the reservation.if date not provided then null.
    - **check_out**: date and time of leaving the hotel.if date not provided then null.
    - **guests**: Number of guests comming with, if not provided then default to 0.

    ### Date Handling (CRITICAL)
    - Today's date is {now_utc}.
    - Always provide the `date_and_time` in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
    - If the user says "tomorrow," calculate it relative to today (April 11, 2026).
    - If only a date is provided, default the time to 12:00:00 (noon).

    ### Output Requirement
    Return only valid JSON that strictly follows the schema. Do not include conversational filler."""

    response = await intent_llm_structured.ainvoke(prompt)

    response_dict = response.model_dump()

    logger.info(f"intent response: {response_dict}")

    return {"intent" : response_dict}



async def hotel_search_node(state: AgentState):

    intent = state["intent"]
    city = intent["city"] 
    budget= intent["budget"] or 1000
    check_in = intent["check_in"]
    check_out = intent["check_out"]
    guests = intent["guests"] or 0

    payload = {
        "city": city,
        "check_in": check_in,
        "check_out": check_out,
        "budget": budget,
        "guests": guests
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/api/hotels/search",
            json=payload
        )

        json_response = response.json()
        logger.info(f"hotel search response: {json_response}")

        prompt= f"""You are an part of expert hotel booking assistant. Your task tell the user about the hotel availability.
                ### available hotels
                {json_response}
                this list should be presentable to the user and be proffessional.
                ask the user to choose the hotel from the list .
                """

        headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
        }

        data = {
            "model": "openrouter/free",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(OPENROUTER_URL, headers=headers, json=data) as resp:
                result = await resp.json()
                return {"final_reply" : result["choices"][0]["message"]["content"]}

        
    

async def book_hotel_node(state: AgentState):

    intent = state["intent"]
    hotel = intent["selected_hotel"]
    id = hotel["id"]
    name = hotel["name"]
    

    payload = {
        "id": id,
        "name": name
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8080/api/hotels/book/{id}/{name}",
            json=payload
        )

    json_response = response.json()

    logger.info(f"book hotel response: {json_response}")

    prompt= f"""
    You are an part of expert hotel booking assistant. Your task is to sent final reply that the user has booked the hotel.
    hotel : {json_response}
    -> avoid numbers and dates in the reply.
    -> be professional and be welcoming.

    """

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openrouter/free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENROUTER_URL, headers=headers, json=data) as resp:
            result = await resp.json()
            return {"final_reply" :  result["choices"][0]["message"]["content"] }
            




async def web_search_node(state: AgentState):

    response = await web_search(state["query"])

    return {"final_reply" : response}


async def human_verification_node(state: AgentState):

    state_key = f"session_id:{state['session_id']}"

    await redis_client.set(state_key,json.dumps(state))


async def load_state_node(state: AgentState):
    state_key = f"session_id:{state['session_id']}"

    data = await redis_client.get(state_key)

    if data is None:
        return {"action": None}

    user_dict = json.loads(data.decode())

    return {
        "action": user_dict.get("action")
    }

