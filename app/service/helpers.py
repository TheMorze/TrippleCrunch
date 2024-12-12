import asyncio

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