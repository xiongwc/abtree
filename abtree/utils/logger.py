"""
Logging Utilities - Unified Logging Functionality

Provides unified logging functionality with support for different log levels and colored output.
"""

import logging
import os
import sys
import inspect
from dataclasses import dataclass
from typing import Optional


class ColorCode:
    """ANSI color codes"""
    # Foreground colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Styles
    BOLD = "\033[1m"
    
    # Reset
    RESET = "\033[0m"
    
    # Combined styles
    BOLD_RED = BOLD + RED


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
    format: str = "%(asctime)s | %(levelname)s | %(classname)s | %(message)s"
    enable_colors: bool = True


class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    def __init__(self, config: LoggerConfig):
        super().__init__(config.format)
        self.config = config
        self._setup_colors()
    
    def _setup_colors(self) -> None:
        """Setup color mappings"""
        self.level_colors = {
            logging.DEBUG: LevelColor.DEBUG,
            logging.INFO: LevelColor.INFO,
            logging.WARNING: LevelColor.WARNING,
            logging.ERROR: LevelColor.ERROR,
            logging.CRITICAL: LevelColor.CRITICAL,
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record"""
        # Add classname to record if not present
        if not hasattr(record, 'classname'):
            # Try to extract class name from the logger name or module
            classname = record.name.split('.')[-1] if record.name else "Unknown"
            record.classname = classname
        
        # Check if colors are supported
        if not self.config.enable_colors or not self._supports_color():
            return super().format(record)
        
        # Parse the formatted string to add colors to different parts
        formatted = super().format(record)
        
        # Split by | to get different parts
        parts = formatted.split(" | ")
        if len(parts) == 4:
            time_part = parts[0]
            level_part = parts[1]
            classname_part = parts[2]
            message_part = parts[3]
            
            # Add colors to different parts
            colored_time = f"{ColorCode.GREEN}{time_part}{ColorCode.RESET}"
            
            # Color for level based on log level
            level_color = self.level_colors.get(record.levelno, ColorCode.WHITE)
            colored_level = f"{level_color}{level_part}{ColorCode.RESET}"
            
            # Blue color for classname
            colored_classname = f"{ColorCode.BLUE}{classname_part}{ColorCode.RESET}"
            
            # White color for message
            colored_message = f"{ColorCode.WHITE}{message_part}{ColorCode.RESET}"
            
            # Reconstruct the formatted string
            formatted = f"{colored_time} | {colored_level} | {colored_classname} | {colored_message}"
        else:
            # Fallback: just color the level name
            if record.levelno in self.level_colors:
                color = self.level_colors[record.levelno]
                level_name = record.levelname
                colored_level = f"{color}{level_name}{ColorCode.RESET}"
                formatted = formatted.replace(level_name, colored_level)
        
        return formatted
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        # Force enable colors for testing
        return True


class ABTreeLogger:
    """
    ABTree Logger Class
    
    A unified logger class that provides colored logging functionality
    with support for different log levels and automatic classname detection.
    """
    
    def __init__(self, name: str = "abtree", config: Optional[LoggerConfig] = None):
        """
        Initialize logger
        
        Args:
            name: Logger name
            config: Logger configuration
        """
        self.name = name
        self.config = config or LoggerConfig()
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup the underlying logger"""
        # Create logger
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(getattr(logging, self.config.level.upper()))

        # Clear existing handlers
        self._logger.handlers.clear()

        # Create formatter
        if self.config.enable_colors:
            formatter: logging.Formatter = ColoredFormatter(self.config)
        else:
            formatter = logging.Formatter(self.config.format)

        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
    
    def _get_calling_classname(self) -> str:
        """Automatically detect the calling class name"""
        try:
            # Get the call stack
            frame = inspect.currentframe()
            # Go up 2 frames: 1 for the logging method, 1 for the caller
            caller_frame = frame.f_back.f_back if frame and frame.f_back else None
            
            if caller_frame:
                # Get the 'self' parameter from the calling frame
                if 'self' in caller_frame.f_locals:
                    calling_class = caller_frame.f_locals['self'].__class__.__name__
                    return str(calling_class)
                
                # If no 'self', try to get from the function name or module
                func_name = caller_frame.f_code.co_name
                if func_name != '<module>':
                    return str(func_name)
                
                # Fallback to module name
                module_name = caller_frame.f_globals.get('__name__', 'Unknown')
                return str(module_name.split('.')[-1])
            
        except Exception:
            pass
        
        return "Unknown"
    
    def get_logger(self) -> logging.Logger:
        """Get underlying logger"""
        return self._logger
    
    def set_level(self, level: str) -> None:
        """Set log level"""
        self._logger.setLevel(getattr(logging, level.upper()))
    
    def debug(self, message: str) -> None:
        """Log debug message with automatic classname detection"""
        classname = self._get_calling_classname()
        extra = {'classname': classname}
        self._logger.debug(message, extra=extra)
    
    def info(self, message: str) -> None:
        """Log info message with automatic classname detection"""
        classname = self._get_calling_classname()
        extra = {'classname': classname}
        self._logger.info(message, extra=extra)
    
    def warning(self, message: str) -> None:
        """Log warning message with automatic classname detection"""
        classname = self._get_calling_classname()
        extra = {'classname': classname}
        self._logger.warning(message, extra=extra)
    
    def error(self, message: str) -> None:
        """Log error message with automatic classname detection"""
        classname = self._get_calling_classname()
        extra = {'classname': classname}
        self._logger.error(message, extra=extra)
    
    def critical(self, message: str) -> None:
        """Log critical message with automatic classname detection"""
        classname = self._get_calling_classname()
        extra = {'classname': classname}
        self._logger.critical(message, extra=extra)
    
    def log_with_color(self, message: str, color: str = ColorCode.GREEN, level: str = "INFO") -> None:
        """
        Log with custom color and automatic classname detection
        
        Args:
            message: Log message
            color: Color code
            level: Log level
        """
        classname = self._get_calling_classname()
        extra = {'classname': classname}
        
        if level.upper() == "DEBUG":
            self._logger.debug(message, extra=extra)
        elif level.upper() == "INFO":
            self._logger.info(message, extra=extra)
        elif level.upper() == "WARNING":
            self._logger.warning(message, extra=extra)
        elif level.upper() == "ERROR":
            self._logger.error(message, extra=extra)
        elif level.upper() == "CRITICAL":
            self._logger.critical(message, extra=extra)
        else:
            self._logger.info(message, extra=extra)


# Global logger instances
_logger_instances = {}


def get_logger(name: str = "abtree", config: Optional[LoggerConfig] = None) -> ABTreeLogger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name
        config: Logger configuration
        
    Returns:
        ABTreeLogger instance
    """
    global _logger_instances
    
    if name not in _logger_instances:
        _logger_instances[name] = ABTreeLogger(name, config)
    
    return _logger_instances[name]


def get_abtree_logger() -> logging.Logger:
    """
    Get abtree logger instance
    
    Returns:
        abtree logger instance
    """
    logger = get_logger("abtree")
    
    # If logger has no handlers, set it up
    if not logger.get_logger().handlers:
        config = LoggerConfig(level="DEBUG", enable_colors=True)
        logger = get_logger("abtree", config)
    
    return logger.get_logger()
