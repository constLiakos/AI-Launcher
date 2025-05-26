# AI Launcher

A modern, lightweight desktop AI assistant with a sleek interface that lives in your system tray. Quick access to AI conversations with global hotkeys and real-time streaming responses.

![Demo](assets/demo-01.gif "Demo 1")

## Features

### 🚀 Quick Access

- **Global Hotkey**: Instantly summon the AI interface from anywhere (configurable in settings)
- **System Tray Integration**: Minimizes to tray, always accessible with right-click menu
- **Compact Design**: Clean, minimal interface that expands when needed

### 💬 AI Conversation

- **Real-time Streaming**: See responses as they're generated with visual feedback
- **Markdown Support**: Rich text formatting in responses with HTML rendering
- **Copy Responses**: One-click copying to clipboard with visual confirmation
- **Request Management**: Cancel ongoing requests, configurable delays, smart debouncing

### 🎨 Modern Interface

- **Frameless Window**: Sleek, borderless design with drag-to-move functionality
- **Smooth Animations**: Fluid resize and state transitions with animation manager
- **Dark Theme**: Modern styling with rounded corners and drop shadows
- **Visual Feedback**: Input states (normal, thinking, streaming, typing)
- **Smart Positioning**: Remembers window position, auto-saves during moves

### ⚙️ Customizable

- **Settings Dialog**: Easy configuration with keyboard shortcuts (Ctrl+S)
- **Configurable Hotkeys**: Set your preferred global shortcut
- **API Settings**: Connect to your preferred AI service
- **Request Delays**: Prevent accidental rapid-fire requests with configurable timing
- **Clear Options**: Option to clear previous responses when reopening

### ⌨️ Keyboard Shortcuts

- **Global Hotkey**: Quick access from anywhere (configurable)
- **Escape**: Hide to system tray
- **Ctrl+Q**: Quit application completely
- **Ctrl+S**: Open settings dialog
- **Enter**: Send message

## Installation

### Prerequisites

- Python 3.7+
- PyQt5
- pynput (for global hotkeys)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/constLiakos/AI-Launcher.git
cd AI-Launcher
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

**Linux/macOS:**

```bash
python src/main.py
```

**Windows:**

```cmd
python src\main.py
```

### Building Executable

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

The executable will be created in the `dist/` directory.

## Info

### LLM Providers

| Provider     | API URL                                               | Docs URL                                                    |
|--------------|-------------------------------------------------------|-------------------------------------------------------------|
| OpenAI       | https://api.openai.com/v1                             | https://platform.openai.com/docs/quickstart                 |
| Groq         | https://api.groq.com/openai/v1/audio/transcriptions  | https://console.groq.com/docs/quickstart                     |
| TogetherAI   | https://api.together.xyz/v1                           | https://docs.together.ai/docs/introduction                   |
| FireworksAI  | https://api.fireworks.ai/inference/v1                 | https://docs.fireworks.ai/getting-started/introduction       |

### Local Running

| Provider | API URL                    | Docs URL                                                                                       |
|----------|----------------------------|------------------------------------------------------------------------------------------------|
| Ollama   | http://localhost:11434/v1  | https://github.com/ollama/ollama/blob/main/README.md#quickstart                                |
