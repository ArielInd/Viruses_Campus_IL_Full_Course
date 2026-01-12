from playwright.sync_api import sync_playwright
import time

class Downloader:
    def __init__(self, username, password, headless=True):
        self.username = username
        self.password = password
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def start(self):
        """Initialize playwright and browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def stop(self):
        """Close browser and stop playwright."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login(self):
        """Log in to Campus IL."""
        if not self.page:
            self.start()
        
        self.page.goto("https://campus.gov.il/login/")
        
        # Wait for the login form to be visible (it redirects)
        self.page.wait_for_selector("#emailOrUsername")
        
        self.page.fill("#emailOrUsername", self.username)
        self.page.fill("#password", self.password)
        self.page.click("#sign-in")
        
        # Optional: wait for navigation to complete
        self.page.wait_for_load_state("networkidle")
