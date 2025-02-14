# system-info-now

A lightweight Python utility that captures and exports comprehensive system information to JSON in one command.

## Description

system-info-now provides a snapshot of your system's current state in a standardized, easy-to-parse format. It gathers real-time data about your operating system, hardware, running processes, and environment variables, making it perfect for system diagnostics, environment documentation, and troubleshooting.

## Features

- Operating system details and version
- CPU specifications and core count
- Memory usage and statistics
- Disk utilization
- Network interface information
- Current running processes (top 10 by CPU usage)
- Git repository status (if in a repo)
- System uptime and load averages
- Environment variables
- User information
- Cross-platform support (Windows, Linux, macOS)
- JSON output for easy parsing and integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bjoaquinc/system-info-now.git
cd system-info-now
```

2. Install required dependencies:
```bash
pip install psutil
```

## Usage

Run the script from the project directory:
```bash
python system_info.py
```

This will create a `system_data.json` file in your current directory.

## Requirements

- Python 3.x
- psutil library

## Output Example

```json
{
  "os": {
    "name": "Darwin",
    "version": "21.6.0",
    "release": "21.6.0",
    "architecture": "arm64"
  },
  "cpu_info": {
    "processor": "arm",
    "cores": 8,
    "logical_processors": 8
  },
  "memory_info": {
    "total": 16000000000,
    "available": 8000000000,
    "used": 8000000000,
    "percent": 50.0
  }
  // ... additional system information
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Plans

- Command line arguments for customizing output
- Additional system metrics collection
- Export formats beyond JSON (YAML, CSV)
- Option to exclude sensitive information
- VS Code extension integration
- Package distribution via pip

## Support

If you encounter any problems or have suggestions, please file an issue on the GitHub repository.

## Authors

- Joaquin Coromina (@bjoaquinc)
