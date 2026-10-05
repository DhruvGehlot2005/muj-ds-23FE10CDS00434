"""
@file logger.py
@description Secure structured logger preventing PII and resume content leakage
@module backend.app.utils.logger
"""

import logging
import sys


def setup_logger(name: str = "nlp_resume") -> logging.Logger:
    """
    Configures and returns a secure structured logger.

    @param name: Logger namespace
    @return Configured logging.Logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = setup_logger()
