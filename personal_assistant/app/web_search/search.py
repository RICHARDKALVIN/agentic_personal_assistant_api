import aiohttp
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from loguru import logger

load_dotenv()

OPENROUTER_URL = os.getenv("OPEN_ROUTER_URL")
SERPER_URL = os.getenv("SERPER_URL")


async def web_search(query):
    results = await search(query)

    links = [r['link'] for r in results.get('organic', [])[:2]]

    context_parts = []
    for link in links:
        context_parts.append(await scrape(link))

    context = "\n\n".join(context_parts)

    logger.info(f"context from web_scraping: {context}")

    prompt = f"""
    you are a Part of personal assistant agent. your task is to answer from websearch results.
    your answer should be in this format:
    "
    1. content
    2. content
    " 
    Answer the question based on context:
    {context}
    Question: {query}

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
            return result["choices"][0]["message"]["content"]


async def search(query):
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }

    payload = {"q": query}

    async with aiohttp.ClientSession() as session:
        async with session.post(SERPER_URL, headers=headers, json=payload) as resp:
            return await resp.json()


async def scrape(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                return soup.get_text()[:3000]
    except Exception as e:
        return f"Error scraping {url}: {e}"