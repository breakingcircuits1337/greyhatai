# Grey Hat AI

**Advanced Cybersecurity AI Framework with GUI and Voice Integration**

Grey Hat AI is a powerful, production-ready AI application designed specifically for cybersecurity professionals using Kali Linux. Built upon the proven CAI (Cybersecurity AI) framework, it provides an intuitive graphical interface, multi-modal interaction capabilities, and advanced automation features for penetration testing and security research.

## 🎯 Key Features

### 🖥️ Unified Command and Control Interface
- **Modern Web-based GUI**: Built with Streamlit for intuitive operation
- **Real-time Agent Transparency**: Live view of AI reasoning and decision-making process
- **Conversational Interface**: Natural language interaction with streaming responses
- **Secure Configuration Management**: GUI-based API key input and system configuration

### 🤖 Multi-Model LLM Support
- **Google Gemini**: Advanced reasoning and analysis capabilities
- **Mistral AI**: Including Codestral for code generation and analysis
- **Groq**: Ultra-fast inference for rapid reconnaissance tasks
- **Dynamic Switching**: Task-specific LLM optimization for maximum efficiency

### 🎤 Voice Interaction Engine
- **Speech-to-Text**: Local Whisper-based STT for privacy and speed
- **Text-to-Speech**: High-quality Eleven Labs TTS with voice selection
- **Continuous Listening**: Voice Activity Detection for hands-free operation
- **Multi-threaded Architecture**: Seamless integration with GUI workflow

### 🌐 Autonomous Web Agent
- **Playwright Integration**: Advanced browser automation capabilities
- **Intelligent Navigation**: Autonomous web reconnaissance and interaction
- **Form Automation**: Automated form filling and submission
- **Content Extraction**: Smart parsing and analysis of web content
- **Screenshot Capture**: Visual documentation of findings

### 🚀 Autonomous Testing Workflow
- **Orchestrated Penetration Testing**: Multi-phase automated security assessment
- **Human-in-the-Loop**: Critical actions require explicit user confirmation
- **Tool Integration**: Seamless use of Kali Linux security tools
- **Comprehensive Reporting**: Automated generation of findings and reports

### 🔍 Enhanced Observability
- **Agent Scratchpad**: Real-time visualization of AI thought processes
- **Phoenix Integration**: Advanced tracing and observability
- **Decision Transparency**: Complete visibility into agent reasoning
- **Performance Monitoring**: Track LLM usage and response times

## 🛠️ Installation

### Prerequisites
- Kali Linux (or compatible Debian-based system)
- Python 3.9 or higher
- Internet connection for API access and tool downloads

### Quick Installation

1. **Clone or extract Grey Hat AI**:
   ```bash
   # If you have the source code
   cd grey_hat_ai
   ```

2. **Run the automated installer**:
   ```bash
   sudo python3 install_kali.py
   ```

3. **Launch Grey Hat AI**:
   ```bash
   ./launch_grey_hat_ai.sh
   ```

The installer will:
- Install all system dependencies
- Create a virtual environment
- Install Python packages
- Set up Playwright browsers
- Create launcher scripts and desktop entries
- Configure the application structure

### Manual Installation

If you prefer manual installation:

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv python3-dev build-essential \
                       portaudio19-dev libasound2-dev libsndfile1-dev ffmpeg
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv ~/grey_hat_ai_venv
   source ~/grey_hat_ai_venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -e .
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   playwright install-deps chromium
   ```

5. **Launch the application**:
   ```bash
   streamlit run grey_hat_ai/app.py
   ```

## 🚀 Usage

### Initial Setup

1. **Launch Grey Hat AI** using one of the methods above
2. **Open your browser** and navigate to the displayed URL (typically `http://localhost:8501`)
3. **Configure API Keys** in the sidebar:
   - Google Gemini API key
   - Mistral AI API key
   - Groq API key
   - Eleven Labs API key (for voice features)

### Basic Operation

1. **Select Active LLM**: Choose your preferred LLM provider and model from the sidebar
2. **Set Target**: Enter your target IP, URL, or domain in the target field
3. **Start Conversation**: Use the chat interface to interact with the AI agent
4. **Monitor Agent Activity**: Watch the Agent Scratchpad for real-time insights

### Voice Interaction

1. **Configure Eleven Labs**: Enter your API key in the sidebar
2. **Start Voice Listening**: Click the "🎤 Start Voice" button
3. **Speak Commands**: The system will automatically detect and transcribe speech
4. **Receive Audio Responses**: The AI will respond with synthesized speech

### Autonomous Testing

1. **Set Target**: Enter the target system in the sidebar
2. **Start Auto Test**: Click "🚀 Start Auto Test" to begin automated assessment
3. **Monitor Progress**: Watch the conversation and scratchpad for real-time updates
4. **Review Findings**: The system will provide comprehensive results and recommendations

### Advanced Features

#### Custom Tool Integration
Grey Hat AI integrates seamlessly with existing Kali Linux tools:
- **Network Reconnaissance**: nmap, netcat, curl integration
- **Web Testing**: Automated browser-based testing
- **Code Analysis**: Built-in code interpretation and analysis
- **Custom Scripts**: Execute and analyze custom security scripts

#### Multi-Phase Testing Workflow
1. **Reconnaissance Phase**: Fast LLM (Groq) for rapid information gathering
2. **Analysis Phase**: Advanced LLM (Gemini/Mistral) for vulnerability assessment
3. **Exploitation Phase**: Human-confirmed testing of identified vulnerabilities
4. **Reporting Phase**: Automated documentation and recommendations

## 🔧 Configuration

### API Keys
Configure your API keys through the GUI sidebar or by setting environment variables:

```bash
export GOOGLE_GEMINI_API_KEY="your_key_here"
export MISTRAL_API_KEY="your_key_here"
export GROQ_API_KEY="your_key_here"
export ELEVENLABS_API_KEY="your_key_here"
```

### Voice Settings
Customize voice recognition and synthesis:
- **Whisper Model Size**: Adjust for speed vs. accuracy trade-off
- **Voice Selection**: Choose from available Eleven Labs voices
- **Audio Settings**: Configure microphone and speaker preferences

### Web Agent Configuration
Customize browser automation behavior:
- **Browser Type**: Chromium (default), Firefox, or WebKit
- **Headless Mode**: Run browsers with or without GUI
- **Security Settings**: Configure SSL and security preferences

## 🛡️ Security Considerations

### Responsible Use
- **Authorization Required**: Only test systems you own or have explicit permission to test
- **Human Oversight**: Always maintain human control over critical operations
- **Data Privacy**: Voice processing is done locally when possible
- **API Security**: API keys are handled securely and not stored in plaintext

### Network Security
- **Isolated Testing**: Consider using isolated networks for testing
- **VPN Usage**: Use VPNs when appropriate for testing activities
- **Traffic Monitoring**: Monitor network traffic during automated testing

## 🔍 Troubleshooting

### Common Issues

#### Installation Problems
- **Permission Errors**: Ensure you have sudo access for system package installation
- **Python Version**: Verify Python 3.9+ is installed
- **Network Issues**: Check internet connectivity for package downloads

#### Runtime Issues
- **API Key Errors**: Verify API keys are correctly entered and have sufficient credits
- **Voice Problems**: Check microphone permissions and audio device configuration
- **Browser Issues**: Ensure Playwright browsers are properly installed

#### Performance Issues
- **Slow Responses**: Try switching to faster LLM providers (Groq) for speed-critical tasks
- **Memory Usage**: Monitor system resources during intensive operations
- **Network Latency**: Consider local model deployment for improved performance

### Getting Help
- **Logs**: Check application logs for detailed error information
- **Documentation**: Refer to the docs/ directory for detailed guides
- **Community**: Engage with the cybersecurity AI community for support

## 📚 Documentation

- **User Guide**: Detailed usage instructions and best practices
- **API Reference**: Complete API documentation for developers
- **Architecture Guide**: Technical details about system design
- **Security Guide**: Best practices for secure operation

## 🤝 Contributing

Grey Hat AI is built on open-source principles. Contributions are welcome:

1. **Fork the Repository**: Create your own fork for development
2. **Create Feature Branch**: Develop new features in dedicated branches
3. **Submit Pull Request**: Contribute improvements back to the project
4. **Report Issues**: Help improve the system by reporting bugs and suggestions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CAI Framework**: Built upon the excellent Cybersecurity AI framework by Alias Robotics
- **Streamlit**: For providing an excellent framework for rapid GUI development
- **OpenAI Whisper**: For high-quality local speech recognition
- **Playwright**: For robust browser automation capabilities
- **The Security Community**: For continuous feedback and improvement suggestions

## ⚠️ Disclaimer

Grey Hat AI is a powerful tool designed for legitimate cybersecurity research and testing. Users are responsible for ensuring their use complies with applicable laws and regulations. The developers assume no responsibility for misuse of this software.

---

**🎯 Grey Hat AI - Empowering Cybersecurity Professionals with Advanced AI**

