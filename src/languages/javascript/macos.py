import subprocess
import json
import os
from pathlib import Path

def get_javascript_debug_info():
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