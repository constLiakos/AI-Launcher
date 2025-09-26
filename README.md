# 🚀 AI Launcher
[![Version](https://img.shields.io/badge/version-v1.0.6-blue.svg)](https://github.com/constLiakos/AI-Launcher-Electron/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#)
> ✨ A lightweight desktop AI assistant that lives in your system tray with quick global hotkey access.

![Demo](docs/assets/demo.gif "Demo 1")

## 🌟 Features
- **⚡ Global Hotkey**: Instantly summon the AI interface from anywhere.
- **🔄 System Tray Integration**: Always accessible with a right-click context menu.
- **📡 Real-time Streaming**: See responses as they're generated in real-time.
- **🎤 Voice Input**: Speech-to-text with microphone support.
- **📝 Multiline Input**: Adaptive input modes for single-line or multiline messages.
- **📄 Markdown Support**: Rich text formatting with code highlighting.
- **🎨 Modern Interface**: Sleek, frameless design.
- **💬 Conversation History**: Persists conversations locally using an SQLite database.
- **⚙️ Customizable**: Configurable hotkeys, API settings, and models.

## 📦 Installation
### 🎯 Quick Start (Recommended)
Download the latest pre-built installer from the [releases page](https://github.com/constLiakos/AI-Launcher-Electron/releases).

### 🛠️ From Source
1. **Clone the repository:**
```bash
git clone https://github.com/constLiakos/AI-Launcher-Electron.git
cd AI-Launcher-Electron
```
2. **Install dependencies:**
```bash
npm install
```
3. **Generate Prisma Client:**
```bash
npm run prisma:generate
```
4. **Run the application in development mode:**
```bash
npm run dev
```

### 🔨 Building Executable
To build a standalone executable for your platform:
```bash
npm run dist
```
The distributable files will be located in the `dist` directory.

## ⌨️ Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| **🔥 Global Hotkey** | Quick access from anywhere (configurable) |
| **➖ Escape** | Hide to system tray |
| **Ctrl+Q** | Quit application |
| **Ctrl+S** | Open settings |
| **↵ Enter** | Send message (in single-line mode) |
| **Shift+Enter** | New line (in multiline mode) |

## 🤖 Supported Providers
### 🌐 LLM Providers
| Provider | API URL | Docs URL |
|--------------|-------------------------------------------------------|-------------------------------------------------------------|
| OpenAI | `https://api.openai.com/v1` | [Docs](https://platform.openai.com/docs/quickstart) |
| Groq | `https://api.groq.com/openai/v1` | [Docs](https://console.groq.com/docs/quickstart) |
| TogetherAI | `https://api.together.xyz/v1` | [Docs](https://docs.together.ai/docs/introduction) |
| FireworksAI | `https://api.fireworks.ai/inference/v1` | [Docs](https://docs.fireworks.ai/getting-started/introduction) |
### 🏠 Local Running
| Provider | API URL | Docs URL |
|----------|-----------------------------|------------------------------------------------------------------------------------------------|
| Ollama | `http://localhost:11434/v1` | [Docs](https://github.com/ollama/ollama/blob/main/README.md#quickstart) |

## 🛠️ Tech Stack
- **Framework**: [Electron](https://www.electronjs.org/)
- **Frontend**: [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev/)
- **Database**: [SQLite](https://www.sqlite.org/index.html) + [Prisma ORM](https://www.prisma.io/)
- **Packaging**: [Electron Builder](https://www.electron.build/)