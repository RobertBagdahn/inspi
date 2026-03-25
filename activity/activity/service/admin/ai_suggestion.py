from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="inspi-441320", location="europe-west1")


def get_ai_suggestion(prompt: str, model: str, OutputModel):

    local = False

    if not local:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=OutputModel,
            ),
        )

        resp = OutputModel.model_validate_json(response.text)
    else:
        resp = OutputModel(summary="This is a test summary")

    return resp
