
def build_prompt(summary, stm_messages, ltm_memories, user_query):

   
    
    prompt = f"""

    Previous conversation summary:
    {summary}

    Long-term memory:
    {ltm_memories}

    Recent conversation:
    {stm_messages}

    User question:
    {user_query}


    """

    return prompt