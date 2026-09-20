import os
from pydantic import BaseModel
from openai import OpenAI
from scraper.models import DocumentType

client = OpenAI()

class EmailIntent(BaseModel):
    matter_number: str
    document_type: DocumentType

class ScrapedMetadata(BaseModel):
    title_description: str
    type_category: str
    initial_filing_date: str
    final_filing_date: str

def extract_intent(email_body: str) -> EmailIntent:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract the matter number (e.g., M12345) and requested document type from the user email."},
            {"role": "user", "content": email_body}
        ],
        response_format=EmailIntent,
    )
    return completion.choices[0].message.parsed

def extract_metadata(page_text: str) -> ScrapedMetadata:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract the project description/title, category/type, initial filing date, and final filing date from this raw website text. If a date is missing, return 'Unknown'."},
            {"role": "user", "content": page_text[:4000]} # Limit to 4000 characters to save tokens
        ],
        response_format=ScrapedMetadata,
    )
    return completion.choices[0].message.parsed