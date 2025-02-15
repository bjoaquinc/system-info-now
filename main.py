#!/usr/bin/env python3
import platform
import os
import json
import subprocess
import getpass
import datetime
import sys
import logging
import site
from pathlib import Path

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

try:
    import psutil
except ImportError:
    sys.exit("Error: The 'psutil' module is required. Install it with 'pip install psutil'.")

def get_os_info():
    if platform.system() != 'Darwin':
        raise SystemError("This tool is designed for macOS only")
    return {
        "name": platform.system(),
        "version": platform.version(),
        "release": platform.release(),
        "architecture": platform.machine()
    }

def get_cpu_info():
    return {
        "processor": platform.processor(),
        "cores": psutil.cpu_count(logical=False),
        "logical_processors": psutil.cpu_count(logical=True)
    }

def get_gpu_info():
    """Get GPU information relevant for AI/ML workloads on macOS."""
    try:
        cmd = ['system_profiler', 'SPDisplaysDataType', '-json']
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            gpu_data = json.loads(result.stdout)
            gpus = []
            for gpu in gpu_data.get('SPDisplaysDataType', []):
                gpu_info = {
                    'name': gpu.get('_name', 'Unknown'),
                    'metal_support': gpu.get('spdisplays_mtlgpufamilysupport', '').replace('spdisplays_', ''),
                    'vendor': gpu.get('spdisplays_vendor', '').replace('sppci_vendor_', ''),
                    'cores': gpu.get('sppci_cores', '0'),
                    'device_type': gpu.get('sppci_device_type', '').replace('spdisplays_', ''),
                    'model': gpu.get('sppci_model', 'Unknown'),
                    'bus': gpu.get('sppci_bus', '').replace('spdisplays_', '')
                }
                gpus.append(gpu_info)
            return gpus
        return None
    except Exception as e:
        logging.error(f"Error getting GPU information: {str(e)}")
        return None

def get_memory_info():
    """Get memory information relevant for ML/AI workloads."""
    try:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "total_memory": f"{vm.total / (1024**3):.2f} GB",  # Total usable memory (RAM + Swap)
            "available": f"{vm.available / (1024**3):.2f} GB",        # Currently available
            "percent_used": f"{vm.percent}%",                         # Memory pressure indicator
            "total_swap": f"{swap.total / (1024**3):.2f} GB",
            "swap_used": f"{swap.percent}%"                          # Swap pressure indicator
        }
    except Exception as e:
        logging.error(f"Error getting memory info: {str(e)}")
        return None

def get_swap_info():
    """Get swap memory information."""
    swap = psutil.swap_memory()
    return {
        "total": f"{swap.total / (1024**3):.2f} GB",
        "used": f"{swap.used / (1024**3):.2f} GB",
        "free": f"{swap.free / (1024**3):.2f} GB",
        "percent_used": f"{swap.percent}%"
    }

def get_disk_info():
    du = psutil.disk_usage('/')
    return {
        "total": du.total,
        "used": du.used,
        "free": du.free,
        "percent": du.percent
    }

def get_network_info():
    addrs = psutil.net_if_addrs()
    network_data = {}
    for iface, addr_list in addrs.items():
        network_data[iface] = []
        for addr in addr_list:
            network_data[iface].append({
                "family": str(addr.family),
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast
            })
    return network_data

def get_uptime_load():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat()
    try:
        loadavg = os.getloadavg()
        return {
            "boot_time": boot_time,
            "load_average": loadavg
        }
    except Exception as e:
        logging.error(f"Error getting load average: {str(e)}")
        return {"boot_time": boot_time}

def get_is_admin():
    """Check if the current user has administrator privileges on macOS."""
    try:
        return os.geteuid() == 0
    except Exception as e:
        logging.error(f"Error checking admin status: {str(e)}")
        return False

def get_user_info():
    return {
        "user": getpass.getuser(),
        "is_admin": get_is_admin()
    }

def get_git_info():
    # First, check if Git is available
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        return None

    # Then check if the current directory is inside a Git repository.
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        return None

    # If inside a repo, gather branch, status, and last commit info.
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                         universal_newlines=True).strip()
    except Exception:
        branch = "N/A"

    try:
        status = subprocess.check_output(["git", "status", "--short"],
                                         universal_newlines=True).strip()
    except Exception:
        status = "N/A"

    try:
        last_commit = subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%h - %s (%ci)"],
            universal_newlines=True
        ).strip()
    except Exception:
        last_commit = "N/A"

    return {
        "branch": branch,
        "status": status,
        "last_commit": last_commit
    }

def get_env_vars():
    # Be cautious: environment variables may contain sensitive information.
    return dict(os.environ)

def get_process_info():
    # Gather the top 10 processes by CPU usage.
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            info = proc.info
            # Ensure cpu_percent has a valid value, default to 0 if None
            if info['cpu_percent'] is None:
                info['cpu_percent'] = 0.0
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # Sort processes by CPU usage in descending order
    processes = sorted(processes, key=lambda p: float(p.get('cpu_percent', 0)), reverse=True)[:10]
    return processes

def get_python_debug_info():
    """Get detailed Python environment information for debugging."""
    try:
        python_info = {
            "runtime": {
                "version": sys.version,
                "executable": sys.executable,
                "encoding": {
                    "filesystem": sys.getfilesystemencoding(),
                    "default": sys.getdefaultencoding()
                }
            },
            "paths": {
                "pythonpath": sys.path,
                "site_packages": site.getsitepackages(),
                "user_site_packages": site.getusersitepackages()
            },
            "dependencies": {
                "requirements": {
                    "exists": os.path.exists('requirements.txt'),
                    "content": None,
                },
                "packages": {
                    "installed": None,
                    "outdated": None
                },
                "pip": {
                    "version": None,
                    "config": None
                }
            },
            "virtual_environments": {
                "active": {
                    "path": os.environ.get('VIRTUAL_ENV'),
                    "name": os.path.basename(os.environ.get('VIRTUAL_ENV', '')),
                    "packages": None,
                    "python_version": None,
                    "pip_version": None,
                    "pip_config": None
                },
                "detected": {}
            }
        }

        # Get requirements.txt content if it exists
        if python_info["dependencies"]["requirements"]["exists"]:
            with open('requirements.txt', 'r') as f:
                python_info["dependencies"]["requirements"]["content"] = f.read()

        # Get pip version and installed packages
        try:
            pip_version = subprocess.check_output(
                [sys.executable, "-m", "pip", "--version"],
                text=True
            ).strip()
            python_info["dependencies"]["pip"]["version"] = pip_version

            installed_packages = subprocess.check_output(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                text=True
            )
            python_info["dependencies"]["packages"]["installed"] = json.loads(installed_packages)

            outdated = subprocess.check_output(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                text=True
            )
            python_info["dependencies"]["packages"]["outdated"] = json.loads(outdated)

            pip_config = subprocess.check_output(
                [sys.executable, "-m", "pip", "config", "list"],
                text=True
            )
            python_info["dependencies"]["pip"]["config"] = pip_config
        except Exception as e:
            python_info["dependencies"]["error"] = f"Error getting pip information: {str(e)}"

        # Virtual environments detection
        venv_locations = [
            os.path.expanduser('~/.virtualenvs/'),
            os.path.expanduser('~/venvs/'),
            os.getcwd(),
            os.path.expanduser('~/Desktop/'),
        ]

        for location in venv_locations:
            if os.path.exists(location):
                for item in os.listdir(location):
                    potential_venv = os.path.join(location, item)
                    if os.path.exists(os.path.join(potential_venv, 'bin', 'python')):
                        venv_info = {
                            "path": potential_venv,
                            "name": item,
                            "packages": None,
                            "python_version": None,
                            "pip_version": None,
                            "pip_config": None
                        }
                        
                        try:
                            venv_python = os.path.join(potential_venv, 'bin', 'python')
                            venv_pip = os.path.join(potential_venv, 'bin', 'pip')
                            
                            # Get Python version
                            version_output = subprocess.check_output(
                                [venv_python, "--version"],
                                text=True
                            )
                            venv_info["python_version"] = version_output.strip()
                            
                            # Get pip version
                            pip_version = subprocess.check_output(
                                [venv_pip, "--version"],
                                text=True
                            ).strip()
                            venv_info["pip_version"] = pip_version

                            # Get installed packages
                            packages = subprocess.check_output(
                                [venv_pip, "list", "--format=json"],
                                text=True
                            )
                            venv_info["packages"] = json.loads(packages)
                            
                            # Get pip config
                            pip_config = subprocess.check_output(
                                [venv_pip, "config", "list"],
                                text=True
                            )
                            venv_info["pip_config"] = pip_config
                            
                        except Exception as e:
                            venv_info["error"] = f"Error getting venv info: {str(e)}"

                        if potential_venv == os.environ.get('VIRTUAL_ENV'):
                            python_info["virtual_environments"]["active"].update(venv_info)
                        else:
                            python_info["virtual_environments"]["detected"][potential_venv] = venv_info

        return python_info
    except Exception as e:
        return f"Error getting Python debug info: {str(e)}"

def get_javascript_debug_info():
    """Get detailed JavaScript environment information for debugging on macOS."""
    try:
        js_info = {
            "node": {
                "installed": False,
                "version": None,
                "npm_version": None,
                "global_packages": None,
                "local_packages": None,
                "missing_dependencies": None,
                "npm_config": None
            },
            "browsers": {}
        }
        
        # Check Node.js installation
        try:
            node_version = subprocess.check_output(["node", "--version"], text=True).strip()
            npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
            js_info["node"].update({
                "installed": True,
                "version": node_version,
                "npm_version": npm_version
            })
            
            # Get global npm packages
            npm_packages = subprocess.check_output(["npm", "list", "-g", "--json"], text=True)
            js_info["node"]["global_packages"] = json.loads(npm_packages)

            # Get local packages if package.json exists
            if os.path.exists('package.json'):
                # Read package.json
                with open('package.json', 'r') as f:
                    package_json = json.load(f)
                
                # Get actual installed packages
                try:
                    local_packages = subprocess.check_output(["npm", "list", "--json"], text=True)
                    js_info["node"]["local_packages"] = json.loads(local_packages)
                    
                    # Check for missing dependencies
                    missing_deps = []
                    required_deps = {
                        **package_json.get('dependencies', {}),
                        **package_json.get('devDependencies', {})
                    }
                    
                    node_modules_path = Path('node_modules')
                    for dep in required_deps:
                        dep_path = node_modules_path / dep
                        if not dep_path.exists():
                            missing_deps.append(dep)
                    
                    if missing_deps:
                        js_info["node"]["missing_dependencies"] = {
                            "count": len(missing_deps),
                            "packages": missing_deps,
                            "recommendation": "Run 'npm install' to install missing packages"
                        }
                    else:
                        js_info["node"]["missing_dependencies"] = {
                            "count": 0,
                            "packages": [],
                            "status": "All dependencies are installed"
                        }
                except subprocess.CalledProcessError as e:
                    js_info["node"]["local_packages"] = f"Error listing local packages: {str(e)}"
            else:
                js_info["node"]["local_packages"] = "No package.json found"
                js_info["node"]["missing_dependencies"] = "No package.json found"
            
            # Get npm configuration
            npm_config = subprocess.check_output(["npm", "config", "list", "--json"], text=True)
            js_info["node"]["npm_config"] = json.loads(npm_config)
        except Exception as e:
            js_info["node"]["error"] = f"Error getting Node.js information: {str(e)}"
        
        # macOS browser detection
        browsers = {
            "Chrome": "/Applications/Google Chrome.app",
            "Firefox": "/Applications/Firefox.app",
            "Safari": "/Applications/Safari.app",
            "Edge": "/Applications/Microsoft Edge.app"
        }
        
        for browser, path in browsers.items():
            if os.path.exists(path):
                version = None
                if browser == "Chrome":
                    try:
                        result = subprocess.check_output(
                            [f"{path}/Contents/MacOS/Google Chrome", "--version"],
                            text=True
                        ).strip()
                        version = result.split()[-1]
                    except:
                        pass
                elif browser == "Safari":
                    try:
                        result = subprocess.check_output(
                            ["defaults", "read", f"{path}/Contents/Info.plist", "CFBundleShortVersionString"],
                            text=True
                        ).strip()
                        version = result
                    except:
                        pass
                
                js_info["browsers"][browser] = {
                    "installed": True,
                    "path": path,
                    "version": version
                }
            else:
                js_info["browsers"][browser] = {
                    "installed": False
                }
        
        return js_info
    except Exception as e:
        return f"Error getting JavaScript debug info: {str(e)}"

def main():
    logger = setup_logging()
    logger.info("Starting system information collection")

    try:
        import psutil
    except ImportError:
        logger.error("Failed to import psutil module")
        sys.exit("Error: The 'psutil' module is required. Install it with 'pip install psutil'.")

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