from google import genai
from google.genai import types
from products.models import Disease

# pip install google-genai


def generate_prompt(image_path):
    kasalliklar=list(Disease.objects.values_list("name",flat=True))
    client = genai.Client(
        api_key="AIzaSyBN2VdiUn4W2rJICGCzGeJy83pMwcXjdTE",
    )

    files = [
        # Please ensure that the file is available in local system working direrctory or change the file path.
        client.files.upload(file=image_path),
    ]

    model = "gemini-2.0-flash-lite"
    # model = "gemini-2.0-flash"
    # gemini-2.0-flash-preview-image-generation
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

