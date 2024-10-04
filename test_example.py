import re
import time

from playwright.sync_api import Page, expect


def test_has_title(page: Page):
    page.goto("https://playwright.dev/")
    time.sleep(3)
    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Playwright"))


def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")
    time.sleep(3)
    # Click the get started link.
    page.get_by_role("link", name="Get started").click()

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()