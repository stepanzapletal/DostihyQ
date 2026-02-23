# pip install ollama
# využíváme model gemma3n:e4b protože je jednoduchý, rychlý a malý
from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(
    model="gemma3n:e4b",
    messages=[
        {
            "role": "user",
            "content": 'Simple request, nothing to think about. Just say "Hello"',
        }
    ],
    think=False,  # NEžádat o "think" režim, protože gemma ho nemá
)
print(response.message.content)