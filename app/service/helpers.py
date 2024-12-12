import asyncio
import os
from openai import AsyncOpenAI
from g4f.client import Client, AsyncClient

async def get_gpt_response(prompt):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        # Add any other necessary parameters
    )

    return response.choices[0].message.content


# from g4f.client import AsyncClient
# from g4f.Provider import OpenaiChat, Gemini

# async def get_gpt_response_2(prompt: str):
#     client = AsyncClient(
#         provider=OpenaiChat,
#         image_provider=Gemini,
#         # Add other parameters as needed
#     )

#     response = await client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {
#             "role": "user",
#             "content": prompt
#         }
#     ]
#      # Add other parameters as needed
#     )

#     return response.choices[0].message.content
async def get_llama_response(prompt):
    client = AsyncOpenAI(api_key=os.environ.get("LLAMA_API_KEY"), base_url=os.environ.get("LLAMA_BASE_URL"))
    response = await client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct-Lite",
        messages=[{"role": "user", "content": prompt}],
        # Add any other necessary parameters
    )

    return response.choices[0].message.content
