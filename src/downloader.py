from playwright.sync_api import sync_playwright
from src.config import config
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
        self.page.wait_for_selector("#emailOrUsername")
        self.page.fill("#emailOrUsername", self.username)
        self.page.fill("#password", self.password)
        self.page.click("#sign-in")
        self.page.wait_for_load_state("networkidle")

    def is_logged_in(self):
        """Check if user is logged in."""
        if not self.page:
            return False
        logout_elem = self.page.query_selector("text=התנתקות")
        return logout_elem is not None

    def navigate_to_course(self):
        """Navigate to the course homepage."""
        if not self.page:
            self.start()
        self.page.goto(config.COURSE_URL)
        self.page.wait_for_load_state("networkidle")

    def get_course_hierarchy(self):
        """
        Extract the course hierarchy.
        Returns a list of modules, each containing units.
        """
        # This will be refined as we find the exact selectors.
        # For now, it's a placeholder logic.
        hierarchy = []
        
        # Example logic to find modules and units
        # modules = self.page.query_selector_all(".course-module")
        # for i, module in enumerate(modules, 1):
        #     title = module.query_selector(".module-title").inner_text()
        #     units = []
        #     unit_elems = module.query_selector_all(".unit-link")
        #     for j, unit in enumerate(unit_elems, 1):
        #         units.append({
        #             "index": j,
        #             "title": unit.inner_text(),
        #             "url": unit.get_attribute("href")
        #         })
        #     hierarchy.append({"index": i, "title": title, "units": units})
        
        return hierarchy
