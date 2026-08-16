import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# client = Groq(api_key=GROQ_API_KEY)

def get_chatbot_response(user_message):
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI Career and Resume Assistant. "
                            "Your strictly main task is to provide guidance on careers, resumes, interview preparation, and professional development. "
                            "If the user asks a question that is NOT related to careers, jobs, education, or professional skill development, "
                            "politely decline to answer and ask them to ask a career-related question."
                },
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
        )
        ai_reply = response.choices[0].message.content
        return ai_reply 

    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Sorry, I am facing a temporary issue. Please try again."