import logging
from pathlib import Path

from date_task_bot.config import get_config


def setup_logger() -> None:
    config = get_config()

    log_dir = Path("./logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL.value)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL.value)
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(config.LOG_LEVEL.value)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logging.getLogger("uvicorn").handlers = logger.handlers
    logging.getLogger("uvicorn.access").handlers = logger.handlers
    logging.getLogger("fastapi").handlers = logger.handlers
