from openai import OpenAI
from .utils.print_in_color import print_in_color

default_system_prompt = "You are an useful assistant. Your task is just talk with the user and help him solve his task. You must always answer in the same language as the user message."

def create_completion_ollama(prompt, system_prompt=default_system_prompt, stream=False):
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="llama3")
    response = client.chat.completions.create(
        model="llama3",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=3000,
        stream=stream,
    )
    if not stream:
        return response.choices[0].message.content

    _entire_response = ""

    for chunk in response:
        print_in_color(chunk.choices[0].delta.content, "yellow")
        _entire_response += chunk.choices[0].delta.content
    return _entire_response
