from fetch_papers import fetch_latest_papers
from summarize import summarize_text
from generate_pdf import generate_pdf
from send_email import send_pdf

def run():
    print("=== Scientific Paper Summarizer (Python Only) ===\n")
    user_topic = input("Enter research topic (e.g., AI, Physics, Biology): ")
    user_email = input("Enter your email address: ")

    print("\n🔍 Fetching latest research papers...")
    papers = fetch_latest_papers(query=user_topic)

    print("🧠 Summarizing papers...")
    summarized = []
    for i, paper in enumerate(papers, 1):
        print(f"  - Summarizing Paper {i}: {paper['title'][:50]}...")
        summary = summarize_text(paper['summary'])
        summarized.append({
            "title": paper['title'],
            "abstract": paper['summary'],
            "summary": summary,
            "link": paper['link']
        })

    print("📄 Generating PDF...")
    generate_pdf(summarized)

    print("📧 Sending email to", user_email)
    send_pdf(user_email)

    print("\n✅ Done! Check your inbox for the PDF summary.")

if __name__ == "__main__":
    run()
