import os
import imaplib
import smtplib
import email
from email.message import EmailMessage
from pathlib import Path
from dataclasses import dataclass

@dataclass
class UnreadEmail:
    sender: str
    subject: str
    body: str

def get_unread_emails() -> list[UnreadEmail]:
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, password)
    mail.select("inbox")

    _, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    unread_list = []
    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        sender = msg.get("From")
        subject = msg.get("Subject")
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
            
        unread_list.append(UnreadEmail(sender=sender, subject=subject, body=body.strip()))

    mail.logout()
    return unread_list

def send_response_email(to_email: str, subject: str, body: str, zip_path: Path):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = to_email
    msg.set_content(body)

    with open(zip_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='zip', filename=zip_path.name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)