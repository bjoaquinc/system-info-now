#!/usr/bin/env python3

# standard library imports
import os
import json
import sys
import logging

# utils imports
from utils.logger import setup_logging

# system imports
from src.system.macos import (
    get_os_info, get_cpu_info, get_gpu_info, get_memory_info,
    get_disk_info, get_network_info, get_uptime_load, get_user_info,
    get_process_info, get_git_info, get_env_vars
)

# language imports
from src.languages.python.macos import get_python_debug_info
from src.languages.javascript.macos import get_javascript_debug_info

# third-party imports
try:
    import psutil
except ImportError:
    sys.exit("Error: The 'psutil' module is required. Install it with 'pip install psutil'.")

try:
    import yaml
except ImportError:
    sys.exit("Error: The 'pyyaml' module is required. Install it with 'pip install pyyaml'.")

# Primary function
def main():
    logger = setup_logging()
    logger.info("Starting system information collection")

    # Restructure data into three main categories
    data = {
        "system_debug_data": {},
        "python_debug_data": {},
        "javascript_debug_data": {}
    }
    
    try:
        # System Debug Data
        logger.info("Collecting system debug data")
        data["system_debug_data"].update({
            "os": get_os_info(),
            "cpu_info": get_cpu_info(),
            "gpu_info": get_gpu_info(),
            "memory_info": get_memory_info(),
            "disk_usage": get_disk_info(),
            "network_info": get_network_info(),
            "uptime": get_uptime_load(),
            "user": get_user_info(),
            "git": get_git_info() if get_git_info() is not None else "Not in a git repository",
            "environment": get_env_vars(),
            "processes": get_process_info()
        })

        # Python Debug Data
        logger.info("Collecting Python debug data")
        data["python_debug_data"] = get_python_debug_info()
        
        # JavaScript Debug Data
        logger.info("Collecting JavaScript debug data")
        data["javascript_debug_data"] = get_javascript_debug_info()

    except Exception as e:
        logger.error(f"Error collecting system data: {str(e)}")
        sys.exit(1)

    output_file = "system_data.json"
    try:
        logger.info(f"Writing data to {output_file}")
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully wrote system data to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write data to {output_file}: {str(e)}")
        sys.exit(1)

    logger.info("Script completed successfully")

if __name__ == '__main__':
    main()