import os
import instructor
import google.generativeai as genai
from pydantic import BaseModel, Field


def get_ai_suggestion(prompt: str, model: str, OutputModel):

    local = False

    if not local:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        client = instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name=model,
            ),
            mode=instructor.Mode.GEMINI_JSON,
        )

        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt + " "}],
            response_model=OutputModel,
            max_retries=5,
        )
    else:
        resp = OutputModel(summary="This is a test summary")

    return resp
