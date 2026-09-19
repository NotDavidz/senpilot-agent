import sys
import time
import tempfile
import zipfile
from pathlib import Path
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

load_dotenv()

from scraper.models import ScrapeResult
from scraper.uarb import scrape_matter
from ai_parser import extract_intent, extract_metadata # <--- Import new function
from email_client import get_unread_emails, send_response_email
import re

def create_zip_archive(files: list, zip_name: str, dest_dir: Path) -> Path:
    zip_path = dest_dir / f"{zip_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in files:
            zipf.write(f.saved_path, f.suggested_filename)
    return zip_path

# --- UPDATED: Dynamic Email Formatting ---
def format_email_body(result: ScrapeResult, metadata) -> str:
    counts = result.matter.counts
    doc_type = result.requested_document_type.value
    
    return (
        f"Hi User,\n\n"
        f"{result.matter.matter_number} is about the {metadata.title_description}. "
        f"It relates to {metadata.type_category}. The matter had an initial filing "
        f"on {metadata.initial_filing_date} and a final filing on {metadata.final_filing_date}.\n\n"
        f"I found {counts.exhibits} Exhibits, {counts.key_documents} Key Documents, "
        f"{counts.other_documents} Other Documents, {counts.transcripts} Transcripts, "
        f"and {counts.recordings} Recordings.\n\n"
        f"I downloaded {len(result.downloaded)} out of the {counts.get(result.requested_document_type)} "
        f"{doc_type} and am attaching them as a ZIP here."
    )

def main():
    print("Agent started. Polling inbox every 60 seconds...")
    
    while True:
        try:
            emails = get_unread_emails()
            if not emails:
                pass
            
            for incoming in emails:
                print(f"Processing request from {incoming.sender}...")
                
                intent = extract_intent(incoming.body)
                
                if not intent.matter_number or not intent.matter_number.strip():
                    print(" -> No Matter Number found. Skipping irrelevant email.")
                    continue
                
                print(f" -> Extracted Matter: {intent.matter_number} | Tab: {intent.document_type.value}")

                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    result = scrape_matter(intent.matter_number, intent.document_type, temp_path)
                    
                    if not result.downloaded:
                        print(" -> No files downloaded. Skipping.")
                        continue

                    # --- NEW: Extract dynamic metadata ---
                    print(" -> Extracting matter metadata via AI...")
                    metadata = extract_metadata(result.raw_page_text)

                    zip_path = create_zip_archive(result.downloaded, intent.matter_number, temp_path)

                    email_text = format_email_body(result, metadata)
                    
                    clean_email = re.search(r'[\w\.-]+@[\w\.-]+', incoming.sender).group(0) if re.search(r'[\w\.-]+@[\w\.-]+', incoming.sender) else incoming.sender
                    
                    send_response_email(
                        to_email=clean_email,
                        subject=f"Re: {incoming.subject} - {intent.matter_number} Documents",
                        body=email_text,
                        zip_path=zip_path
                    )
                    print(f"✅ Success! Sent files to {clean_email}")
                    
        except Exception as e:
            print(f"Error in polling loop: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    main()