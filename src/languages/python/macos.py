import sys
import os
import site
import subprocess
import json

def get_python_debug_info():
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