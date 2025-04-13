#!/usr/bin/env python3

# standard library imports
import os
import json
import sys
import logging
from pathlib import Path

# utils imports
from utils.logger import setup_logging
from utils.platform_detect import get_platform

# third-party imports
try:
    import psutil
except ImportError:
    sys.exit("Error: The 'psutil' module is required. Install it with 'pip install psutil'.")

try:
    import yaml
except ImportError:
    sys.exit("Error: The 'pyyaml' module is required. Install it with 'pip install pyyaml'.")

def load_config():
    config_path = Path("config.yaml")
    default_config = {
        "output": {
            "format": "json",
            "directory": "output",
            "filename": "system_data.json"
        },
        "logging": {
            "level": "INFO",
            "directory": "logs"
        },
        "project": {
            "root_dir": "."  # Default to current directory
        },
        "collectors": {
            "system": True,
            "python": True,
            "javascript": True
        }
    }
    
    if not config_path.exists():
        return default_config
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def import_platform_modules(platform_name):
    """Import the appropriate modules based on the platform."""
    if platform_name == 'darwin':
        # macOS
        from src.system.macos import (
            get_os_info, get_cpu_info, get_gpu_info, get_memory_info,
            get_disk_info, get_network_info, get_uptime_load, get_user_info,
            get_process_info, get_git_info, get_env_vars
        )
        from src.languages.python.macos import get_python_debug_info
        from src.languages.javascript.macos import get_javascript_debug_info
    elif platform_name == 'linux':
        # Linux
        from src.system.linux import (
            get_os_info, get_motherboard_info, get_cpu_info, get_gpu_info, get_memory_info,
            get_disk_info, get_network_info, get_uptime_load, get_user_info,
            get_process_info, get_git_info, get_env_vars
        )
        from src.languages.python.linux import get_python_debug_info
        from src.languages.javascript.linux import get_javascript_debug_info
    else:
        # Unsupported platform
        sys.exit(f"Error: Unsupported platform '{platform_name}'. Currently only macOS and Linux are supported.")
    
    return {
        'get_os_info': get_os_info,
        'get_motherboard_info': get_motherboard_info if platform_name == 'linux' else None,
        'get_cpu_info': get_cpu_info,
        'get_gpu_info': get_gpu_info,
        'get_memory_info': get_memory_info,
        'get_disk_info': get_disk_info,
        'get_network_info': get_network_info,
        'get_uptime_load': get_uptime_load,
        'get_user_info': get_user_info,
        'get_process_info': get_process_info,
        'get_git_info': get_git_info,
        'get_env_vars': get_env_vars,
        'get_python_debug_info': get_python_debug_info,
        'get_javascript_debug_info': get_javascript_debug_info
    }

# Primary function
def main():
    config = load_config()
    
    # Convert root_dir to absolute path
    project_root = Path(config['project']['root_dir']).resolve()
    
    # Setup logging based on config
    logger = setup_logging(
        level=config['logging']['level'],
        log_dir=config['logging']['directory']
    )
    logger.info(f"Starting system information collection for project at: {project_root}")

    # Detect platform
    platform_name = get_platform()
    logger.info(f"Detected platform: {platform_name}")
    
    # Import platform-specific modules
    if platform_name not in ['darwin', 'linux']:
        logger.error(f"Unsupported platform: {platform_name}")
        sys.exit(f"Error: Unsupported platform '{platform_name}'. Currently only macOS and Linux are supported.")
    
    modules = import_platform_modules(platform_name)

    # Restructure data into three main categories
    data = {
        "system_debug_data": {},
        "python_debug_data": {},
        "javascript_debug_data": {}
    }
    
    try:
        # System Debug Data
        if config['collectors']['system']:
            logger.info("Collecting system debug data")
            data["system_debug_data"].update({
                "os": modules['get_os_info'](),
                # For linux only, idk the command for macOS
                "motherboard_info": modules['get_motherboard_info']() if platform_name == 'linux' else None,
                "cpu_info": modules['get_cpu_info'](),
                "gpu_info": modules['get_gpu_info'](),
                "memory_info": modules['get_memory_info'](),
                "disk_usage": modules['get_disk_info'](),
                "network_info": modules['get_network_info'](),
                "uptime": modules['get_uptime_load'](),
                "user": modules['get_user_info'](),
                "git": modules['get_git_info']() if modules['get_git_info']() is not None else "Not in a git repository",
                "environment": modules['get_env_vars'](),
                "processes": modules['get_process_info']()
            })

        # Python Debug Data
        if config['collectors']['python']:
            logger.info("Collecting Python debug data")
            data["python_debug_data"] = modules['get_python_debug_info'](project_root)
        
        # JavaScript Debug Data
        if config['collectors']['javascript']:
            logger.info("Collecting JavaScript debug data")
            data["javascript_debug_data"] = modules['get_javascript_debug_info'](project_root)

    except Exception as e:
        logger.error(f"Error collecting system data: {str(e)}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir = Path(config['output']['directory'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / config['output']['filename']
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