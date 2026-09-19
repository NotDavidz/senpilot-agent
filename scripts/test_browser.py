import re
from playwright.sync_api import sync_playwright

URL = "https://uarb.novascotia.ca/fmi/webd/UARB15"
MATTER_NUMBER = "M12205"

def debug_modal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("1. Loading page...")
        page.goto(URL, wait_until="networkidle")
        
        print("2. Activating input field...")
        page.get_by_text("eg M01234").first.click(force=True)
        
        # --- THE FIX ---
        # Wait for the actual text box to render and force focus on it before typing
        active_input = page.locator('div[contenteditable="true"]').first
        active_input.wait_for(state="visible", timeout=10000)
        active_input.click(force=True) 
        page.wait_for_timeout(500) # 0.5s buffer for FileMaker JS to register focus
        # ---------------
        
        print(f"3. Typing {MATTER_NUMBER}...")
        page.keyboard.type(MATTER_NUMBER, delay=100)
        page.keyboard.press("Enter")
        
        print("4. Opening tab...")
        page.get_by_text(re.compile(r"Other Documents", re.IGNORECASE)).first.wait_for(timeout=30000)
        page.get_by_text(re.compile(r"Other Documents", re.IGNORECASE)).first.click(force=True)
        
        print("5. Clicking first GO GET IT...")
        btn = page.get_by_text(re.compile(r"GO\s+GET\s+IT", re.IGNORECASE)).first
        btn.wait_for(state="visible", timeout=15000)
        btn.click(force=True)
        
        print("6. Waiting for modal to open...")
        page.wait_for_timeout(3000)
        
        print("\n" + "="*50)
        print("DEBUG: FILE LINK HTML")
        print("="*50)
        try:
            file_els = page.locator("text=/\\.(pdf|doc|xls|csv|txt)/i")
            for i in range(file_els.count()):
                html = file_els.nth(i).evaluate("el => el.outerHTML")
                print(f"FILE ELEMENT {i}:\n{html}\n")
        except Exception as e:
            print("Error:", e)

        print("\n" + "="*50)
        print("DEBUG: CLOSE BUTTON HTML")
        print("="*50)
        try:
            close_els = page.locator("text=/^Close$/i")
            for i in range(close_els.count()):
                html = close_els.nth(i).evaluate("el => el.outerHTML")
                print(f"CLOSE ELEMENT {i}:\n{html}\n")
        except Exception as e:
            print("Error:", e)

        print("="*50)
        input("Press ENTER to close...")
        context.close()
        browser.close()

if __name__ == "__main__":
    debug_modal()