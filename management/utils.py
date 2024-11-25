from transformers import pipeline

# Load the summarizer once (global for efficiency)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(content):
    """
    Summarize text using Hugging Face.
    """
    summary = summarizer(content, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']
