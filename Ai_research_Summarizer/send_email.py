import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

def send_pdf(to_email, subject="Your Scientific Summary Digest", file_path="summary.pdf"):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("SENDER_EMAIL")
    msg['To'] = to_email
    msg.set_content("Please find attached the summary of the latest scientific research papers.")

    with open(file_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="summary.pdf")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("SENDER_EMAIL"), os.getenv("APP_PASSWORD"))
        smtp.send_message(msg)
