import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# client = Groq(api_key=GROQ_API_KEY)

def get_chatbot_response(user_message):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI Career and Resume Assistant. Provide short, clear, and professional answers."
                },
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
        )
        ai_reply = response.choices[0].message.content
        return ai_reply.replace("\n", "<br>")

    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Sorry, I am facing a temporary issue. Please try again."