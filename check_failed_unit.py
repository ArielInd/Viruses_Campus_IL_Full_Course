from src.downloader import Downloader
from src.config import config
import logging

logging.basicConfig(level=logging.INFO)

downloader = Downloader(config.USERNAME, config.PASSWORD, headless=True)
try:
    print("Logging in...")
    downloader.login()
    
    print("Getting hierarchy...")
    hierarchy = downloader.get_course_hierarchy()
    
    target_unit = None
    for module in hierarchy:
        for unit in module['units']:
            if "4.2" in unit['title']:
                target_unit = unit
                break
        if target_unit:
            break
            
    if target_unit:
        print(f"Checking unit: {target_unit['title']}")
        print(f"URL: {target_unit['url']}")
        
        content = downloader.download_transcript(target_unit['url'])
        if content:
            print("✅ Transcript found!")
        else:
            print("❌ No transcript found.")
    else:
        print("Unit 4.2 not found in hierarchy.")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    downloader.stop()
