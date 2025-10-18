from transformers import pipeline

summarizer = pipeline("summarization", model="google/pegasus-xsum")

def summarize_text(text, max_len=512):
    if len(text) > 1000:
        text = text[:1000]
    summary = summarizer(text, max_length=max_len, min_length=40, do_sample=False)
    return summary[0]['summary_text']
