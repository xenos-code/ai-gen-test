# main.py

from io import BytesIO
import tempfile
import streamlit as st
import pandas as pd
import time
import re
import os
import zipfile
from datetime import datetime as dt
from prompts import prompts
from app import (
    create_url_path,
    create_full_path,
    generate_content,
    generate_related_links,
    generate_article,
    MyHTMLParser,
    save_article_as_docx,
    render_expanders
)
from expanders import expanders



def main():
    st.set_page_config(page_title="AI Content Factory- V - 0.1", page_icon=None, layout='centered', initial_sidebar_state='expanded')
    st.title("AI Content Factory V - 0.1")
    st.write("A powerful AI-driven content generation tool for creating high-quality articles at scale.")
    render_expanders(expanders)

    with st.sidebar:
        st.header("Settings")

        api_key = st.text_input("API Key:", value="", type="password")
        uploaded_file = st.file_uploader("Upload a CSV file:", type=["csv"])

        domain = st.text_input("URL Path:", value="")

        # Model and settings
        model = st.selectbox("Model:", ["gpt-3.5-turbo", "gpt-4"])
        temperature = st.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
        max_tokens = st.slider("Max Tokens:", min_value=1, max_value=8000, value=2048, step=1)
        presence_penalty = st.slider("Presence Penalty:", min_value=-2.0, max_value=2.0, value=0.2, step=0.1)
        frequency_penalty = st.slider("Frequency Penalty:", min_value=-2.0, max_value=2.0, value=0.2, step=0.1)

        # Add the input field for the section start column
        section_start_col = st.number_input("Section Start Column (default is 7)", min_value=1, value=7, step=1)

    if st.button("Generate Articles"):
        if not api_key or not uploaded_file:
            st.error("Please provide all required inputs (API Key, Domain Name, and CSV File).")
            return

        df = pd.read_csv(uploaded_file)
        df.columns = map(str.lower, df.columns)  # Convert all column names to lowercase
        df["url path"] = df["keyword / h1"].apply(create_url_path)
        df["full path"] = df["url path"].apply(lambda x: create_full_path(domain, x))

        topics = df["topic"].tolist()
        h1_keywords = df["keyword / h1"].tolist()
        sections = df.iloc[:, 7:].values.tolist()

        progress_text = "Generating articles. Please wait..."
        my_bar = st.progress(0)
        total_items = len(topics) * 2
        definitions = []
        articles = []
        for idx, (topic, sec) in enumerate(zip(topics, sections)):
            related_links = generate_related_links(df, topic)

            definition = generate_article(api_key, topic, sec, related_links, model, temperature, presence_penalty, frequency_penalty, max_tokens, definition_only=True)
            definitions.append(definition)
            time.sleep(7)
            my_bar.progress((((idx + 1) * 2 - 1) / total_items * 100) / 100)

            article = generate_article(api_key, topic, sec, related_links, model, temperature, presence_penalty, frequency_penalty, max_tokens, definition_only=False)
            articles.append(article)
            time.sleep(7)
            my_bar.progress((((idx + 1) * 2) / total_items * 100) / 100)

            
        # Create a temporary directory to store the generated DOCX files
        timestamp = dt.now().strftime('%Y-%m-%d_%H-%M-%S')
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, f"article_batch_{timestamp}")
            os.makedirs(output_dir)

            for idx, (topic, h1_keyword, definition, article) in enumerate(zip(topics, h1_keywords, definitions, articles)):
                docx_filename = f"{output_dir}/{topic.replace(' ', '_')}_article.docx"
                save_article_as_docx(docx_filename, h1_keyword, definition, article)

            # Save the updated DataFrame to a new CSV file
            output_file = f"{output_dir}/article_batch_{timestamp}.csv"
            df.to_csv(output_file, index=False)

            with zipfile.ZipFile(f"{temp_dir}/article_batch_{timestamp}.zip", "w") as zipf:
                for folder, _, filenames in os.walk(output_dir):
                    for filename in filenames:
                        file_path = os.path.join(folder, filename)
                        zipf.write(file_path, os.path.basename(file_path))

            st.success(f"Generated articles and definitions added to 'article_batch_{timestamp}.zip'.")

            with open(f"{temp_dir}/article_batch_{timestamp}.zip", "rb") as f:
                bytes = f.read()
                b = BytesIO(bytes)
                st.download_button("Download Generated Articles", b, f"article_batch_{timestamp}.zip", "application/zip")

if __name__ == "__main__":
    main()
