from langfuse import Langfuse, get_client

import os
from dotenv import load_dotenv
load_dotenv()


Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    base_url=os.getenv("LANGFUSE_BASE_URL"),

)

langfuse = get_client()