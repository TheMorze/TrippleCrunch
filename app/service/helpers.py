import asyncio
import os
from openai import AsyncOpenAI
from g4f.client import Client, AsyncClient

from app.lexicon.bot_lexicon import AI_LEXICON


async def get_gpt_response(prompt):
    client = AsyncClient()

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


async def get_llama_response(prompt):
    client = AsyncOpenAI(api_key=os.environ.get("LLAMA_API_KEY"), base_url=os.environ.get("LLAMA_BASE_URL"))
    response = await client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct-Lite",
        messages=[{"role": "user", "content": prompt}],
        # Add any other necessary parameters
    )

    return response.choices[0].message.content


async def get_scenary_response(prompt):
    client = AsyncClient()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": AI_LEXICON['PREDEFINED_PROMPT'] + prompt}],
    )

    return response.choices[0].message.content

