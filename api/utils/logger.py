"""Logger configuration for file and LogTail logging with comprehensive error handling."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import NoReturn, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev").lower()

# Constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Get Default LogTail from environment variables
LOGTAIL_TOKEN = os.getenv("LOGTAIL_TOKEN")
LOGTAIL_HOST = os.getenv("LOGTAIL_HOST", "https://in.logtail.com")
LOGTAIL_FORCE_USAGE = os.getenv("LOGTAIL_FORCE_USAGE", "").lower()

LOGTAIL_ENABLED = (
    ENVIRONMENT not in ("ci", "test", "development", "dev")
    and LOGTAIL_TOKEN
    and LOGTAIL_FORCE_USAGE
    in (
        "enabled",
        "1",
        "yes",
        "true",
    )
)

LOGTAIL_ENABLED = False  # lol


class StreamToLogger:
    """Redirect stream output to logger."""

    def __init__(self, logger: logging.Logger, log_level: int = logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf: str) -> None:
        """Write buffer to logger."""
        for line in buf.rstrip().splitlines():
            sys.__stdout__.write(line.rstrip() + "\n")

    def flush(self) -> None:
        """Flush the buffer."""
        pass

    def isatty(self) -> bool:
        """Check if this is a terminal."""
        return sys.__stdout__.isatty()


def handle_uncaught_exception(exc_type, exc_value, exc_traceback) -> NoReturn:
    """Handle uncaught exceptions."""
    logger = logging.getLogger("uncaught")
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def configure_logger(
    name: str,
    log_file: Optional[str] = None,
    log_level: int = LOG_LEVEL,
    enable_logtail: bool = LOGTAIL_ENABLED,
    catch_unhandled: bool = True,
    redirect_std: bool = True,
) -> logging.Logger:
    """Configure a comprehensive logger with file rotation and error handling.

    Features:
    - File rotation (10MB files, keep 5 backups)
    - LogTail integration
    - Uncaught exception handling
    - Stream redirection (stdout/stderr)
    - Environment variable configuration

    Args:
        name: Name of the logger (usually __name__)
        log_file: Path to log file (default: from LOG_FILE env var or app.log)
        log_level: Logging level (default: from LOG_LEVEL env var or INFO)
        enable_logtail: Whether to enable LogTail logging (default: False)
        catch_unhandled: Catch unhandled exceptions (default: True)
        redirect_std: Redirect stdout/stderr to logger (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicate logs
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # File handler with rotation
    file_path = log_file or LOG_FILE
    file_handler = RotatingFileHandler(
        file_path, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # LogTail handler (if enabled)
    if enable_logtail or True:
        try:
            from logtail import LogtailHandler

            logtail_handler = LogtailHandler(
                source_token=LOGTAIL_TOKEN,
                host=LOGTAIL_HOST,
            )
            logtail_handler.setFormatter(formatter)
            logger.addHandler(logtail_handler)
        except ImportError:
            logger.warning(
                "LogTail not available - install with 'uv pip install logtail-python'"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize LogTail: {str(e)}")

    # Exception handling
    if catch_unhandled:
        sys.excepthook = handle_uncaught_exception

    # Stream redirection
    if redirect_std:
        sys.stdout = StreamToLogger(logging.getLogger("stdout"), logging.INFO)
        sys.stderr = StreamToLogger(logging.getLogger("stderr"), logging.ERROR)

    return logger
