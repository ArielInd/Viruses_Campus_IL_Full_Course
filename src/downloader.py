from playwright.sync_api import sync_playwright
from src.config import config
import time
import os
import re
import logging

# Configure logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class Downloader:
    def __init__(self, username, password, headless=True):
        self.username = username
        self.password = password
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.logger = logger

    def start(self):
        """Initialize playwright and browser."""
        self.logger.info("Initializing browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def stop(self):
        """Close browser and stop playwright."""
        if self.browser:
            self.logger.info("Closing browser.")
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login(self):
        """Log in to Campus IL."""
        if not self.page:
            self.start()
        
        self.logger.info(f"Logging in as {self.username}...")
        self.page.goto("https://campus.gov.il/login/")
        self.page.wait_for_selector("#emailOrUsername")
        self.page.fill("#emailOrUsername", self.username)
        self.page.fill("#password", self.password)
        self.page.click("#sign-in")
        self.page.wait_for_load_state("networkidle")
        
        if self.is_logged_in():
            self.logger.info("Successfully logged in.")
        else:
            self.logger.error("Login failed.")

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
        self.logger.info(f"Navigating to course: {config.COURSE_URL}")
        self.page.goto(config.COURSE_URL)
        self.page.wait_for_load_state("networkidle")

    def sanitize_filename(self, filename):
        """Sanitize filename to be safe for the filesystem."""
        forbidden_chars = r'[\\/*?:"<<>>|"]'
        sanitized = re.sub(forbidden_chars, '_', filename)
        sanitized = sanitized.replace(' ', '_')
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

    def download_transcript(self, unit_url):
        """Download transcript from a unit page."""
        if not self.page:
            self.start()
            
        self.page.goto(unit_url)
        transcript_link = self.page.query_selector("a[href*='transcript'][href$='.txt']")
        if not transcript_link:
            transcript_link = self.page.query_selector("a:has-text('Transcript')")
            
        if transcript_link:
            url = transcript_link.get_attribute("href")
            return self._download_file_from_url(url)
        return None

    def _download_file_from_url(self, url):
        """Download file content from URL using the browser's context."""
        response = self.page.request.get(url)
        if response.status == 200:
            return response.text()
        return None

    def save_transcript(self, content, folder_path, filename):
        """Save transcript content to a file."""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def bulk_download(self, hierarchy, output_dir):
        """Iterate through hierarchy and download missing transcripts."""
        results = {"downloaded": [], "skipped": [], "failed": []}
        
        self.logger.info("Starting bulk download...")
        
        for module in hierarchy:
            module_path = module.get('path')
            if not module_path:
                module_name = f"{module['index']:02d}_{self.sanitize_filename(module['title'])}"
                module_path = os.path.join(output_dir, module_name)
                
            for unit in module['units']:
                file_path = os.path.join(module_path, unit['filename'])
                
                if os.path.exists(file_path):
                    self.logger.info(f"Skipping (already exists): {unit['filename']}")
                    results["skipped"].append(unit)
                    continue
                
                self.logger.info(f"Downloading: {unit['filename']}...")
                content = self.download_transcript(unit['url'])
                if content:
                    self.save_transcript(content, module_path, unit['filename'])
                    self.logger.info(f"Successfully downloaded: {unit['title']}")
                    results["downloaded"].append(unit)
                else:
                    self.logger.error(f"Failed to download: {unit['title']}")
                    results["failed"].append(unit)
        
        self.logger.info(f"Bulk download complete. Summary: {len(results['downloaded'])} downloaded, {len(results['skipped'])} skipped, {len(results['failed'])} failed.")
        return results
