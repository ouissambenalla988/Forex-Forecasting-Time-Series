# chatbot_module.py
import openai
import os
import requests
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def ask_chatbot(question):
    """Utilise GPT pour répondre à une question sur le Forex."""
    context = (
        "Tu es un expert du marché Forex. Tu donnes des réponses précises, pédagogiques "
        "et à jour, basées sur les actualités économiques et les tendances du marché."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur : {e}"

def get_forex_news():
    """Récupère les dernières news Forex via NewsAPI."""
    url = f"https://newsapi.org/v2/everything?q=forex&language=fr&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        return [(a["title"], a["url"]) for a in data.get("articles", [])[:5]]
    except Exception as e:
        return [("Erreur de récupération des news", str(e))]
