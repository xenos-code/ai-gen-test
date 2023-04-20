# app_functions.py

import openai
import pandas as pd
import time
import re
import os
import zipfile
from prompts import prompts
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from html.parser import HTMLParser

def create_url_path(keyword):
    url_path = keyword.lower()
    url_path = re.sub(r"[^a-z0-9\s]+", "", url_path)  # Remove non-alphanumeric and non-space characters
    url_path = url_path.replace(" ", "-")  # Replace spaces with hyphens

    # Remove trailing hyphen if present
    if url_path[-1] == "-":
        url_path = url_path[:-1]

    return f"/{url_path}"

def create_full_path(domain, url_path):
    return f"https://{domain}{url_path}"

def generate_content(api_key, prompt, sections):
    openai.api_key = api_key

    system_message = prompts["system_message"]
    
    print(f"Generated prompt:\n{prompt}\n")

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    completion = openai.ChatCompletion.create(
        model= "gpt-3.5-turbo",
        max_tokens = 3200,
        # temperature = temperature, 
        # presence_penalty = presence_penalty,
        # frequency_penalty = frequency_penalty,
        messages = messages
    )

    response = completion.choices[0].message.content.strip()
    # print(f"Generated response:\n{response}\n")
    return response

def generate_related_links(df, current_topic):
    current_category = df.loc[df['topic'] == current_topic, 'category'].values[0]
    current_full_path = df.loc[df['topic'] == current_topic, 'full path'].values[0]
    related_links = df[df['category'] == current_category][['topic', 'full path']]
    
    # Filter out the self-link by comparing the full paths
    related_links = related_links[related_links['full path'] != current_full_path]

    return related_links.to_dict('records')

def generate_article(api_key, model, max_tokens, temperature, presence_penalty, frequency_penalty, prompt, sections, definition_only=False):
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

    article = generate_content(api_key, model, max_tokens, temperature, presence_penalty, frequency_penalty, prompt, sections)
    return article

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.current_tag = None
        self.parent_tag = None
        self.current_href = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag in ["ul", "ol"]:
            self.parent_tag = tag
        if tag == "a":
            attrs_dict = dict(attrs)
            self.current_href = attrs_dict.get("href")

    def handle_endtag(self, tag):
        if tag == self.parent_tag:
            self.parent_tag = None
        self.current_tag = None

    def handle_data(self, data):
        if self.current_tag in ["h2", "h3", "h4", "p"]:
            self.text.append({"type": self.current_tag, "content": data.strip()})
        elif self.current_tag == "li":
            self.text.append({"type": self.current_tag, "content": data.strip(), "parent": self.parent_tag})
        elif self.current_tag == "a":
            self.text.append({"type": self.current_tag, "content": data.strip(), "href": self.current_href})


def save_article_as_docx(filename, title, definition, content):
    # Parse the HTML content
    parser = MyHTMLParser()
    parser.feed(content)
    parsed_content = parser.text

    # Create a new DOCX document
    doc = Document()
    doc.add_heading(title, level=1)
    doc.add_paragraph(definition)

    # Add parsed content to the DOCX document
    for item in parsed_content:
        if item["type"] in ["h2", "h3", "h4"]:
            level = int(item["type"][1])
            doc.add_heading(item["content"], level=level)
        elif item["type"] == "p":
            doc.add_paragraph(item["content"])
        elif item["type"] == "li":
            style = "ListBullet" if item["parent"] == "ul" else "ListNumber"
            doc.add_paragraph(item["content"], style=style)
        elif item["type"] == "a":
            p = doc.add_paragraph()
            r = p.add_run(item["content"])
            r.hyperlink = item["href"]

    # Save the document to a file
    doc.save(filename)
