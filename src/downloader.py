from playwright.sync_api import sync_playwright
from src.config import config
import time
import os
import re
import logging
from datetime import datetime
from urllib.parse import urljoin

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
        self.page.goto("https://app.campus.gov.il/authn/login")
        self.page.wait_for_selector("#emailOrUsername")
        self.page.fill("#emailOrUsername", self.username)
        self.page.fill("#password", self.password)
        self.page.click("#sign-in")
        
        try:
            # Explicitly wait for dashboard URL pattern
            self.page.wait_for_url("**/learner-dashboard**", timeout=20000)
            self.logger.info("Successfully logged in.")
        except Exception:
            current_url = self.page.url
            if 'learner-dashboard' in current_url or 'dashboard' in current_url:
                self.logger.info("Successfully logged in (verified by URL check).")
            else:
                self.logger.warning(f"Login Wait Timeout. Current URL: {current_url}. Proceeding cautiously.")

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
        Extract the course hierarchy from Campus IL (Open edX platform).
        Returns a list of modules, each containing units.
        """
        if not self.page:
            self.start()
        
        # Convert marketing URL to learning URL
        # From: https://campus.gov.il/course/tau-acd-rfp1-howtobeatviruses-he/
        # To: https://app.campus.gov.il/learning/course/course-v1:TAU+ACD_RFP1_HowToBeatViruses_HE+2022_1/home
        course_url = config.COURSE_URL
        if 'campus.gov.il/course/' in course_url:
            # Extract course slug from marketing URL
            course_slug = course_url.rstrip('/').split('/')[-1]
            # Convert to learning URL format
            # This is a heuristic - may need adjustment based on actual URL pattern
            learning_url = f"https://app.campus.gov.il/learning/course/course-v1:TAU+ACD_RFP1_HowToBeatViruses_HE+2022_1/home"
            self.logger.info(f"Navigating to course home: {learning_url}")
            self.page.goto(learning_url)
        else:
            self.logger.info(f"Navigating to course: {course_url}")
            self.page.goto(course_url)
        
        self.page.wait_for_load_state("networkidle")
        
        # Wait for course content to load
        try:
            self.page.wait_for_selector(".pgn_collapsible", timeout=10000)
            self.logger.info("Course content loaded")
        except Exception as e:
            self.logger.warning(f"Timeout waiting for course content: {e}")
        
        # Additional wait for JavaScript
        time.sleep(2)
        
        # Click "Expand all" button to reveal all course content
        try:
            # Updated selector based on actual DOM structure
            expand_button = self.page.query_selector("button.btn-outline-primary.btn-block, button:has-text('הרחב הכל'), button:has-text('Expand all')")
            if expand_button:
                self.logger.info("Expanding all course sections...")
                expand_button.click()
                time.sleep(3)  # Increased wait for expansion
            else:
                self.logger.warning("Could not find expand all button")
        except Exception as e:
            self.logger.warning(f"Could not find/click expand button: {e}")
        
        hierarchy = []
        
        # Find all modules (sections)
        # Based on DOM investigation: each module is a .pgn_collapsible element
        module_elements = self.page.query_selector_all(".pgn_collapsible")
        
        self.logger.info(f"Found {len(module_elements)} modules")
        
        for module_idx, module_elem in enumerate(module_elements, start=1):
            # Extract module title from .collapsible-trigger span
            title_elem = module_elem.query_selector(".collapsible-trigger span")
            if not title_elem:
                self.logger.warning(f"Could not find title for module {module_idx}")
                continue
            
            module_title = title_elem.inner_text().strip()
            self.logger.info(f"Processing module {module_idx}: {module_title}")
            
            module = {
                "index": module_idx,
                "title": module_title,
                "units": []
            }
            
            # Find all units (sequentials) within this module
            unit_links = module_elem.query_selector_all("a[href*='type@sequential']")
            
            for unit_idx, unit_link in enumerate(unit_links, start=1):
                unit_title = unit_link.inner_text().strip()
                unit_url = unit_link.get_attribute("href")
                
                # Make URL absolute if it's relative
                if unit_url and not unit_url.startswith('http'):
                    unit_url = f"https://app.campus.gov.il{unit_url}"
                
                unit = {
                    "index": unit_idx,
                    "title": unit_title,
                    "url": unit_url
                }
                
                module["units"].append(unit)
                self.logger.info(f"  Found unit {unit_idx}: {unit_title}")
            
            hierarchy.append(module)
        
        self.logger.info(f"Extracted hierarchy: {len(hierarchy)} modules, {sum(len(m['units']) for m in hierarchy)} total units")
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
        """Download transcript from a unit page (handling iframes and tabs)."""
        if not self.page:
            self.start()
            
        self.logger.info(f"Visiting unit: {unit_url}")
        self.page.goto(unit_url)
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            self.logger.warning("Timeout waiting for page load, proceeding anyway...")
        
        # Helper to check for transcript in current view (iframe)
        def find_download_in_frames():
            for frame in self.page.frames:
                try:
                    # 1. Check for standard Links (<a>)
                    links = frame.query_selector_all("a.btn")
                    for link in links:
                        try:
                            text = link.inner_text()
                            href = link.get_attribute("href")
                            is_download_text = ("Download" in text or "הורד" in text) and ("(.txt)" in text or "Text" in text or "טקסט" in text)
                            is_txt_href = href and (".txt" in href)
                            
                            if is_download_text or is_txt_href:
                                self.logger.info(f"Found transcript link: {text} -> {href}")
                                if href and not href.startswith(('http:', 'https:')):
                                    href = urljoin(frame.url, href)
                                return ('url', href)
                        except Exception:
                            continue

                    # 2. Check for Buttons (<button>)
                    buttons = frame.query_selector_all("button")
                    for btn in buttons:
                        try:
                            text = btn.inner_text()
                            # Check for "Download" and "Text"/.txt
                            if ("Download" in text or "הורד" in text) and ("(.txt)" in text or "Text" in text or "טקסט" in text):
                                self.logger.info(f"Found transcript button: {text}")
                                # Click and capture download
                                with self.page.expect_download(timeout=10000) as download_info:
                                    btn.click()
                                download = download_info.value
                                path = download.path()
                                
                                # Read content
                                with open(path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Clean up temporary file if possible? Playwright manages it.
                                return ('content', content)
                        except Exception as e:
                            # self.logger.warning(f"Button check failed: {e}")
                            continue

                except Exception:
                    continue
            return None

        try:
            # Wait for content iframe to account for domcontentloaded being too early
            try:
                self.page.wait_for_selector("iframe", state="attached", timeout=10000)
            except:
                pass
                
            result = find_download_in_frames()
            if result:
                rtype, rvalue = result
                self.logger.info(f"Found transcript in first tab ({rtype}).")
                if rtype == 'url':
                    return self._download_file_from_url(rvalue)
                else:
                    return rvalue
        except Exception as e:
            self.logger.warning(f"Error checking first tab: {e}")

        # 2. Iterate through other tabs (verticals)
        try:
            tabs = self.page.query_selector_all(".sequence-navigation-tabs a.btn-link")
            if not tabs:
                return None
            
            for i, tab in enumerate(tabs):
                tab_title = tab.get_attribute("title")
                # self.logger.info(f"Checking tab {i+1}: {tab_title}")
                
                tab.click()
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                except:
                    pass
                time.sleep(1) 
                
                result = find_download_in_frames()
                if result:
                    rtype, rvalue = result
                    self.logger.info(f"Found transcript in tab {i+1} ({rtype}).")
                    if rtype == 'url':
                        return self._download_file_from_url(rvalue)
                    else:
                        return rvalue
                    
        except Exception as e:
            self.logger.warning(f"Error iterating tabs: {e}")

        self.logger.warning("No transcript found in any tab.")
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

    def generate_summary_report(self, results, output_dir):
        """Generate a summary.txt report file."""
        report_path = os.path.join(output_dir, "summary.txt")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"Course Transcript Downloader - Summary Report\n")
            f.write(f"Generated at: {now}\n")
            f.write(f"{ '='*45}\n\n")
            
            f.write(f"Statistics:\n")
            f.write(f"- Downloaded: {len(results['downloaded'])}\n")
            f.write(f"- Skipped: {len(results['skipped'])}\n")
            f.write(f"- Failed: {len(results['failed'])}\n\n")
            
            if results["downloaded"]:
                f.write(f"Downloaded Transcripts:\n")
                for unit in results["downloaded"]:
                    f.write(f"- {unit['title']} ({unit['filename']})\n")
                f.write("\n")
                
            if results["skipped"]:
                f.write(f"Skipped (Already Exists):\n")
                for unit in results["skipped"]:
                    f.write(f"- {unit['title']} ({unit['filename']})\n")
                f.write("\n")
                
            if results["failed"]:
                f.write(f"Failed Downloads:\n")
                for unit in results["failed"]:
                    f.write(f"- {unit['title']}\n")
                f.write("\n")
                
        self.logger.info(f"Summary report generated at: {report_path}")
        return report_path