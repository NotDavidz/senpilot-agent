import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from . import models, selectors

def scrape_matter(matter_number: str, doc_type: models.DocumentType, download_dir: Path) -> models.ScrapeResult:
    downloaded_files = []

    with sync_playwright() as p:
        # headless=True for cloud/server deployment
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print(f"[DEBUG] Loading UARB portal for Matter: {matter_number}")
        page.goto(selectors.UARB_URL, wait_until="networkidle")
        
        placeholder = page.get_by_text(selectors.MATTER_PLACEHOLDER_TEXT).first
        placeholder.wait_for(state="visible", timeout=30000)
        placeholder.click(force=True)
        
        active_input = page.locator('div[contenteditable="true"]').first
        active_input.wait_for(state="visible", timeout=10000)
        active_input.click(force=True) 
        page.wait_for_timeout(500) 
        
        print(f"[DEBUG] Typing matter number: {matter_number}")
        page.keyboard.type(matter_number, delay=100)
        page.keyboard.press("Enter")

        print(f"[DEBUG] Waiting for tab: {doc_type.value}")
        target_tab = page.get_by_text(re.compile(doc_type.value, re.IGNORECASE)).first
        target_tab.wait_for(state="visible", timeout=30000)
        page.wait_for_timeout(2000) 

        page_text = page.locator("body").inner_text()
        
        def extract_count(name: str) -> int:
            match = re.search(fr"{name}\s*-\s*(\d+)", page_text, re.IGNORECASE)
            return int(match.group(1)) if match else 0

        counts = models.MatterCounts(
            exhibits=extract_count("Exhibits"),
            key_documents=extract_count("Key Documents"),
            other_documents=extract_count("Other Documents"),
            transcripts=extract_count("Transcripts"),
            recordings=extract_count("Recordings")
        )
        print(f"[DEBUG] Extracted Counts: {counts}")

        overview = models.MatterOverview(matter_number=matter_number, counts=counts)
        target_tab.click(force=True)

        print("[DEBUG] Waiting for first 'GO GET IT' button...")
        page.get_by_text(selectors.GO_GET_IT_RE).first.wait_for(state="visible", timeout=15000)
        
        actual_total = counts.get(doc_type)
        limit = min(actual_total, 10)
        print(f"[DEBUG] Target download limit set to: {limit} files")
        
        processed_filenames = set()
        attempts = 0
        max_attempts = 50 
        
        while len(downloaded_files) < limit and attempts < max_attempts:
            attempts += 1
            buttons = page.get_by_text(selectors.GO_GET_IT_RE)
            visible_count = buttons.count()
            print(f"[DEBUG] Loop Attempt {attempts}: Found {visible_count} visible buttons")
            
            for i in range(visible_count):
                if len(downloaded_files) >= limit:
                    print("[DEBUG] Reached download limit. Breaking out of loop.")
                    break
                    
                print(f"[DEBUG] Processing visible button {i+1} of {visible_count}...")
                btn = buttons.nth(i)
                btn.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                
                btn.dispatch_event("mousedown")
                btn.dispatch_event("mouseup")
                btn.dispatch_event("click")
                
                modal = page.get_by_text(selectors.DOWNLOAD_MODAL_TEXT).first
                try:
                    modal.wait_for(state="visible", timeout=8000)
                    print("[DEBUG] Modal opened successfully.")
                except Exception:
                    print("[DEBUG] Modal timeout. Triggering fallback click...")
                    btn.click(force=True)
                    modal.wait_for(state="visible", timeout=8000)
                    
                page.wait_for_timeout(1000)
                
                file_link = page.locator("span.v-button-caption").filter(
                    has_text=re.compile(r"\.(pdf|docx?|xlsx?|csv|txt)", re.IGNORECASE)
                ).first
                
                file_link.wait_for(state="visible", timeout=5000)
                filename = file_link.inner_text().strip()
                
                if filename in processed_filenames:
                    print(f"[DEBUG] Skipping duplicate file: {filename}")
                    close_btn = page.locator("span.v-button-caption").filter(has_text="Close").first
                    close_btn.dispatch_event("click")
                    modal.wait_for(state="hidden", timeout=5000)
                    page.wait_for_timeout(500)
                    continue
                    
                print(f"[DEBUG] Downloading new file: {filename}")
                processed_filenames.add(filename)
                
                with page.expect_download(timeout=60000) as download_info:
                    file_link.dispatch_event("click")
                    
                dl = download_info.value
                file_path = download_dir / dl.suggested_filename
                dl.save_as(str(file_path))
                
                downloaded_files.append(
                    models.DownloadedDocument(saved_path=file_path, suggested_filename=dl.suggested_filename)
                )
                print(f"[DEBUG] Saved: {dl.suggested_filename} ({len(downloaded_files)}/{limit})")
                
                close_btn = page.locator("span.v-button-caption").filter(has_text="Close").first
                close_btn.dispatch_event("click")
                modal.wait_for(state="hidden", timeout=10000)
                page.wait_for_timeout(1000)
                
            if len(downloaded_files) < limit:
                print("[DEBUG] Exhausted visible buttons. Scrolling down to recycle list...")
                buttons.last.hover()
                page.mouse.wheel(0, 1500) 
                page.wait_for_timeout(2500) 

        browser.close()
        print(f"[DEBUG] Scraping complete. Total downloaded: {len(downloaded_files)}")
        return models.ScrapeResult(
            matter=overview,
            requested_document_type=doc_type,
            downloaded=downloaded_files,
            raw_page_text=page_text
        )