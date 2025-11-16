import logging
import logging.config
from typing import Any


def setup_logging(
    logger_name: str | None,
    level: int = logging.NOTSET,
) -> Any:
    """
    Setup the logger `logger_name`
    """
    logging.basicConfig(level=level)
    logger = logging.getLogger(logger_name)
    if level != logging.NOTSET:
        logger.setLevel(level)
    # logger.propagate = False
    assert logger is not None
    # print('setup_logging() =>', logger)
    # print_logging_tree()
    return logger
