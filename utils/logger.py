# utils/logger.py
import os
import logging
import datetime
import sys

def setup_logging():
    # Create logs directory if it doesn't exist 
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Setup logging configuration
    log_file = os.path.join('logs', f'system_info_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)