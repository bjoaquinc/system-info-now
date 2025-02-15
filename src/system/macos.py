import platform
import psutil
import subprocess
import json
import logging
import os
import datetime
import getpass

def get_os_info():
    if platform.system() != 'Darwin':
        raise SystemError("SORRY! We currently only support Mac OS but we will have Windows and Linux support soon!")
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
            "total_memory": f"{vm.total / (1024**3):.2f} GB",
            "available": f"{vm.available / (1024**3):.2f} GB",
            "percent_used": f"{vm.percent}%",
            "total_swap": f"{swap.total / (1024**3):.2f} GB",
            "swap_used": f"{swap.percent}%"
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

def get_env_vars():
    return dict(os.environ)

def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            info = proc.info
            if info['cpu_percent'] is None:
                info['cpu_percent'] = 0.0
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    processes = sorted(processes, key=lambda p: float(p.get('cpu_percent', 0)), reverse=True)[:10]
    return processes

def get_git_info():
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        return None

    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        return None

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