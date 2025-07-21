"""
Logging Utilities - Unified Logging Functionality

Provides unified logging functionality with support for different log levels and colored output.
"""

import logging
import sys
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ColorCode:
    """ANSI color codes"""
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    
    # Reset
    RESET = "\033[0m"
    
    # Combined styles
    BOLD_RED = BOLD + RED
    BOLD_GREEN = BOLD + GREEN
    BOLD_YELLOW = BOLD + YELLOW
    BOLD_BLUE = BOLD + BLUE
    BOLD_CYAN = BOLD + CYAN
    BOLD_MAGENTA = BOLD + MAGENTA


class StatusColor:
    """Status color mapping"""
    SUCCESS = ColorCode.BOLD_GREEN
    FAILURE = ColorCode.BOLD_RED
    RUNNING = ColorCode.BOLD_YELLOW
    UNKNOWN = ColorCode.BOLD_CYAN


class LevelColor:
    """Log level color mapping"""
    DEBUG = ColorCode.CYAN
    INFO = ColorCode.GREEN
    WARNING = ColorCode.YELLOW
    ERROR = ColorCode.RED
    CRITICAL = ColorCode.BOLD_RED


@dataclass
class LoggerConfig:
    """Logger configuration"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    console_output: bool = True
    enable_colors: bool = True
    show_emoji: bool = True
    compact_mode: bool = False


class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    def __init__(self, config: LoggerConfig):
        super().__init__()
        self.config = config
        self._setup_colors()
    
    def _setup_colors(self):
        """Setup color mappings"""
        self.level_colors = {
            logging.DEBUG: LevelColor.DEBUG,
            logging.INFO: LevelColor.INFO,
            logging.WARNING: LevelColor.WARNING,
            logging.ERROR: LevelColor.ERROR,
            logging.CRITICAL: LevelColor.CRITICAL,
        }
        
        self.status_colors = {
            "SUCCESS": StatusColor.SUCCESS,
            "FAILURE": StatusColor.FAILURE,
            "RUNNING": StatusColor.RUNNING,
        }
        
        self.emoji_map = {
            logging.DEBUG: "🔍",
            logging.INFO: "ℹ️",
            logging.WARNING: "⚠️",
            logging.ERROR: "❌",
            logging.CRITICAL: "🚨",
        }
    
    def format(self, record):
        """Format log record"""
        # Check if colors are supported
        if not self.config.enable_colors or not self._supports_color():
            return super().format(record)
        
        # Get original format
        original_format = self._style._fmt
        formatted = super().format(record)
        
        # Add colors
        if record.levelno in self.level_colors:
            color = self.level_colors[record.levelno]
            emoji = self.emoji_map.get(record.levelno, "") if self.config.show_emoji else ""
            
            # Add color to level name
            level_name = record.levelname
            colored_level = f"{color}{level_name}{ColorCode.RESET}"
            
            # Replace level name
            formatted = formatted.replace(level_name, colored_level)
            
            # Add emoji
            if emoji and self.config.show_emoji:
                formatted = f"{emoji} {formatted}"
        
        return formatted
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        # Check environment variable
        if os.environ.get("NO_COLOR"):
            return False
        
        # Check terminal type
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # Check platform
        if sys.platform.startswith('win'):
            return True  # Windows 10+ supports ANSI colors
        
        return True


class StatusFormatter(ColoredFormatter):
    """Status-specific formatter"""
    
    def format(self, record):
        """Format status logs"""
        if not self.config.enable_colors or not self._supports_color():
            return super().format(record)
        
        # Check if message contains status information
        message = record.getMessage()
        
        # Add colors to status
        for status, color in self.status_colors.items():
            if status in message:
                # Use regex to replace status names
                import re
                pattern = rf'\b{status}\b'
                colored_status = f"{color}{status}{ColorCode.RESET}"
                message = re.sub(pattern, colored_status, message)
                record.msg = message
                break
        
        return super().format(record)


def setup_logger(
    name: str = "abtree", config: Optional[LoggerConfig] = None
) -> logging.Logger:
    """
    Setup logger

    Args:
        name: Logger name
        config: Logger configuration

    Returns:
        Configured logger
    """
    if config is None:
        config = LoggerConfig()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    if config.enable_colors:
        formatter = ColoredFormatter(config)
    else:
        formatter = logging.Formatter(config.format)

    # Add console handler
    if config.console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler
    if config.file_path:
        file_handler = logging.FileHandler(config.file_path, encoding="utf-8")
        # File logs don't use colors
        file_formatter = logging.Formatter(config.format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "abtree") -> logging.Logger:
    """
    Get logger

    Args:
        name: Logger name

    Returns:
        Logger
    """
    return logging.getLogger(name)


# Predefined logger
_abtree_logger = None


def get_abtree_logger() -> logging.Logger:
    """
    Get ABTree main logger

    Returns:
        ABTree logger
    """
    global _abtree_logger
    if _abtree_logger is None:
        _abtree_logger = setup_logger("abtree")
    return _abtree_logger


def log_tree_execution(tree_name: str, status: str, duration: float = 0.0) -> None:
    """
    Log behavior tree execution

    Args:
        tree_name: Behavior tree name
        status: Execution status
        duration: Execution duration
    """
    logger = get_abtree_logger()
    logger.info(
        f"Behavior tree '{tree_name}' execution completed - Status: {status}, Duration: {duration:.3f}s"
    )


def log_node_execution(node_name: str, node_type: str, status: str) -> None:
    """
    Log node execution

    Args:
        node_name: Node name
        node_type: Node type
        status: Execution status
    """
    logger = get_abtree_logger()
    logger.debug(f"Node execution - Name: {node_name}, Type: {node_type}, Status: {status}")


def log_blackboard_access(key: str, operation: str, value: any = None) -> None:
    """
    Log blackboard access

    Args:
        key: Key name
        operation: Operation type
        value: Value
    """
    logger = get_abtree_logger()
    if value is not None:
        logger.debug(f"Blackboard access - Key: {key}, Operation: {operation}, Value: {value}")
    else:
        logger.debug(f"Blackboard access - Key: {key}, Operation: {operation}")


def log_event(event_name: str, source: str = None, data: any = None) -> None:
    """
    Log event

    Args:
        event_name: Event name
        source: Event source
        data: Event data
    """
    logger = get_abtree_logger()
    if source and data:
        logger.info(f"Event - Name: {event_name}, Source: {source}, Data: {data}")
    elif source:
        logger.info(f"Event - Name: {event_name}, Source: {source}")
    else:
        logger.info(f"Event - Name: {event_name}")


def log_error(message: str, error: Exception = None) -> None:
    """
    Log error

    Args:
        message: Error message
        error: Exception object
    """
    logger = get_abtree_logger()
    if error:
        logger.error(f"Error: {message}", exc_info=error)
    else:
        logger.error(f"Error: {message}")


def log_warning(message: str) -> None:
    """
    Log warning

    Args:
        message: Warning message
    """
    logger = get_abtree_logger()
    logger.warning(f"Warning: {message}")


def log_info(message: str) -> None:
    """
    Log info

    Args:
        message: Info message
    """
    logger = get_abtree_logger()
    logger.info(message)


def log_debug(message: str) -> None:
    """
    Log debug

    Args:
        message: Debug message
    """
    logger = get_abtree_logger()
    logger.debug(message)


def log_success(message: str) -> None:
    """
    Log success

    Args:
        message: Success message
    """
    logger = get_abtree_logger()
    logger.info(f"✅ {message}")


def log_failure(message: str) -> None:
    """
    Log failure

    Args:
        message: Failure message
    """
    logger = get_abtree_logger()
    logger.warning(f"❌ {message}")


def log_running(message: str) -> None:
    """
    Log running

    Args:
        message: Running message
    """
    logger = get_abtree_logger()
    logger.info(f"🔄 {message}")


def log_tree_status(tree_name: str, status: str, details: str = "") -> None:
    """
    Log behavior tree status

    Args:
        tree_name: Behavior tree name
        status: Status
        details: Details
    """
    logger = get_abtree_logger()
    if details:
        logger.info(f"Behavior tree '{tree_name}' status: {status} - {details}")
    else:
        logger.info(f"Behavior tree '{tree_name}' status: {status}")


def log_node_status(node_name: str, status: str, details: str = "") -> None:
    """
    Log node status

    Args:
        node_name: Node name
        status: Status
        details: Details
    """
    logger = get_abtree_logger()
    if details:
        logger.debug(f"Node '{node_name}' status: {status} - {details}")
    else:
        logger.debug(f"Node '{node_name}' status: {status}")


def log_performance(operation: str, duration: float, details: str = "") -> None:
    """
    Log performance

    Args:
        operation: Operation name
        duration: Execution duration
        details: Details
    """
    logger = get_abtree_logger()
    if details:
        logger.debug(f"Performance - {operation}: {duration:.3f}s - {details}")
    else:
        logger.debug(f"Performance - {operation}: {duration:.3f}s")


def log_memory_usage(usage_mb: float, details: str = "") -> None:
    """
    Log memory usage

    Args:
        usage_mb: Memory usage (MB)
        details: Details
    """
    logger = get_abtree_logger()
    if details:
        logger.debug(f"Memory usage: {usage_mb:.2f}MB - {details}")
    else:
        logger.debug(f"Memory usage: {usage_mb:.2f}MB")


def log_system_info(info: Dict[str, Any]) -> None:
    """
    Log system information

    Args:
        info: System information dictionary
    """
    logger = get_abtree_logger()
    info_str = ", ".join([f"{k}: {v}" for k, v in info.items()])
    logger.info(f"System info: {info_str}")


def log_configuration(config: Dict[str, Any]) -> None:
    """
    Log configuration information

    Args:
        config: Configuration information dictionary
    """
    logger = get_abtree_logger()
    config_str = ", ".join([f"{k}: {v}" for k, v in config.items()])
    logger.info(f"Configuration: {config_str}")


def create_status_logger(name: str = "status") -> logging.Logger:
    """
    Create status-specific logger

    Args:
        name: Logger name

    Returns:
        Status logger
    """
    config = LoggerConfig(
        level="INFO",
        format="%(asctime)s - %(levelname)s - %(message)s",
        enable_colors=True,
        show_emoji=True
    )
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # Use status formatter
    formatter = StatusFormatter(config)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def log_with_color(message: str, color: str = ColorCode.GREEN, level: str = "INFO") -> None:
    """
    Log with color

    Args:
        message: Log message
        color: Color code
        level: Log level
    """
    logger = get_abtree_logger()
    
    # Check if colors are supported
    if not os.environ.get("NO_COLOR") and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        colored_message = f"{color}{message}{ColorCode.RESET}"
    else:
        colored_message = message
    
    if level.upper() == "DEBUG":
        logger.debug(colored_message)
    elif level.upper() == "INFO":
        logger.info(colored_message)
    elif level.upper() == "WARNING":
        logger.warning(colored_message)
    elif level.upper() == "ERROR":
        logger.error(colored_message)
    elif level.upper() == "CRITICAL":
        logger.critical(colored_message)
    else:
        logger.info(colored_message)


# Convenient color log functions
def log_green(message: str) -> None:
    """Log green message"""
    log_with_color(message, ColorCode.GREEN)


def log_blue(message: str) -> None:
    """Log blue message"""
    log_with_color(message, ColorCode.BLUE)


def log_yellow(message: str) -> None:
    """Log yellow message"""
    log_with_color(message, ColorCode.YELLOW)


def log_red(message: str) -> None:
    """Log red message"""
    log_with_color(message, ColorCode.RED)


def log_cyan(message: str) -> None:
    """Log cyan message"""
    log_with_color(message, ColorCode.CYAN)


def log_magenta(message: str) -> None:
    """Log magenta message"""
    log_with_color(message, ColorCode.MAGENTA)


def log_bold(message: str, color: str = ColorCode.WHITE) -> None:
    """Log bold message"""
    log_with_color(message, ColorCode.BOLD + color)
