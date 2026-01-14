from src.downloader import Downloader
from src.config import config
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_button_download():
    downloader = Downloader(config.USERNAME, config.PASSWORD, headless=True)
    unit_url = "https://app.campus.gov.il/learning/course/course-v1:TAU+ACD_RFP1_HowToBeatViruses_HE+2022_1/block-v1:TAU+ACD_RFP1_HowToBeatViruses_HE+2022_1+type@sequential+block@585cc897195e495bac93ea1a8d8e8031"
    
    try:
        logger.info("Logging in...")
        downloader.login()
        
        logger.info(f"Visiting verified failed unit: {unit_url}")
        downloader.page.goto(unit_url)
        downloader.page.wait_for_load_state("domcontentloaded")
        
        # Wait for iframe
        downloader.page.wait_for_selector("iframe")
        
        # Iterate frames to find button
        button_found = False
        for frame in downloader.page.frames:
            try:
                # Search for button with "Text" or ".txt"
                # Subagent said "Download Text (.txt) file"
                buttons = frame.query_selector_all("button")
                for btn in buttons:
                    text = btn.inner_text()
                    if "Text" in text and "Download" in text:
                        logger.info(f"Found candidate button: {text}")
                        
                        # Try to click and download
                        logger.info("Clicking button and waiting for download...")
                        with downloader.page.expect_download(timeout=10000) as download_info:
                            btn.click()
                        
                        download = download_info.value
                        path = download.path()
                        logger.info(f"Downloaded to: {path}")
                        
                        # Read content
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            logger.info(f"Content length: {len(content)}")
                            logger.info(f"Preview: {content[:100]}")
                        
                        button_found = True
                        break
                if button_found: break
            except Exception as e:
                logger.error(f"Error in frame: {e}")
                
        if not button_found:
            logger.error("No button found!")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        downloader.stop()

if __name__ == "__main__":
    test_button_download()
