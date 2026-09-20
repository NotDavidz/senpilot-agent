## Build

*   **Language:** Python 3
*   **Web Automation:** Playwright (Headless Chromium)
*   **AI & Parsing:** OpenAI API (`gpt-4o-mini`) with Pydantic Structured Outputs
*   **Communication:** email ingestion & delivery

---

## What I Would Have Done Differently (With More Time)

*   **Parallel Processing** The current implementation processes emails synchronously in a `while` loop. If many people email the agent at once, they will experience long wait times. Implementing a message queue would allow multiple Playwright workers to process scraping jobs in parallel.

*   **Cloud Storage:** In a production environment, I would stream the Playwright downloads directly into a cloud storage bucket (like AWS S3 or Google Cloud Storage) and email the user a secure download link. This would eliminate the risk of the ZIP file being marked as spam and bypass standard Gmail attachment size limits.

*   **Webhooks:** As mentioned in my Loom video, I would implement a webhook architecture to push incoming emails to the agent instantly, replacing the need to continuously poll the inbox every minute.

*   **Error Handling:** I would improve the fallback responses so the agent gracefully notifies the user if they input unparsable, non-existent, or incorrectly formatted case numbers and document types.

---

## What I Learned

*   **LLMs as a Translation Layer:** Using AI models is an effective way to add a transition layer between unpredictable human input and strict programmatic objects. It is superior to relying on rigid Regex patterns in natural language scenarios.

*   **Scraping Strategies** I learned that not all website scrolls are built the same. Recognizing that some sites actively delete and recycle DOM elements/objects to save memory rather than just lazy-loading new ones changed my approach. It shows how essential it is to adapt scraping strategies to the specific rendering needs of modern applications.