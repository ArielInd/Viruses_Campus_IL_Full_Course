from src.downloader import Downloader
from src.config import config
import json

downloader = Downloader(config.USERNAME, config.PASSWORD, headless=True)
try:
    print("Logging in...")
    downloader.login()
    
    print("Getting hierarchy (first module only)...")
    # monkey patch get_course_hierarchy to stop after first module to save time? 
    # No, just let it run or call the internal logic.
    # Actually, I'll just run it and break early if I could, but let's just run it.
    hierarchy = downloader.get_course_hierarchy()
    
    if hierarchy and hierarchy[2]['units']:
        # Module 3 usually has real content (Module 1 is intro)
        unit = hierarchy[2]['units'][1] # 1.1 "What is life?"
        print(f"FOUND_URL: {unit['url']}")
    
except Exception as e:
    print(e)
finally:
    downloader.stop()
