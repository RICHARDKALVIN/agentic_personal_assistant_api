from app.schemas.chat_schemas import  ChatRequest, ChatResponse  
from app.memory.RedisSTM import RedisSTM
from app.utils.prompts import build_prompt
from app.core.redis import redis_client
from langchain_core.output_parsers import StrOutputParser
from app.utils.query_util import get_re_written_query
from loguru import logger
from app.graph.graph import app
from app.schemas.graph_state import AgentState
from langfuse.langchain import CallbackHandler


   

async def chat(chat_request : ChatRequest,handler : CallbackHandler):

    config = {
        "callbacks": [handler],
        "metadata": {
            "langfuse_user_id": chat_request.user_id,
            "langfuse_session_id": chat_request.session_id       
        }
    }

    redisSTM = RedisSTM(user_id=chat_request.user_id)

    count_key = f"count:messages:{chat_request.user_id}"
    

    stm,re_messgaes = await redisSTM.get_messages()

    summary = await redisSTM.get_summary()

    re_written_query = await  get_re_written_query(chat_request.message,re_messgaes )

    prompt = build_prompt(summary, stm, "none", re_written_query)

    logger.info(f"agent memeory: {prompt}")


    ans = await app.ainvoke(AgentState(query=re_written_query,final_reply="",intent={},message_to_next="",conv_history=prompt),config=config)
  

    logger.info(f"agent response: { ans["final_reply"]}")
    await redisSTM.add_message("user",  re_written_query)
    await redisSTM.add_message("assistant", ans["final_reply"])

    new_count = await redis_client.incr(count_key)
    
    if new_count % 3 == 0:
        await redisSTM.summarize_conversation()

    return ChatResponse(response=ans["final_reply"])




