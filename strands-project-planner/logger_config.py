import logging
import os
from datetime import datetime

def setup_logger():
    """Setup logger that appends to a single timestamped log file"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Single log file that gets appended to
    log_file = 'logs/project_planner.log'
    
    # Configure logger
    logger = logging.getLogger('ProjectPlanner')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # File handler (append mode)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler (only for important messages)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_session_start(logger):
    """Log the start of a new planning session"""
    logger.info("="*80)
    logger.info(f"NEW PROJECT PLANNING SESSION STARTED")
    logger.info("="*80) 