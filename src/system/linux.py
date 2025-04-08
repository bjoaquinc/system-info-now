import platform
import psutil
import subprocess
import json
import logging
import os
import datetime
import getpass
import re
from pathlib import Path

def get_os_info():
    if platform.system() != 'Linux':
        raise SystemError("This module is designed for Linux systems only!")
    
    result = {
        "name": platform.system(),
        "kernel": platform.release(),
        "architecture": platform.machine()
    }
    
    fields_to_populate = [
        "chassis", "distribution", "based_on", "build_id", 
        "hostname", "machine_id", "boot_id"
    ]
    
    for field in fields_to_populate:
        result[field] = "Unknown"
    
    try:
        hostnamectl = subprocess.run(
            ['hostnamectl', 'status'], 
            capture_output=True, text=True, check=True
        )
        
        if hostnamectl.returncode == 0:
            for line in hostnamectl.stdout.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if key == 'operating_system':
                        result["distribution"] = value
                    elif key == 'kernel':
                        result["kernel"] = value
                    elif key == 'architecture':
                        result["architecture"] = value
                    elif key == 'static_hostname':
                        result["hostname"] = value
                    elif key == 'chassis':
                        result["chassis"] = value
                    elif key == 'machine_id':
                        result["machine_id"] = value
                    elif key == 'boot_id':
                        result["boot_id"] = value
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    try:
        os_release = {}
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_release[key] = value.strip('"')
        
        if 'NAME' in os_release and result["distribution"] == "Unknown":
            result["distribution"] = os_release['NAME']
        
        if 'VERSION_ID' in os_release:
            result["version"] = os_release['VERSION_ID']
        
        if 'ID_LIKE' in os_release:
            result["based_on"] = os_release['ID_LIKE']
        
        if 'BUILD_ID' in os_release:
            result["build_id"] = os_release['BUILD_ID']
            
    except Exception as e:
        logging.error(f"Error getting OS info from /etc/os-release: {str(e)}")
    
    ordered_result = {
        "chassis": result.get("chassis", "Unknown"),
        "name": result.get("name", "Unknown"),
        "distribution": result.get("distribution", "Unknown"),
        "based_on": result.get("based_on", "Unknown"),
        "build_id": result.get("build_id", "Unknown"),
        "hostname": result.get("hostname", "Unknown"),
        "kernel": result.get("kernel", "Unknown"),
        "architecture": result.get("architecture", "Unknown"),
        "machine_id": result.get("machine_id", "Unknown"),
        "boot_id": result.get("boot_id", "Unknown")
    }
    
    return ordered_result

def get_motherboard_info():
    """Get information about the motherboard/hardware."""
    result = {
        "hardware_vendor": "Unknown",
        "hardware_model": "Unknown",
        "firmware_version": "Unknown",
        "firmware_date": "Unknown"
    }
    
    try:
        hostnamectl = subprocess.run(
            ['hostnamectl', 'status'], 
            capture_output=True, text=True, check=True
        )
        
        if hostnamectl.returncode == 0:
            for line in hostnamectl.stdout.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if key == 'hardware_vendor':
                        result["hardware_vendor"] = value
                    elif key == 'hardware_model':
                        result["hardware_model"] = value
                    elif key == 'firmware_version':
                        result["firmware_version"] = value
                    elif key == 'firmware_date':
                        result["firmware_date"] = value
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
        
    if result["hardware_vendor"] == "Unknown" or result["hardware_model"] == "Unknown":
        try:
            if os.path.exists('/sys/class/dmi/id/board_vendor'):
                with open('/sys/class/dmi/id/board_vendor', 'r') as f:
                    result["hardware_vendor"] = f.read().strip()
                    
            if os.path.exists('/sys/class/dmi/id/board_name'):
                with open('/sys/class/dmi/id/board_name', 'r') as f:
                    result["hardware_model"] = f.read().strip()
                    
            if os.path.exists('/sys/class/dmi/id/bios_version'):
                with open('/sys/class/dmi/id/bios_version', 'r') as f:
                    result["firmware_version"] = f.read().strip()
                    
            if os.path.exists('/sys/class/dmi/id/bios_date'):
                with open('/sys/class/dmi/id/bios_date', 'r') as f:
                    result["firmware_date"] = f.read().strip()
        except Exception as e:
            logging.error(f"Error getting motherboard info from DMI: {str(e)}")
            
    return result

def get_cpu_info():
    """Get detailed CPU information focusing on the most useful data for humans."""
    result = {
        "model": "Unknown",
        "architecture": "Unknown",
        "vendor": "Unknown",
        "cores_physical": None,
        "cores_logical": None,
        "sockets": None,
        "threads_per_core": None,
        "max_frequency": "Unknown",
        "min_frequency": "Unknown",
        "cache": {},
        "virtualization": "Unknown"
    }
    
    try:
        lscpu = subprocess.run(['lscpu'], capture_output=True, text=True, check=True)
        
        if lscpu.returncode == 0:
            lscpu_output = lscpu.stdout.strip().split('\n')
            
            for line in lscpu_output:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Model name':
                        result["model"] = value
                    elif key == 'Architecture':
                        result["architecture"] = value
                    elif key == 'Vendor ID':
                        result["vendor"] = value
                    elif key == 'CPU(s)':
                        result["cores_logical"] = int(value) if value.isdigit() else None
                    elif key == 'Core(s) per socket':
                        cores_per_socket = int(value) if value.isdigit() else None
                        if cores_per_socket and result.get("sockets"):
                            result["cores_physical"] = cores_per_socket * result["sockets"]
                    elif key == 'Socket(s)':
                        result["sockets"] = int(value) if value.isdigit() else None
                        if value.isdigit() and "cores_per_socket" in locals():
                            result["cores_physical"] = cores_per_socket * int(value)
                    elif key == 'Thread(s) per core':
                        result["threads_per_core"] = int(value) if value.isdigit() else None
                    elif key == 'CPU max MHz':
                        result["max_frequency"] = f"{value} MHz"
                    elif key == 'CPU min MHz':
                        result["min_frequency"] = f"{value} MHz"
                    elif key.startswith('L1') or key.startswith('L2') or key.startswith('L3'):
                        if 'Caches' not in result:
                            result["cache"] = {}
                        cache_level = key.split()[0]
                        result["cache"][cache_level] = value
                    elif key == 'Virtualization':
                        result["virtualization"] = value
            
            if result["cores_physical"] is None:
                result["cores_physical"] = psutil.cpu_count(logical=False)
            
            if result["cores_logical"] is None:
                result["cores_logical"] = psutil.cpu_count(logical=True)
                
            return result
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logging.error(f"Error getting CPU info from lscpu: {str(e)}")
    
    try:
        cpu_model = "Unknown"
        physical_cores = set()
        with open('/proc/cpuinfo', 'r') as f:
            current_processor = None
            for line in f:
                line = line.strip()
                if line.startswith('processor'):
                    current_processor = line.split(':', 1)[1].strip()
                elif line.startswith('model name') and cpu_model == "Unknown":
                    cpu_model = line.split(':', 1)[1].strip()
                elif line.startswith('physical id') and current_processor:
                    physical_id = line.split(':', 1)[1].strip()
                    core_id = None
                elif line.startswith('core id') and current_processor:
                    core_id = line.split(':', 1)[1].strip()
                    if physical_id is not None and core_id is not None:
                        physical_cores.add((physical_id, core_id))
        
        result["model"] = cpu_model
        result["cores_physical"] = len(physical_cores) or psutil.cpu_count(logical=False)
        result["cores_logical"] = psutil.cpu_count(logical=True)
        
        return result
    except Exception as e:
        logging.error(f"Error getting CPU info from /proc/cpuinfo: {str(e)}")
        
        return {
            "model": "Unknown",
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True)
        }

def get_gpu_info():
    """Get comprehensive GPU information from multiple sources."""
    try:
        gpus = []
        gpu_ids = set()  # To avoid duplicate entries
        
        try:
            nvidia_smi = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,driver_version,memory.total,compute_mode', 
                 '--format=csv,noheader'],
                capture_output=True, text=True, check=True
            )
            if nvidia_smi.returncode == 0:
                for line in nvidia_smi.stdout.strip().split('\n'):
                    if line.strip():
                        parts = [part.strip() for part in line.split(',')]
                        if len(parts) >= 3:
                            gpu_info = {
                                'name': parts[0],
                                'type': 'NVIDIA',
                                'driver_version': parts[1] if len(parts) > 1 else 'Unknown',
                                'memory': parts[2] if len(parts) > 2 else 'Unknown',
                                'compute_mode': parts[3] if len(parts) > 3 else 'Unknown',
                                'source': 'nvidia-smi'
                            }

                            gpus.append(gpu_info)
                            gpu_ids.add(parts[0])
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
        try:
            if os.path.exists('/sys/class/drm'):
                for card in os.listdir('/sys/class/drm'):
                    if card.startswith('card') and not card.endswith('dev'):
                        card_path = f'/sys/class/drm/{card}/device'
                        if os.path.exists(f'{card_path}/vendor'):
                            with open(f'{card_path}/vendor', 'r') as f:
                                vendor_id = f.read().strip()
                            
                            # AMD vendor ID is 0x1002
                            if vendor_id == '0x1002':
                                gpu_name = "AMD GPU"
                                if os.path.exists(f'{card_path}/product_name'):
                                    with open(f'{card_path}/product_name', 'r') as f:
                                        gpu_name = f.read().strip()
                                
                                if gpu_name not in gpu_ids:
                                    gpu_info = {
                                        'name': gpu_name,
                                        'type': 'AMD',
                                        'source': 'sysfs',
                                        'device_path': card_path
                                    }
                                    
                                    if os.path.exists(f'{card_path}/mem_info_vram_total'):
                                        try:
                                            with open(f'{card_path}/mem_info_vram_total', 'r') as f:
                                                mem_bytes = int(f.read().strip())
                                                gpu_info['memory'] = f"{mem_bytes / (1024**2):.0f} MiB"
                                        except (ValueError, IOError):
                                            pass
                                    
                                    gpus.append(gpu_info)
                                    gpu_ids.add(gpu_name)
        except Exception as e:
            logging.error(f"Error getting AMD GPU info: {str(e)}")
        
        try:
            glxinfo = subprocess.run(
                ['glxinfo'], 
                capture_output=True, text=True, check=True
            )
            
            if glxinfo.returncode == 0:
                opengl_info = {}
                
                opengl_pattern = re.compile(r'^OpenGL ([^:]+):\s*(.+)$')
                for line in glxinfo.stdout.split('\n'):
                    match = opengl_pattern.match(line.strip())
                    if match:
                        key, value = match.groups()
                        opengl_info[key.strip()] = value.strip()
                
                if opengl_info and 'renderer string' in opengl_info:
                    renderer = opengl_info['renderer string']
                    found_match = False
                    
                    for gpu in gpus:
                        if gpu['name'] in renderer or ('type' in gpu and gpu['type'] in renderer):
                            gpu['opengl'] = {
                                'renderer': renderer,
                                'version': opengl_info.get('version string', 'Unknown'),
                                'vendor': opengl_info.get('vendor string', 'Unknown')
                            }
                            found_match = True
                            break
                    
                    if not found_match and 'vendor string' in opengl_info:
                        vendor = opengl_info['vendor string']
                        gpu_type = 'Unknown'
                        
                        if 'NVIDIA' in vendor:
                            gpu_type = 'NVIDIA'
                        elif 'AMD' in vendor or 'ATI' in vendor:
                            gpu_type = 'AMD'
                        elif 'Intel' in vendor:
                            gpu_type = 'Intel'
                        
                        opengl_gpu = {
                            'name': renderer,
                            'type': gpu_type,
                            'source': 'glxinfo',
                            'opengl': {
                                'renderer': renderer,
                                'version': opengl_info.get('version string', 'Unknown'),
                                'vendor': opengl_info.get('vendor string', 'Unknown')
                            }
                        }
                        
                        if renderer not in gpu_ids:
                            gpus.append(opengl_gpu)
                            gpu_ids.add(renderer)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        if not gpus or len(gpus) < 1:
            try:
                lspci = subprocess.run(
                    ['lspci', '-v'], 
                    capture_output=True, text=True, check=True
                )
                
                if lspci.returncode == 0:
                    gpu_regex = re.compile(r'([0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f])\s+(VGA compatible controller|3D controller):\s*(.*)')
                    matches = gpu_regex.findall(lspci.stdout)
                    
                    for match in matches:
                        pci_id, controller_type, description = match
                        if description not in gpu_ids:
                            gpu_type = 'Unknown'
                            if 'NVIDIA' in description:
                                gpu_type = 'NVIDIA'
                            elif 'AMD' in description or 'ATI' in description:
                                gpu_type = 'AMD'
                            elif 'Intel' in description:
                                gpu_type = 'Intel'
                            
                            gpu_info = {
                                'name': description.strip(),
                                'type': gpu_type,
                                'controller_type': controller_type,
                                'pci_id': pci_id,
                                'source': 'lspci'
                            }
                            gpus.append(gpu_info)
                            gpu_ids.add(description)
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        
        # Return prioritizing NVIDIA & AMD dedicated GPUs
        sorted_gpus = sorted(gpus, key=lambda g: 0 if g.get('type') == 'NVIDIA' else 
                                              (1 if g.get('type') == 'AMD' else 2))
        
        return sorted_gpus if sorted_gpus else None
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
    """Get comprehensive disk and filesystem information in a human-readable format."""
    result = {
        "human_readable": {
            "system_disks": [],
            "removable_disks": [],
            "virtual_disks": [],
        },
        "raw_data": {
            "physical_disks": [],
            "filesystems": {},
        }
    }
    
    try:
        lsblk_json = subprocess.run(
            ['lsblk', '-o', 'NAME,MAJ:MIN,RM,SIZE,RO,TYPE,MOUNTPOINTS', '--json'],
            capture_output=True, text=True
        )
        
        if lsblk_json.returncode == 0:
            try:
                lsblk_data = json.loads(lsblk_json.stdout)
                result["raw_data"]["physical_disks"] = lsblk_data.get("blockdevices", [])
                
                for device in lsblk_data.get("blockdevices", []):
                    if device.get("type") == "loop" and "snap" in str(device.get("mountpoints", [])):
                        continue
                    
                    simplified_device = {
                        "name": device.get("name", "Unknown"),
                        "size": device.get("size", "Unknown"),
                        "type": device.get("type", "Unknown"),
                        "partitions": [],
                        "mountpoints": device.get("mountpoints", [])
                    }
                    
                    for child in device.get("children", []):
                        partition = {
                            "name": child.get("name", "Unknown"),
                            "size": child.get("size", "Unknown"),
                            "mountpoints": child.get("mountpoints", []),
                            "usage": "Unknown" 
                        }
                        simplified_device["partitions"].append(partition)
                    
                    if device.get("type") == "disk":
                        if device.get("rm") == True:
                            result["human_readable"]["removable_disks"].append(simplified_device)
                        elif device.get("name").startswith(("sd", "nvme", "hd")):
                            result["human_readable"]["system_disks"].append(simplified_device)
                        else:
                            result["human_readable"]["virtual_disks"].append(simplified_device)
                
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing lsblk JSON output: {str(e)}")
                lsblk = subprocess.run(
                    ['lsblk', '-o', 'NAME,MAJ:MIN,RM,SIZE,RO,TYPE,MOUNTPOINTS'],
                    capture_output=True, text=True, check=True
                )
                
                if lsblk.returncode == 0:
                    result["raw_data"]["physical_disks"] = _parse_lsblk_output(lsblk.stdout)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logging.error(f"Error getting disk info with lsblk: {str(e)}")
    
    try:
        df = subprocess.run(
            ['df', '-h'],
            capture_output=True, text=True, check=True
        )
        
        if df.returncode == 0:
            filesystems = _parse_df_output(df.stdout)
            
            real_filesystems = []
            for fs in filesystems:
                if (fs.get("filesystem", "").startswith("/dev/") and 
                    not any(snap in fs.get("mounted_on", "") for snap in ["/snap", "/var/lib/snapd"])):
                    real_filesystems.append(fs)
                    
            result["human_readable"]["filesystems"] = real_filesystems
            
            for fs in filesystems:
                mountpoint = fs.get("mounted_on", "")
                if mountpoint:
                    result["raw_data"]["filesystems"][mountpoint] = fs
            
            for disk_category in ["system_disks", "removable_disks", "virtual_disks"]:
                for disk in result["human_readable"][disk_category]:
                    for partition in disk["partitions"]:
                        for fs in filesystems:
                            if fs.get("filesystem", "").endswith(partition["name"]):
                                partition["usage"] = {
                                    "used": fs.get("used", "Unknown"),
                                    "available": fs.get("avail", "Unknown"),
                                    "percent": fs.get("use%", "Unknown")
                                }
            
            for fs in real_filesystems:
                try:
                    size_str = fs.get("size", "0").rstrip("GMKBiT")
                    used_str = fs.get("used", "0").rstrip("GMKBiT")
                    
                    size_unit = next((c for c in reversed(fs.get("size", "0")) if c.isalpha()), "B")
                    used_unit = next((c for c in reversed(fs.get("used", "0")) if c.isalpha()), "B")
                    
                    multiplier = {
                        'B': 1,
                        'K': 1024,
                        'M': 1024**2,
                        'G': 1024**3,
                        'T': 1024**4
                    }
                    
                    size_mult = multiplier.get(size_unit, 1)
                    used_mult = multiplier.get(used_unit, 1)
                    
                    total_space += float(size_str) * size_mult
                    used_space += float(used_str) * used_mult
                except (ValueError, IndexError):
                    pass
            
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logging.error(f"Error getting filesystem info with df: {str(e)}")
    
    if (not result["raw_data"]["physical_disks"] and 
        not result["raw_data"]["filesystems"] and
        result["human_readable"]["total_storage"] == "Unknown"):
        try:
            partitions = psutil.disk_partitions(all=False)
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result["raw_data"]["filesystems"][partition.mountpoint] = {
                        "filesystem": partition.device,
                        "type": partition.fstype,
                        "size": _format_size(usage.total),
                        "used": _format_size(usage.used),
                        "available": _format_size(usage.free),
                        "use_percent": f"{usage.percent}%",
                        "mounted_on": partition.mountpoint
                    }
                except (PermissionError, OSError):
                    continue
            
            system_disks = {}
            for partition in partitions:
                if not partition.device.startswith("/dev/"):
                    continue
                
                # Extract disk name from partition (e.g., sda from /dev/sda1)
                disk_name = re.sub(r'\d+$', '', partition.device.split('/')[-1])
                
                if disk_name not in system_disks:
                    system_disks[disk_name] = {
                        "name": disk_name,
                        "partitions": [],
                        "mountpoints": []
                    }
                
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    system_disks[disk_name]["partitions"].append({
                        "name": partition.device.split('/')[-1],
                        "mountpoints": [partition.mountpoint],
                        "usage": {
                            "used": _format_size(usage.used),
                            "available": _format_size(usage.free),
                            "percent": f"{usage.percent}%"
                        }
                    })
                except (PermissionError, OSError):
                    continue
            
            result["human_readable"]["system_disks"] = list(system_disks.values())
            
            try:
                root_usage = psutil.disk_usage('/')
                result["human_readable"]["total_storage"] = _format_size(root_usage.total)
                result["human_readable"]["used_storage"] = _format_size(root_usage.used)
                result["human_readable"]["free_storage"] = _format_size(root_usage.free)
                result["human_readable"]["usage_percent"] = f"{root_usage.percent}%"
            except (PermissionError, OSError):
                pass
                
        except Exception as e:
            logging.error(f"Error getting disk info with psutil: {str(e)}")
    
    return result["human_readable"]

def _parse_lsblk_output(output):
    """Parse lsblk text output when JSON format is not available."""
    lines = output.strip().split('\n')
    if len(lines) <= 1:
        return []
    
    header = lines[0].split()
    lines = lines[1:]
    
    disks = []
    current_disk = None
    current_part = None
    
    for line in lines:
        indent = len(line) - len(line.lstrip())
        line = line.strip()
        
        if not line:
            continue
            
        parts = []
        in_quotes = False
        current_part = ""
        
        for char in line:
            if char == '"' and not in_quotes:
                in_quotes = True
            elif char == '"' and in_quotes:
                in_quotes = False
            elif char.isspace() and not in_quotes:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
                
        if current_part:
            parts.append(current_part)
        
        device_info = {}
        for i, col_name in enumerate(header):
            if i < len(parts):
                device_info[col_name.lower()] = parts[i]
        
        if indent == 0:
            device_info["children"] = []
            disks.append(device_info)
            current_disk = device_info
            current_part = None
        elif indent == 2 and current_disk:
            device_info["children"] = []
            current_disk["children"].append(device_info)
            current_part = device_info
        elif indent == 4 and current_part:
            current_part["children"].append(device_info)
    
    return disks

def _parse_df_output(output):
    """Parse df -h output to get filesystem information."""
    lines = output.strip().split('\n')
    if len(lines) < 2:
        return []
    
    header = lines[0].split()
    filesystems = []
    
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < len(header):
            continue
            
        fs_info = {}
        
        # Handle case where mountpoint has spaces
        if len(parts) > len(header):
            mountpoint_index = len(header) - 1
            fs_info[header[-1].lower()] = " ".join(parts[mountpoint_index:])
            parts = parts[:mountpoint_index] + [fs_info[header[-1].lower()]]
        
        for i, col_name in enumerate(header):
            if i < len(parts):
                fs_info[col_name.lower()] = parts[i]
                
        filesystems.append(fs_info)
    
    return filesystems

def _format_size(size_bytes):
    """Format byte size into human readable format."""
    if size_bytes < 0:
        return "0B"
        
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
    size = float(size_bytes)
    
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == 'B':
                return f"{int(size)}{unit}"
            return f"{size:.2f}{unit}"
        size /= 1024

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
    """Check if the current user has root privileges on Linux."""
    try:
        return os.geteuid() == 0
    except Exception as e:
        logging.error(f"Error checking admin status: {str(e)}")
        return False

def get_user_info():
    return {
        "user": getpass.getuser(),
        "is_admin": get_is_admin(),
        "groups": get_user_groups()
    }

def get_user_groups():
    """Get the groups the current user belongs to."""
    try:
        username = getpass.getuser()
        process = subprocess.run(['groups', username], capture_output=True, text=True)
        if process.returncode == 0:
            output = process.stdout.strip()
            if ':' in output:
                groups = output.split(':', 1)[1].strip().split()
                return groups
        return []
    except Exception as e:
        logging.error(f"Error getting user groups: {str(e)}")
        return []

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