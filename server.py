import uvicorn
import logging
from dotenv import load_dotenv
from src.tasks import initScheduler

load_dotenv()


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def main():
    # Configure logging
    configure_logging()
    logging.info("-----------")

    initScheduler()

    logging.info("Starting the Uvicorn server...")

    # Start the server
    uvicorn.run(
        "src.api:app",  # The ASGI app to run, module_name:app_instance
        host="0.0.0.0",
        port=8000,
        proxy_headers=True,
        log_level="debug",
        access_log=True,
    )


if __name__ == "__main__":
    main()
