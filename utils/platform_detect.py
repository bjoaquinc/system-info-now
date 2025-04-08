import platform

def get_platform():
    """
    Determines the current operating system platform.
    
    Returns:
        str: One of 'darwin' (macOS), 'linux', 'windows', or 'unknown'
    """
    system = platform.system().lower()
    
    if system == 'darwin':
        return 'darwin'
    elif system == 'linux':
        return 'linux'
    elif system == 'windows':
        return 'windows'
    else:
        return 'unknown'
