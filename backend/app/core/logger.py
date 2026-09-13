import sys

from loguru import logger

from app.config.settings import get_settings


def configure_logging() -> None:
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        colorize=True,
        backtrace=settings.debug,
        diagnose=settings.debug,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )


__all__ = ["configure_logging", "logger"]

