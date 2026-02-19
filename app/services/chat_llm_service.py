from groq import Groq

from app.config import settings


def get_chat_client() -> Groq:
	if not settings.groq_api_key_chat:
		raise ValueError("GROQ_API_KEY_CHAT is not configured")
	return Groq(api_key=settings.groq_api_key_chat)
