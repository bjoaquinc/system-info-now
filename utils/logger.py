# utils/logger.py
import os
import logging
import datetime
import sys
from pathlib import Path

def setup_logging(level='INFO', log_dir='logs'):
    # Convert string level to logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist using Path
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Setup logging configuration
    log_file = log_path / f'system_info_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)