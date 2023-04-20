# app_functions.py

import re
import pandas as pd
import openai
from prompts import prompts

# [create_url_path and create_full_path functions remain the same]

def generate_content(api_key, prompt, sections):
    openai.api_key = api_key

    system_message = prompts["system_message"]
    
    print(f"Generated prompt:\n{prompt}\n")

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=3200,
        messages=messages
    )

    response = completion.choices[0].message.content.strip()
    print(f"Generated response:\n{response}\n")
    return response

# [generate_related_links function remains the same]

def generate_article(topic, sections, related_links, definition_only=False):
    if definition_only:
        prompt = prompts["definition_prompt"].format(topic)
    else:
        if related_links:
            related_links_prompt = prompts["related_links_prompt"].format(
                ", ".join([f"{rl['topic']} ({rl['full path']})" for rl in related_links])
            )
        else:
            related_links_prompt = ""

        prompt = prompts["article_prompt"].format(
            topic, "\n".join(str(sec) for sec in sections), related_links_prompt
        )

    article = generate_content(api_key, prompt, sections)
    return article

# [Other functions remain the same]
