from src.downloader import Downloader
from src.config import config
import os
import logging

# Configure logging for main script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Define output directory
    output_dir = os.path.join(os.getcwd(), "course_transcripts")
    
    logger.info("Starting Campus IL Transcript Downloader")
    logger.info(f"Output directory: {output_dir}")
    
    downloader = Downloader(config.USERNAME, config.PASSWORD, headless=True)
    
    try:
        # 1. Login
        logger.info("Step 1: Logging in...")
        downloader.login()
        
        # 2. Get Hierarchy
        logger.info("Step 2: Extracting course hierarchy...")
        hierarchy = downloader.get_course_hierarchy()
        
        if not hierarchy:
            logger.error("Failed to extract course hierarchy. Exiting.")
            return

        # 3. Create Directories
        logger.info("Step 3: Creating directory structure...")
        downloader.create_directories(hierarchy, output_dir)
        
        # 4. Bulk Download
        logger.info("Step 4: Starting bulk download of transcripts...")
        results = downloader.bulk_download(hierarchy, output_dir)
        
        # 5. Generate Report
        logger.info("Step 5: Generating summary report...")
        report_path = downloader.generate_summary_report(results, output_dir)
        
        logger.info("Process complete!")
        logger.info(f"Summary report: {report_path}")
        logger.info(f"Transcripts stored in: {output_dir}")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        downloader.stop()

if __name__ == "__main__":
    main()
