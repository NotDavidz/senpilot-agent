import re


UARB_URL = (
    "https://uarb.novascotia.ca/fmi/webd/UARB15"
)

MATTER_PLACEHOLDER_TEXT = "eg M01234"

MATTER_PLACEHOLDER = "div.placeholder"

MATTER_CONTAINER = (
    "xpath=ancestor::div[contains(@class, 'inner_border')]"
)

TEXT_DIV = "div.text"

SEARCH_BUTTON_NAME = "Search"

GO_GET_IT_RE = re.compile(
    r"^\s*GO\s+GET\s+IT\s*$",
    re.IGNORECASE,
)

CLOSE_BUTTON_RE = re.compile(
    r"^\s*Close\s*$",
    re.IGNORECASE,
)

DOWNLOAD_MODAL_TEXT = "Download Files"