import logging
import dotenv
import os
dotenv.load_dotenv()
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", 5))
MAX_BUFFER_SIZE = int(os.getenv("MAX_BUFFER_SIZE", 1024))

def setup_logger(name: str, level: str = "DEBUG") -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(level)

    if not logger.handlers:
        ch = logging.StreamHandler()
        fh = logging.FileHandler(f"{name}.log")
        fh.setLevel(level)
        ch.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger

logger = setup_logger("socket_server", os.getenv("LOG_LEVEL", "DEBUG"))

if __name__ == "__main__":
    pass