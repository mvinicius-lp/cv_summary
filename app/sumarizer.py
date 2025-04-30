# app/routes/summarizer.py

import os
from dotenv import load_dotenv
from huggingface_hub import login
from transformers import pipeline

load_dotenv()

# Login no HuggingFace
login(token=os.getenv("HF_API_KEY"))

# Carregamento do pipeline
summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text: str) -> str:
    summary = summarizer_pipeline(text, max_length=1500, min_length=100, do_sample=False)
    return summary[0]['summary_text']
