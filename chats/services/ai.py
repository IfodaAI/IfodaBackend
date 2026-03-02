import os
import logging

from django.core.cache import cache

from google import genai
from google.genai import types
from products.models import Disease

logger = logging.getLogger(__name__)


def get_disease_names():
    """Disease nomlarini cache bilan olish (1 soat)"""
    cache_key = "disease_names_list"
    names = cache.get(cache_key)
    if names is None:
        names = list(Disease.objects.values_list("name", flat=True))
        cache.set(cache_key, names, 3600)
    return names


def generate_prompt(image_path):
    kasalliklar = get_disease_names()
    try:
        client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

        files = [
            client.files.upload(file=image_path),
        ]

        model = "gemini-2.0-flash-lite"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=files[0].uri,
                        mime_type=files[0].mime_type,
                    ),
                    types.Part.from_text(
                        text=f"Suratdagi kasallikni bizdagi ro'yxatdan topib bering: {kasalliklar}.Va faqat eng yaqini nomini qaytar.")
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )
        result=""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            result+=chunk.text
        return result
    except Exception as e:
        logger.error(f"Gemini AI xatolik: {e}")
        return None

