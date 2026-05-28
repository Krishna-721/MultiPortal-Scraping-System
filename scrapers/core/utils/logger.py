import logging
import os
import sys


def setup_logger(name: str) -> logging.Logger:
    os.makedirs("scrapers/logs", exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(f"scrapers/logs/{name}.log")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.stream.reconfigure(encoding="utf-8")
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
