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
