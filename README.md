# Minecraft Server Manager

**Minecraft Server Manager** is a Python-based command-line tool designed to automate the setup, configuration, and management of Minecraft servers. With features like Java installation, downloading server files, and setting up Playit.gg tunnels, this tool simplifies the process of hosting a Minecraft server, whether you're a beginner or an experienced user.

## Key Features

- **Automated Java Installation**: Installs the required Java version (OpenJDK 17) on both Linux and Windows systems.
- **Server Setup**: Downloads the Minecraft server JAR (vanilla or Paper) and configures server properties automatically.
- **Playit.gg Tunnel Integration**: Ensures Playit.gg is installed and starts a secure tunnel for easy external access to the server.
- **Real-Time Server Management**: Start and monitor the server’s output directly from the terminal. Stop the server and tunnel with a single command.
- **Cross-Platform**: Supports both Linux and Windows, with platform-specific installation steps for Java and Playit.gg.

## Requirements

- Python 3.8 or higher
- `psutil` library (for managing processes)
- `requests` library (for downloading server files)

## Installation

To get started, clone the repository and install the required dependencies:

```bash
git clone https://github.com/OwaisSafa/minecraft-server-Setup-Tunnel.git
cd minecraft-server-Setup-Tunnel
pip install -r requirements.txt
```

## Usage

1. **Install and Configure Server**: Choose the Minecraft distribution (vanilla or Paper), specify the version, and the tool will handle Java installation, downloading the server JAR, and configuring server settings.
2. **Start Minecraft Server**: Launch the server with a specified memory allocation (default is 75% of your system's total memory).
3. **Start Playit.gg Tunnel**: Automatically check for Playit.gg and start a secure tunnel to make your server accessible remotely.
4. **Stop Server and Tunnel**: Stop both the Minecraft server and the Playit.gg tunnel at any time.
5. **Exit**: Quit the program safely.

## How to Run

Simply run the Python script:

```bash
python minecraft_server_manager.py
```

You’ll be presented with an interactive menu to manage your server.

## License

This project is licensed under the MIT License.
