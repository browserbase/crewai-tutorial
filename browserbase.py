import os
from crewai_tools import tool
from playwright.sync_api import sync_playwright
from html2text import html2text
from time import sleep


@tool("Browserbase tool")
def browserbase(url: str):
    """
    Loads a URL using a headless webbrowser

    :param url: The URL to load
    :return: The text content of the page
    """
    with sync_playwright() as playwright:
        print(f"Loading {url} using Browserbase")
        browser = None
        page = None
        try:
            browser = playwright.chromium.connect_over_cdp(
                "wss://connect.browserbase.com?enableProxy=false&apiKey="
                + os.environ["BROWSERBASE_API_KEY"]
            )
            context = browser.contexts[0]
            page = context.pages[0]
        except Exception as e:
            print("No context found, using local browser")
            print(e)
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()

        print("Page found, going to URL", url)
        page.goto(url)
        print("Page loaded")

        # Wait for the flight search to finish
        sleep(20)

        content = html2text(page.content())
        browser.close()
        return content
