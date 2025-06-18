#!/usr/bin/env python3
"""
Grey Hat AI Installation Script for Kali Linux

This script automates the installation and setup of Grey Hat AI
on Kali Linux systems.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, check=True, shell=False):
    """Run a shell command and return the result."""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Error: {e.stderr}")
        if check:
            raise
        return e

def check_system_requirements():
    """Check if the system meets requirements."""
    logger.info("Checking system requirements...")
    
    # Check if running on Linux
    if sys.platform != "linux":
        logger.error("This installer is designed for Linux systems (specifically Kali Linux)")
        return False
    
    # Check Python version
    if sys.version_info < (3, 9):
        logger.error("Python 3.9 or higher is required")
        return False
    
    logger.info("✅ System requirements met")
    return True

def install_system_dependencies():
    """Install system-level dependencies."""
    logger.info("Installing system dependencies...")
    
    # Update package list
    logger.info("Updating package list...")
    run_command("sudo apt update")
    
    # Install required system packages
    packages = [
        "python3-pip",
        "python3-venv",
        "python3-dev",
        "build-essential",
        "portaudio19-dev",
        "libasound2-dev",
        "libsndfile1-dev",
        "ffmpeg",
        "git",
        "curl",
        "wget"
    ]
    
    logger.info("Installing system packages...")
    for package in packages:
        logger.info(f"Installing {package}...")
        result = run_command(f"sudo apt install -y {package}", check=False)
        if result.returncode != 0:
            logger.warning(f"Failed to install {package}, continuing...")
    
    logger.info("✅ System dependencies installed")

def install_playwright():
    """Install Playwright and its browsers."""
    logger.info("Installing Playwright browsers...")
    
    try:
        # Install playwright browsers
        run_command("python3 -m playwright install chromium")
        run_command("python3 -m playwright install-deps chromium")
        logger.info("✅ Playwright browsers installed")
    except subprocess.CalledProcessError:
        logger.warning("⚠️ Playwright browser installation failed, continuing...")

def create_virtual_environment():
    """Create and activate virtual environment."""
    logger.info("Creating virtual environment...")
    
    venv_path = Path.home() / "grey_hat_ai_venv"
    
    # Create virtual environment
    run_command(f"python3 -m venv {venv_path}")
    
    # Get activation script path
    activate_script = venv_path / "bin" / "activate"
    
    logger.info(f"✅ Virtual environment created at {venv_path}")
    return venv_path, activate_script

def install_python_dependencies(venv_path):
    """Install Python dependencies in virtual environment."""
    logger.info("Installing Python dependencies...")
    
    pip_path = venv_path / "bin" / "pip"
    
    # Upgrade pip
    run_command(f"{pip_path} install --upgrade pip")
    
    # Install the package in development mode
    run_command(f"{pip_path} install -e .")
    
    logger.info("✅ Python dependencies installed")

def create_launcher_script(venv_path):
    """Create a launcher script for Grey Hat AI."""
    logger.info("Creating launcher script...")
    
    launcher_content = f"""#!/bin/bash
# Grey Hat AI Launcher Script

# Activate virtual environment
source {venv_path}/bin/activate

# Set environment variables
export PYTHONPATH="{os.getcwd()}:$PYTHONPATH"

# Launch Grey Hat AI
echo "🎯 Starting Grey Hat AI..."
echo "Open your browser and navigate to the URL shown below:"
echo ""

streamlit run grey_hat_ai/app.py --server.port 8501 --server.address 0.0.0.0

# Deactivate virtual environment on exit
deactivate
"""
    
    launcher_path = Path(os.getcwd()) / "launch_grey_hat_ai.sh"
    
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    # Make executable
    os.chmod(launcher_path, 0o755)
    
    logger.info(f"✅ Launcher script created at {launcher_path}")
    return launcher_path

def create_desktop_entry(launcher_path):
    """Create a desktop entry for Grey Hat AI."""
    logger.info("Creating desktop entry...")
    
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Grey Hat AI
Comment=Advanced Cybersecurity AI Framework
Exec={launcher_path}
Icon=applications-security
Terminal=true
Categories=Security;Network;
"""
    
    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_path = desktop_dir / "grey-hat-ai.desktop"
    
    with open(desktop_path, "w") as f:
        f.write(desktop_content)
    
    # Make executable
    os.chmod(desktop_path, 0o755)
    
    logger.info(f"✅ Desktop entry created at {desktop_path}")

def setup_configuration():
    """Set up configuration directory and files."""
    logger.info("Setting up configuration...")
    
    config_dir = Path.home() / ".grey_hat_ai"
    config_dir.mkdir(exist_ok=True)
    
    # Create example configuration file
    config_content = """# Grey Hat AI Configuration
# 
# This file contains example configuration settings.
# You can set API keys here, but it's recommended to use the GUI instead.

# Example API key settings (uncomment and fill in your keys):
# GOOGLE_GEMINI_API_KEY=your_gemini_key_here
# MISTRAL_API_KEY=your_mistral_key_here
# GROQ_API_KEY=your_groq_key_here
# ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Voice settings
WHISPER_MODEL_SIZE=base
SAMPLE_RATE=16000

# Web agent settings
BROWSER_TYPE=chromium
HEADLESS=true
"""
    
    config_path = config_dir / "config.env"
    
    if not config_path.exists():
        with open(config_path, "w") as f:
            f.write(config_content)
    
    logger.info(f"✅ Configuration directory created at {config_dir}")

def print_installation_summary(launcher_path, venv_path):
    """Print installation summary and usage instructions."""
    print("\n" + "="*60)
    print("🎯 GREY HAT AI INSTALLATION COMPLETE!")
    print("="*60)
    print()
    print("📁 Installation Details:")
    print(f"   • Virtual Environment: {venv_path}")
    print(f"   • Launcher Script: {launcher_path}")
    print(f"   • Configuration: {Path.home()}/.grey_hat_ai/")
    print()
    print("🚀 How to Launch:")
    print("   Option 1: Run the launcher script")
    print(f"   $ {launcher_path}")
    print()
    print("   Option 2: Use the desktop entry")
    print("   Search for 'Grey Hat AI' in your applications menu")
    print()
    print("   Option 3: Manual launch")
    print(f"   $ source {venv_path}/bin/activate")
    print("   $ streamlit run grey_hat_ai/app.py")
    print()
    print("🔧 Configuration:")
    print("   • Use the GUI sidebar to configure API keys")
    print("   • Supported LLMs: Google Gemini, Mistral AI, Groq")
    print("   • Voice support: Eleven Labs TTS + local Whisper STT")
    print("   • Web automation: Playwright-based autonomous agent")
    print()
    print("📚 Documentation:")
    print("   • README.md - General information and features")
    print("   • docs/ - Detailed documentation and guides")
    print()
    print("⚠️  Important Notes:")
    print("   • Configure at least one LLM API key to use the system")
    print("   • Voice features require microphone permissions")
    print("   • Web automation requires internet access")
    print("   • Use responsibly and only on authorized targets")
    print()
    print("🎯 Happy Hacking!")
    print("="*60)

def main():
    """Main installation function."""
    print("🎯 Grey Hat AI Installer for Kali Linux")
    print("="*50)
    
    try:
        # Check system requirements
        if not check_system_requirements():
            sys.exit(1)
        
        # Install system dependencies
        install_system_dependencies()
        
        # Create virtual environment
        venv_path, activate_script = create_virtual_environment()
        
        # Install Python dependencies
        install_python_dependencies(venv_path)
        
        # Install Playwright
        install_playwright()
        
        # Create launcher script
        launcher_path = create_launcher_script(venv_path)
        
        # Create desktop entry
        create_desktop_entry(launcher_path)
        
        # Setup configuration
        setup_configuration()
        
        # Print summary
        print_installation_summary(launcher_path, venv_path)
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

