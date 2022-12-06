import logging
import sys


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%m-%d-%Y %H:%M:%S')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('logs.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

logger.info("INIT UWC LOGGER")


class UwcLogger:

    @staticmethod
    def add_info_log(title: str, message: str):
        logger.info(f"[{title}] - {message}")

    @staticmethod
    def add_error_log( title: str, message: str):
        logger.error(f"[{title}] - {message}")

