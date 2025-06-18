# Grey Hat AI - Quick Start Guide

## 🎯 What is Grey Hat AI?

Grey Hat AI is a powerful, production-ready AI application designed specifically for cybersecurity professionals using Kali Linux. It enhances the proven CAI (Cybersecurity AI) framework with:

- **Modern Web GUI**: Streamlit-based interface with real-time agent transparency
- **Multi-LLM Support**: Google Gemini, Mistral AI, and Groq integration
- **Voice Interaction**: Local speech-to-text and Eleven Labs TTS
- **Autonomous Web Testing**: Playwright-based browser automation
- **Human-in-the-Loop**: Maintains human oversight for all critical operations

## 🚀 Quick Installation (Kali Linux)

### Option 1: Automated Installation (Recommended)

```bash
# Extract the package
tar -xzf grey_hat_ai_v1.0.0.tar.gz
cd grey_hat_ai

# Run the automated installer
sudo python3 install_kali.py

# Launch Grey Hat AI
   ./launch_grey_hat_ai.sh
```

### Option 2: Manual Installation

```bash
# Extract and navigate
tar -xzf grey_hat_ai_v1.0.0.tar.gz
cd grey_hat_ai

# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev build-essential \
                    portaudio19-dev libasound2-dev libsndfile1-dev ffmpeg

# Create virtual environment
python3 -m venv ~/grey_hat_ai_venv
source ~/grey_hat_ai_venv/bin/activate

# Install Python dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium

# Launch the application
streamlit run grey_hat_ai/app.py
```

## ⚙️ Initial Configuration

1. **Open your browser** and navigate to `http://localhost:8501`

2. **Configure API Keys** (at least one required):
   - Google Gemini API Key
   - Mistral AI API Key  
   - Groq API Key
   - Eleven Labs API Key (for voice features)

3. **Select Active LLM** from the sidebar dropdown

4. **Test the system** by asking a simple question

## 🎤 Voice Setup (Optional)

1. Configure Eleven Labs API key in the sidebar
2. Select your preferred voice model
3. Click "🎤 Start Voice" to enable voice input
4. Speak naturally - the system will transcribe and respond with voice

## 🎯 Basic Usage

### Conversational Interface
- Type questions or commands in the chat interface
- Watch the "Agent Scratchpad" for real-time AI reasoning
- Use natural language for cybersecurity tasks

### Target Testing
1. Enter target (IP, URL, domain) in the sidebar
2. Click "🚀 Start Auto Test" for automated assessment
3. Monitor progress in real-time
4. Review findings and recommendations

### Example Commands
- "Perform reconnaissance on 192.168.1.1"
- "Analyze this web application: https://example.com"
- "Help me understand this nmap scan result"
- "Generate a penetration testing report"

## 📁 Key Files

- `grey_hat_ai/app.py` - Main Streamlit application
- `install_kali.py` - Automated installation script
- `README.md` - Comprehensive documentation
- `INSTALLATION_GUIDE.md` - Detailed installation and usage guide
- `pyproject.toml` - Python package configuration

## 🔧 System Requirements

- **OS**: Kali Linux 2023.1+ (or compatible Debian-based)
- **Python**: 3.9 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB minimum, 20GB recommended
- **Network**: Internet access for AI APIs

## 🛡️ Security Notes

- **Authorization Required**: Only test systems you own or have permission to test
- **Human Oversight**: Always maintain human control over critical operations
- **API Security**: API keys are stored securely in session memory
- **Audit Logging**: All activities are logged for security monitoring

## 📚 Documentation

- **README.md**: Overview and features
- **INSTALLATION_GUIDE.md**: Comprehensive 50+ page guide covering:
  - Detailed installation instructions
  - Configuration options
  - Usage examples
  - Troubleshooting
  - Security considerations
  - Performance optimization

## 🆘 Quick Troubleshooting

### Installation Issues
- Ensure Python 3.9+ is installed
- Run `sudo apt update` before installation
- Check internet connectivity for package downloads

### Runtime Issues
- Verify API keys are correctly entered
- Check that at least one LLM provider is configured
- Ensure microphone permissions for voice features

### Performance Issues
- Use Groq for fast operations
- Reduce Whisper model size if memory is limited
- Monitor system resources during intensive operations

## 🤝 Support

- **Documentation**: Comprehensive guides included
- **Community**: Engage with cybersecurity AI community
- **Issues**: Report bugs and feature requests
- **Professional**: Consider consulting services for enterprise deployments

## ⚠️ Disclaimer

Grey Hat AI is a powerful tool for legitimate cybersecurity research and testing. Users are responsible for ensuring compliance with applicable laws and regulations. Only test systems you own or have explicit permission to test.

---

**🎯 Grey Hat AI v1.0.0 - Empowering Cybersecurity Professionals with Advanced AI**

*Built on the proven CAI framework by Alias Robotics*  
*Enhanced by Manus AI for production-ready deployment*

