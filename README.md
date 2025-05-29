# AI Launcher

[![Version](https://img.shields.io/badge/version-v1.0.8-blue.svg)](https://github.com/constLiakos/AI-Launcher/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#)

> ✨ A lightweight desktop AI assistant that lives in your system tray with quick global hotkey access.

![Demo](assets/demo-01.gif "Demo 1")

## 🌟 Features

- **⚡ Global Hotkey**: Instantly summon the AI interface from anywhere
- **🔄 System Tray Integration**: Always accessible with right-click menu
- **📡 Real-time Streaming**: See responses as they're generated
- **🎤 Voice Input**: Speech-to-text with microphone support
- **📝 Markdown Support**: Rich text formatting with HTML rendering
- **🎨 Modern Interface**: Sleek, frameless design with smooth animations
- **⚙️ Customizable**: Configurable hotkeys, API settings, and preferences

## 📦 Installation

### 🎯 Quick Start (Recommended)

Download the latest pre-built executable from the [releases page](https://github.com/constLiakos/AI-Launcher/releases).

### 🛠️ From Source

1. **Clone the repository:**

```bash
git clone https://github.com/constLiakos/AI-Launcher.git
cd AI-Launcher
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the application:**

```bash
python src/main.py
```

### 🔨 Building Executable

To build a standalone executable:

**Linux/macOS:**

```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

**Windows:**

```cmd
scripts\build.bat
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **🔥 Global Hotkey** | Quick access from anywhere (configurable) |
| **➖ Escape** | Hide to system tray |
| **Ctrl+Q** | Quit application |
| **Ctrl+S** | Open settings |
| **↵ Enter** | Send message |

## 🤖 Supported Providers

### 🌐 LLM Providers

| Provider     | API URL                                               | Docs URL                                                    |
|--------------|-------------------------------------------------------|-------------------------------------------------------------|
| OpenAI       | <https://api.openai.com/v1>                             | <https://platform.openai.com/docs/quickstart>                 |
| Groq         | <https://api.groq.com/openai/v1/audio/transcriptions>  | <https://console.groq.com/docs/quickstart>                     |
| TogetherAI   | <https://api.together.xyz/v1>                           | <https://docs.together.ai/docs/introduction>                   |
| FireworksAI  | <https://api.fireworks.ai/inference/v1>                 | <https://docs.fireworks.ai/getting-started/introduction>       |

### 🏠 Local Running

| Provider | API URL                    | Docs URL                                                                                       |
|----------|----------------------------|------------------------------------------------------------------------------------------------|
| Ollama   | <http://localhost:11434/v1>  | <https://github.com/ollama/ollama/blob/main/README.md#quickstart>                                |
