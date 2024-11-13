import subprocess
import time
import psutil
import logging
import requests
import os
import platform

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

JAVA_PATH = "/usr/bin/java"  # Default Java path, adjust if needed
SERVER_PORT = 25565  # Default Minecraft server port
SERVER_JAR = "server.jar"  # Default server jar file name

def install_java(java_version):
    """Install the specified Java version."""
    logger.info(f"Checking Java {java_version} installation...")
    if platform.system() == "Linux":
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", f"openjdk-{java_version}-jdk", "-y"], check=True)
            logger.info(f"Java {java_version} installed successfully.")
        except subprocess.CalledProcessError:
            logger.error(f"Failed to install Java {java_version}. Please install it manually.")
            exit(1)
    elif platform.system() == "Windows":
        try:
            subprocess.run(["winget", "install", f"AdoptOpenJDK.{java_version}"], check=True)
            logger.info(f"Java {java_version} installed successfully.")
        except subprocess.CalledProcessError:
            logger.warning(f"Failed to install Java {java_version} using winget. Please install it manually from https://adoptopenjdk.net/")
            exit(1)
    else:
        logger.error("Unsupported operating system for Java installation.")
        exit(1)

def download_server_jar(distribution, version):
    """Download the server jar file for the specified distribution and version."""
    logger.info(f"Starting download for {distribution} version {version}...")
    
    if distribution == "vanilla":
        url = f"https://launcher.mojang.com/v1/objects/{version}/server.jar"
    elif distribution == "paper":
        version_info_url = f"https://papermc.io/api/v2/projects/paper/versions/{version}"
        try:
            response = requests.get(version_info_url)
            response.raise_for_status()
            version_info = response.json()
            latest_build = version_info["builds"][-1]
            url = f"https://papermc.io/api/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
            logger.info(f"Latest build for Paper {version}: Build {latest_build}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching build info for version {version}: {e}")
            exit(1)
    else:
        raise ValueError("Invalid distribution")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("Content-Length", 0))
        with open(SERVER_JAR, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("Download complete.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading server JAR: {e}")
        exit(1)

def configure_server_properties():
    """Configure server properties and accept the EULA."""
    logger.info("Configuring server properties...")
    with open("server.properties", "w") as f:
        f.write(f"server-ip=0.0.0.0\nserver-port={SERVER_PORT}\n")
    with open("eula.txt", "w") as f:
        f.write("eula=true\n")
    logger.info("Server properties and EULA configured.")

def check_playit_installed():
    """Check if Playit.gg is installed, and install if not."""
    logger.info("Checking if Playit.gg is installed...")
    try:
        subprocess.run(["playit", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("Playit.gg is already installed.")
    except FileNotFoundError:
        logger.error("Playit.gg is not installed. Attempting to install it...")
        install_playit()
    except subprocess.CalledProcessError:
        logger.error("An error occurred while checking Playit.gg version.")
        install_playit()

def install_playit():
    """Install Playit.gg using the PPA method (for Ubuntu/Debian)."""
    try:
        # Add the Playit PPA key
        subprocess.run("curl -SsL https://playit-cloud.github.io/ppa/key.gpg | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/playit.gpg >/dev/null", shell=True, check=True)
        
        # Add Playit repository
        subprocess.run('echo "deb [signed-by=/etc/apt/trusted.gpg.d/playit.gpg] https://playit-cloud.github.io/ppa/data ./" | sudo tee /etc/apt/sources.list.d/playit-cloud.list', shell=True, check=True)

        # Update package list
        subprocess.run("sudo apt update", shell=True, check=True)
        
        # Install Playit.gg
        subprocess.run("sudo apt install playit", shell=True, check=True)
        
        logger.info("Playit.gg installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing Playit.gg: {e}")
        exit(1)

def start_server(memory_limit):
    """Start the Minecraft server with specified memory allocation."""
    logger.info(f"Starting the Minecraft server with {memory_limit}GB of RAM...")
    try:
        # Start the server and capture its output in real-time
        minecraft_process = subprocess.Popen(
            [JAVA_PATH, f"-Xmx{memory_limit}G", f"-Xms{memory_limit}G", "-jar", SERVER_JAR],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        # Continuously print the server's output
        for line in minecraft_process.stdout:
            print(line, end="")  # Print each line from the server's output
        
        logger.info("Minecraft server started successfully.")
        return minecraft_process
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting the server: {e}")
        exit(1)


def start_playit():
    """Start Playit.gg tunnel."""
    logger.info("Starting Playit.gg tunnel...")
    try:
        playit_process = subprocess.Popen(["playit"])
        logger.info("Playit.gg tunnel started successfully.")
        return playit_process
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting Playit.gg tunnel: {e}")
        exit(1)

def stop_process(process):
    """Forcefully stop a process."""
    try:
        if process and psutil.pid_exists(process.pid):
            p = psutil.Process(process.pid)
            p.terminate()
            logger.info(f"Terminating process with PID {process.pid}...")
            p.wait(timeout=10)  # Wait for the process to terminate
            if p.is_running():
                logger.warning(f"Process {process.pid} did not stop, killing it forcefully.")
                p.kill()  # Force kill the process if it's still running
            else:
                logger.info(f"Process with PID {process.pid} stopped successfully.")
        else:
            logger.warning(f"No process found with PID {process.pid}")
    except psutil.NoSuchProcess:
        logger.warning(f"Process with PID {process.pid} does not exist.")
    except psutil.AccessDenied:
        logger.error(f"Access denied when trying to terminate process {process.pid}.")
    except psutil.TimeoutExpired:
        logger.error(f"Timeout expired while trying to stop process {process.pid}.")

def main():
    """Main menu for managing the server."""
    playit_process = None
    minecraft_process = None

    while True:
        print("\n=== Minecraft Server Manager ===")
        print("1. Install and Configure Server")
        print("2. Start Server")
        print("3. Start Playit.gg Tunnel")  # Start only Playit.gg
        print("4. Stop Server and Playit.gg Tunnel")
        print("5. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            distribution = input("Enter desired distribution (vanilla/paper): ").strip().lower()
            version = input("Enter desired version: ").strip()
            memory = psutil.virtual_memory().total / (1024 ** 3)
            memory_limit = int(memory * 0.75)
            java_version = "17"
            install_java(java_version)
            download_server_jar(distribution, version)
            configure_server_properties()
            logger.info("Server setup complete!")
        elif choice == "2":
            memory = psutil.virtual_memory().total / (1024 ** 3)
            memory_limit = int(memory * 0.75)
            minecraft_process = start_server(memory_limit)
            
            # Wait for the server to finish (i.e., the user stops it)
            minecraft_process.wait()
            logger.info("Minecraft server has stopped.")
        elif choice == "3":
            check_playit_installed()  # Ensure Playit.gg is installed
            playit_process = start_playit()  # Start Playit.gg tunnel
        elif choice == "4":
            if playit_process:
                stop_process(playit_process)
            if minecraft_process:
                stop_process(minecraft_process)
            logger.info("Both server and Playit.gg tunnel stopped successfully.")
        elif choice == "5":
            logger.info("Exiting the Minecraft Server Manager. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
