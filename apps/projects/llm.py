from apps.projects import models
import json

import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
_generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


def description_for_rec(rec: models.Record) -> str:
    """Use Gemini to make a 1-sentence description for rec"""
    typedesc = {
        "ai_chat": "conversation with an AI chatbot",
        "note": "interview file note",
        "manual_transcript": "conversation transcript",
    }
    prompt = (
        f"Please summarize the most salient aspect of the following {typedesc} "
        "in a single phrase or short sentence of 7-10 words, from the point of view "
        "of the subject. Examples: 'fearful of the future', 'confused about the way forward', "
        "'excited to get started', 'knowledgeable about peanut farms' etc.\n\n"
    ) + rec.get_markdown()
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=_generation_config,
    )
    chat_session = model.start_chat()
    response = chat_session.send_message(prompt)
    return response.text


def description_for_case(case: models.Case) -> str:
    """Use Gemini to make a 1-sentence description for case"""
    prompt = (
        "Please summarize the most salient aspect of the following field notes "
        "in a single phrase or short sentence of 7-10 words, from the point of view "
        "of the subject. Examples: 'fearful of the future', 'confused about the way forward', "
        "'excited to get started', etc.\n\n"
    ) + case.get_markdown()
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=_generation_config,
    )
    chat_session = model.start_chat()
    response = chat_session.send_message(prompt)
    return response.text


def get_themes(project, num_themes=30):
    data = "\n\n".join(case.get_markdown() for case in project.current_cases())
    prompt = (
        f"""
You need to analyze an dataset of interviews.
Please identify the top {num_themes} key themes from the interview and organize the results in a structured table format.
Focus on what the interview subjects (users) say, not the interviewer (model).
The table should includes these items:

  - 'ThemeName': Represents the main idea or topic identified from the interview.
  - 'Description': Provides a brief explanation or summary of the theme.
  - 'Quotes': Contains 5-7 direct quotations from participants that support the identified theme.
  - 'Participants': Indicates the number of participants who mentioned or alluded to the theme.

Use this Json schema. The result should be a list of dicts.

Theme: {{"ThemeName": str, "Description": str, "Quotes": list[str], "Participants": int}}
Return: list[Theme]
"""
        + data
    )
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )
    chat_session = model.start_chat()
    response = chat_session.send_message(prompt)
    results = json.loads(response.text)
    # results should be a list, but might be a dict because gemini grr
    # hack hack hack
    if isinstance(results, dict):
        if len(results) == 1:
            key0 = next(iter(results))
            results = results[key0]
    if isinstance(results, list) and len(results) > 0 and "Participants" in results[0]:
        results = sorted(results, key=lambda x: -x["Participants"])
    return results
