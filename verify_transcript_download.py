from src.downloader import Downloader
from src.config import config

downloader = Downloader(config.USERNAME, config.PASSWORD, headless=True)
unit_url = "https://app.campus.gov.il/learning/course/course-v1:TAU+ACD_RFP1_HowToBeatViruses_HE+2022_1/block-v1:TAU+ACD_RFP1_HowToBeatViruses_HE+2022_1+type@sequential+block@232e4e6fc42440f58c95c154f94e07d6"

try:
    print("Logging in...")
    downloader.login()
    
    print(f"Attempting to download transcript from: {unit_url}")
    
    # Manually debug the page
    downloader.page.goto(unit_url)
    downloader.page.wait_for_load_state("networkidle")
    import time
    time.sleep(5) # Wait for iframes
    
    print(f"Main frame URL: {downloader.page.url}")
    print(f"Total frames: {len(downloader.page.frames)}")
    
    for i, frame in enumerate(downloader.page.frames):
        print(f"Frame {i}: {frame.url}")
        try:
            # Check for any .txt links
            links = frame.query_selector_all("a")
            for link in links:
                href = link.get_attribute("href")
                text = link.inner_text()
                if href and ".txt" in href:
                    print(f"  FOUND .txt LINK: {text} -> {href}")
                if "Download" in text:
                    print(f"  FOUND Download LINK: {text} -> {href}")
        except Exception as e:
            print(f"  Error accessing frame: {e}")

    # Now try the method
    content = downloader.download_transcript(unit_url)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    downloader.stop()
