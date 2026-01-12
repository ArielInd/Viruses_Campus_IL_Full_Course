from playwright.sync_api import sync_playwright
from src.config import config
import time
import os
import re

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

    def sanitize_filename(self, filename):
        """Sanitize filename to be safe for the filesystem."""
        # Replace forbidden characters with underscores
        forbidden_chars = r'[\\/*?:"<<>>|"]'
        sanitized = re.sub(forbidden_chars, '_', filename)
        sanitized = sanitized.replace(' ', '_')
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_')

    def get_course_hierarchy(self):
        """
        Extract the course hierarchy.
        Returns a list of modules, each containing units.
        """
        hierarchy = []
        return hierarchy

    def create_directories(self, hierarchy, output_dir):
        """Create the directory structure based on the hierarchy."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        for module in hierarchy:
            module_name = f"{module['index']:02d}_{self.sanitize_filename(module['title'])}"
            module_path = os.path.join(output_dir, module_name)
            if not os.path.exists(module_path):
                os.makedirs(module_path)
            module['path'] = module_path
            
            for unit in module['units']:
                unit_name = f"{unit['index']:02d}_{self.sanitize_filename(unit['title'])}"
                unit['filename'] = unit_name + ".txt"