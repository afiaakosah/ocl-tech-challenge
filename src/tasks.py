import os
import logging
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from .extractor import extract_data
from .params import QueryParams
from .alert import send_alert, send_email_alert


EXTRACTION_INTERVAL = int(os.getenv("EXTRACTION_INTERVAL", "1"))


# Data extraction task
def run_extraction_task(property_type: str = "FULL", user_params: QueryParams = None):
    logging.info("Starting data extraction...")
    try:
        extract_data(property_type, user_params)
        logging.info("Data extraction completed successfully.")
    except Exception as e:
        error_message = f"Data extraction failed: {str(e)}"
        logging.error(error_message)
        logging.error(traceback.format_exc())
        send_email_alert(error_message)
        send_alert(error_message)


def initScheduler():
    logging.info("Extracting data...")

    run_extraction_task("SECT")
    run_extraction_task("FULL")

    logging.info("Initializing scheduler...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_extraction_task, "interval", days=EXTRACTION_INTERVAL)

    logging.info("Scheduler initialized. Starting...")
    scheduler.start()
