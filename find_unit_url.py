from src.downloader import Downloader
from src.config import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_unit_url(search_term):
    downloader = Downloader(config.USERNAME, config.PASSWORD, headless=True)
    try:
        logger.info("Logging in...")
        downloader.login()
        
        logger.info("Getting hierarchy...")
        hierarchy = downloader.get_course_hierarchy()
        
        for module in hierarchy:
            for unit in module['units']:
                if search_term in unit['title']:
                    print(f"FOUND_UNIT: {unit['title']}")
                    print(f"FOUND_URL: {unit['url']}")
                    return unit['url']
        
        print(f"Unit with title containing '{search_term}' not found.")
        return None
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        downloader.stop()

if __name__ == "__main__":
    # Search for "8.6" which is one of the failed ones mentions
    find_unit_url("8.6")
