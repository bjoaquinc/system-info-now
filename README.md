# system-info-now

A lightweight Python utility that aggregates and exports comprehensive system information to JSON, specifically designed for feeding system context into Large Language Models (LLMs).

## Description

system-info-now provides a snapshot of your system's current state in a standardized, easy-to-parse format. It gathers real-time data about your operating system, hardware, running processes, and environment variables, making it ideal for:
- System diagnostics
- Environment documentation
- Troubleshooting
- Providing contextual information to AI models and language models

By generating a detailed JSON output, the tool enables seamless integration of system context into AI-powered workflows, allowing LLMs to understand the specific environment and configuration details.

## ⚠️ IMPORTANT: Sensitive Data Warning

**CAUTION**: This tool collects comprehensive system information that may include:
- Environment variables
- Path details
- User information
- Potentially sensitive configuration data

🛡️ **ALWAYS REVIEW THE OUTPUT FILE BEFORE SHARING OR FEEDING TO ANY LLM**

## Features

### System Debug Data
- Operating system details and version
- CPU and GPU specifications
- Memory usage and statistics
- Disk utilization
- Network interface information
- Current running processes
- Git repository status
- System uptime and load averages
- Environment variables
- User information

### Language-Specific Debug Data
Currently supported (disabled by default):
- Python environment details
- JavaScript environment information

*More languages coming soon!*

### Operating System Support
Currently supported:
- macOS
- Linux

*Coming soon:*
- Windows


## Installation

1. Clone the repository:
```bash
git clone https://github.com/bjoaquinc/system-info-now.git
cd system-info-now
```

2. Install required dependencies:
```bash
pip install psutil pyyaml
```

## Usage

1. Basic usage:

Run the script from the project directory:
```bash
python main.py
```

2. Configuration (optional): Update the config.yaml file in the project root:

```yaml
# System Info Now Configuration File
output:
  format: json # Only json is currently supported
  directory: output
  filename: system_data.json

logging:
  level: INFO
  directory: logs

# Customizable root directory path for project 
# specific context gathering used by language 
# collectors
project:
  root_dir: "." # Default to current directory, can be set to absolute path

collectors:
  # Core system information - recommended to keep enabled
  system: true
  
  # Language-specific collectors - disabled by default
  # WARNING: When feeding data to LLMs, the complex structure with many versions, 
  # paths, and package details in these collectors may cause hallucinations.
  # Only enable if you specifically need this language data.
  python: false
  javascript: false
  
```

This will create an `output/system_data.json` file in your current directory.

## Requirements

- Python 3.x
- Mac OS or Linux (Working on supporting **Windows** soon)

## Output Example

```json
{
  "system_debug_data": {
    // ... system details including OS, CPU, GPU, memory, disk, network info
  },
  "python_debug_data": {
    // ... Python runtime information, paths, dependencies, and virtual environment details
  },
  "javascript_debug_data": {
    // ... Node.js version, global packages, installed browsers, and npm configuration
  }
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Plans

- Support more operating systems (Windows coming soon)
- Support more languages for debugging
- Support more useful data in existing languages

## Support

If you encounter any problems or have suggestions, please file an issue on the GitHub repository.

## Authors

- Joaquin Coromina (@bjoaquinc)
