import subprocess
import json
import os
import shutil
from pathlib import Path

def get_javascript_debug_info(project_root):
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
        
        # Update path references to use project_root
        package_json_path = project_root / 'package.json'
        node_modules_path = project_root / 'node_modules'

        # Check Node.js installation
        try:
            if shutil.which('node'):
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
                if package_json_path.exists():
                    # Read package.json
                    with open(package_json_path, 'r') as f:
                        package_json = json.load(f)
                    
                    # Update the npm list command to run from project root
                    try:
                        local_packages = subprocess.check_output(
                            ["npm", "list", "--json"],
                            text=True,
                            cwd=str(project_root)
                        )
                        js_info["node"]["local_packages"] = json.loads(local_packages)
                        
                        # Check for missing dependencies
                        missing_deps = []
                        required_deps = {
                            **package_json.get('dependencies', {}),
                            **package_json.get('devDependencies', {})
                        }
                        
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
        
        # Linux browser detection
        browsers = {
            "Chrome": ["google-chrome", "google-chrome-stable"],
            "Firefox": ["firefox"],
            "Chromium": ["chromium-browser", "chromium"],
            "Opera": ["opera"],
            "Cachy Browser": ["cachy-browser"],
            "Brave": ["brave-browser"],
            "Vivaldi": ["vivaldi"],
            "LibreWolf": ["librewolf"],
            "Tor Browser": ["torbrowser-launcher"],
            "Mullvad Browser": ["mullvad-browser"]
        }
        
        for browser, commands in browsers.items():
            installed = False
            version = None
            path = None
            
            for cmd in commands:
                cmd_path = shutil.which(cmd)
                if cmd_path:
                    installed = True
                    path = cmd_path
                    try:
                        if browser == "Chrome" or browser == "Chromium":
                            version_output = subprocess.check_output([cmd_path, "--version"], text=True).strip()
                            version = version_output
                        elif browser == "Firefox":
                            version_output = subprocess.check_output([cmd_path, "--version"], text=True).strip()
                            version = version_output
                        elif browser == "Opera":
                            version_output = subprocess.check_output([cmd_path, "--version"], text=True).strip()
                            version = version_output
                        elif browser == "Cachy Browser":
                            version_output = subprocess.check_output([cmd_path, "--version"], text=True).strip()
                            version = version_output
                        elif browser == "Brave":
                            version_output = subprocess.check_output([cmd_path, "--version"], text=True).strip()
                            version = version_output
                        elif browser == "Vivaldi":
                            version_output = subprocess.check_output([cmd_path, "--version"], text=True).strip()
                            version = version_output
                        elif browser == "LibreWolf":
                            version_output = subprocess.check_output([cmd_path, "--version"], text=True).strip()
                            version = version_output
                        elif browser == "Mullvad Browser":
                            version_output = subprocess.check_output([cmd_path, "--version"], text=True).strip()
                            version = version_output
                        elif browser == "Tor Browser":
                            version_output = subprocess.check_output([cmd_path, "--settings"], text=True).strip()
                            for line in version_output.splitlines():
                                if line.strip().startswith("version "):
                                    version = line.strip()
                                    break
                    except:
                        pass
                    break
            
            js_info["browsers"][browser] = {
                "installed": installed,
                "path": path,
                "version": version
            }
        
        return js_info
    except Exception as e:
        return f"Error getting JavaScript debug info: {str(e)}"
