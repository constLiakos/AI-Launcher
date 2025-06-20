"""
Constants for the AI Launcher application.
Contains all UI dimensions, colors, timings, and text constants.
"""
import sys
from PyQt5.QtCore import Qt, QEasingCurve
from PyQt5.QtGui import QColor
from pathlib import Path

def get_base_path():
    """Get the base path for resources, works in both dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in development
        return Path(__file__).parent.parent

# =============================================================================
# Directories
# =============================================================================

class Directories:
    # These use user's home directory - will work fine with PyInstaller
    DEFAULT_TMP = Path.home() / '.tmp' / 'ai_launcher'
    CONFIG = Path.home() / '.config' / 'ai_launcher' / 'config.json'
    CONVERSATIONS_DATABASE_DIR = Path.home() / '.config' / 'ai_launcher'

class Files:
    RECORDING_FILE_NAME = "recorded_audio.wav"
    RECORDING_FILE_PATH = Directories.DEFAULT_TMP / RECORDING_FILE_NAME
    
    _base_path = get_base_path()
    SETTINGS_GEAR_ICON_PATH = _base_path / "assets" / "settings.png"
    MIC_IDLE_ICON_PATH = _base_path / "assets" / "mic_white_idle.png"
    MIC_RECORDING_ICON_PATH = _base_path / "assets" / "mic_white_recording.png"
    CONVERSATION_BTN_SHOW_RESPONSE_PATH = _base_path / "assets" / "show_last_response_btn.png"
    CONVERSATION_BTN_SHOW_HISTORY_PATH = _base_path / "assets" / "show_history_btn.png"
    CLEAR_CONVESRATION_BTN = _base_path / "assets" / "clear_history.png"
    SUCCESS_ICON = _base_path / "assets" / "success.png"
    COPY_BTN = _base_path / "assets" / "copy.png"
    USER_ICON_PATH = _base_path / "assets" / "user.png"
    ASSISTANT_ICON_PATH = _base_path / "assets" / "assistant.png"
    REFRESH_ICON_PATH = _base_path / "assets" / "refresh.png"
    CONVERSATIONS_DATABASE_PATH = Directories.CONVERSATIONS_DATABASE_DIR / 'ai_conversations.db'

    
class Database:
    CONVERSATIONS_DATABASE_CONNECTION_STRING = 'sqlite:///' + str(Files.CONVERSATIONS_DATABASE_PATH)
# =============================================================================
# LLM Config
# =============================================================================

class Conversation:
    DEFAULT_CONVERSATION_HISTORY_LIMIT = 20
    DEFAULT_CLEAR_HISTORY_ON_MINIMIZE = False
    DEFAULT_CLEAR_LAST_RESPONSE_ON_MINIMIZE = True

# =============================================================================
# LLM Config
# =============================================================================

class LLM:
    DEFAULT_API_BASE = 'https://api.openai.com/v1'
    DEFAULT_LLM_MODEL = 'gpt-4.1-mini'
    DEFAULT_SYSTEM_PROMPT = "You’re a friendly assistant delivering clear, concise answers for everyday learning and fun facts. Keep replies brief, use tables for clarity, and make learning quick and enjoyable."
    DEFAULT_REQUEST_TIMEOUT = 120
    DEFAULT_REQUEST_TIMEOUT_GET_AVAILABLE_MODELS = 7
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7

# =============================================================================
# Hotkey
# =============================================================================

class Hotkey:
    DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW = '<alt>+x'

# =============================================================================
# WINDOW DIMENSIONS
# =============================================================================


class WindowSize:
    """Window size constants"""
    # Compact mode (input only)
    COMPACT_WIDTH = 650
    COMPACT_HEIGHT = 90

    # Expanded mode (with response)
    EXPANDED_SINGLELINE_INPUT_WIDTH = 650
    EXPANDED_SINGLELINE_INPUT_HEIGHT = 450

    EXPANDED_MULTILINE_INPUT_WIDTH = 650
    EXPANDED_MULTILINE_INPUT_HEIGHT = 600

    # Default position
    DEFAULT_X = 100
    DEFAULT_Y = 100

# =============================================================================
# UI ELEMENT SIZES
# =============================================================================


class ElementSize:
    """UI element size constants"""
    # Buttons
    SETTINGS_BUTTON_SIZE = 50
    COPY_BUTTON_WIDTH = 40
    COPY_BUTTON_HEIGHT = 30

    # Response area
    RESPONSE_MIN_HEIGHT = 350
    RESPONSE_MAX_HEIGHT = 1000
    RESPONSE_MARGIN_BOTTOM = 100  # Space for input area

    RESPONSE_MIN_HEIGHT_RATIO = 0.3
    RESPONSE_MAX_HEIGHT_RATIO = 0.9
    RESPONSE_MIN_ABSOLUTE_HEIGHT = 20
    RESPONSE_AVAILABLE_HEIGHT_MINIMUM = 50

    # Margins and spacing
    CONTAINER_MARGIN_HORIZONTAL = 20
    CONTAINER_MARGIN_VERTICAL = 15
    CONTAINER_SPACING = 15
    INPUT_LAYOUT_SPACING = 15

    # Copy button positioning
    COPY_BUTTON_MARGIN = 10
    COPY_BUTTON_RIGHT_MARGIN = 12

    SCROLLBAR_SIZE = 8
    TRIGGER_EDGE_RESIZE_MARGIN_HORIZONTAL = 15
    TRIGGER_EDGE_RESIZE_MARGIN_VERTICAL = 15

    CONVERSATION_TOGGLE_BUTTON_WIDTH = 40
    CONVERSATION_TOGGLE_BUTTON_HEIGHT = 10
    CONVERSATION_TOGGLE_BUTTON_BOTTOM_MARGIN = 1

# =============================================================================
# SETTINGS DIALOG
# =============================================================================


class SettingsDialogSize:
    """Settings dialog constants"""
    # Window dimensions
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 550

    # Layout spacing
    MAIN_LAYOUT_MARGIN = 20
    MAIN_LAYOUT_SPACING = 20
    FORM_LAYOUT_SPACING = 20
    FORM_LAYOUT_VERTICAL_SPACING = 15
    BUTTON_LAYOUT_SPACING = 15

    # Input field dimensions
    INPUT_FIELD_MIN_HEIGHT = 35
    CHECKBOX_MIN_HEIGHT = 35
    COMBO_BOX_MIN_HEIGHT = 35
    BUTTON_MIN_HEIGHT = 40

    SYSTEM_PROMPT_MIN = 100
    SYSTEM_PROMPT_MAX = 200

# =============================================================================
# ABOUT DIALOG
# =============================================================================


class AboutDialogSize:
    """About dialog constants"""
    # Window dimensions
    WINDOW_WIDTH = 650
    WINDOW_HEIGHT = 650

    # Layout spacing
    MAIN_LAYOUT_MARGIN = 20
    MAIN_LAYOUT_SPACING = 20
    FORM_LAYOUT_SPACING = 20
    FORM_LAYOUT_VERTICAL_SPACING = 15
    BUTTON_LAYOUT_SPACING = 15

    # Input field dimensions
    INPUT_FIELD_MIN_HEIGHT = 35
    CHECKBOX_MIN_HEIGHT = 35
    COMBO_BOX_MIN_HEIGHT = 35
    BUTTON_MIN_HEIGHT = 40

# =============================================================================
# STT DIALOG
# =============================================================================


class STTDialogSize:
    """About dialog constants"""
    # Window dimensions
    WINDOW_WIDTH = 650
    WINDOW_HEIGHT = 650

    # Layout spacing
    MAIN_LAYOUT_MARGIN = 20
    MAIN_LAYOUT_SPACING = 20
    FORM_LAYOUT_SPACING = 20
    FORM_LAYOUT_VERTICAL_SPACING = 15
    BUTTON_LAYOUT_SPACING = 15

    # Input field dimensions
    INPUT_FIELD_MIN_HEIGHT = 35
    CHECKBOX_MIN_HEIGHT = 35
    COMBO_BOX_MIN_HEIGHT = 35
    BUTTON_MIN_HEIGHT = 40


# =============================================================================
# STT DIALOG
# =============================================================================

class STT:
    """Constants related to Speech-to-Text functionality."""
    DEFAULT_API_BASE = 'https://api.openai.com/v1'
    DEFAULT_MODEL = "whisper-1"                             
    DEFAULT_HOTKEY = "<ctrl>+<shift>+r"
    DEFAULT_REQUEST_TIMEOUT = 20
    DEFAULT_ENABLED = False

# =============================================================================
# COLORS
# =============================================================================


class Colors:
    """Color constants"""
    # Primary brand colors
    PRIMARY_BLUE = QColor(79, 156, 249)
    PRIMARY_PURPLE = QColor(139, 92, 246)
    PRIMARY_PINK = QColor(236, 72, 153)
    PRIMARY_GREEN = QColor(34, 197, 94)
    PRIMARY_ORANGE = QColor(249, 115, 22)

    # UI colors
    WHITE = QColor(255, 255, 255)
    BLACK = QColor(0, 0, 0)
    TEXT_DARK = QColor(45, 49, 66)  # #2d3142
    SUCCESS_GREEN = QColor(16, 185, 129)  # #10b981

    # Shadow
    SHADOW_COLOR = QColor(0, 0, 0, 60)

    # Animation colors (for thinking animation)
    ANIMATION_COLORS = [
        "rgba(79, 156, 249, 0.8)",   # Blue
        "rgba(139, 92, 246, 0.8)",   # Purple
        "rgba(236, 72, 153, 0.8)",   # Pink
        "rgba(79, 156, 249, 0.8)",   # Blue
        "rgba(34, 197, 94, 0.8)",    # Green
        "rgba(249, 115, 22, 0.8)"    # Orange
    ]


class BackgroundColors:
    """Background color constants for window and input elements"""
    # Window background gradient
    WINDOW_TOP = "rgba(252, 253, 255, 0.95)"
    WINDOW_BOTTOM = "rgba(248, 250, 255, 0.95)"

    # Input field background
    INPUT_COLOR_BACKGROUND = "rgba(254, 254, 255, 0.8)"
    INPUT_COLOR_BACKGROUND_FOCUS = "rgba(254, 254, 255, 1)"

    # Border colors
    WINDOW_BORDER = "rgba(79, 156, 249, 0.4)"
    INPUT_BORDER_NORMAL = "rgba(79, 156, 249, 0.3)"
    INPUT_BORDER_COLOR_TYPING = "rgba(2, 2, 2, 0.2)"
    INPUT_COLOR_BORDER_FOCUS = "#4f9cf9"

# =============================================================================
# THEME
# =============================================================================


class Theme:
    """Theme constants"""
    DEFAULT_THEME = "Classic"
    CLASSIC = "Classic"
    DARK = "Dark"
    NATURE = "Nature"
    ROSE = "Rose"
    HUAWEI = "Huawei"


# =============================================================================
# TIMING AND ANIMATION
# =============================================================================


class Timing:
    """Timing constants for animations and delays"""
    # Request delays
    DEFAULT_REQUEST_DELAY_SECONDS = 1.5

    # Animation durations
    RESIZE_ANIMATION_DURATION = 200
    RESIZE_ANIMATION_FAST_DURATION = 50
    THINKING_ANIMATION_INTERVAL = 440

    # UI feedback delays
    COPY_FEEDBACK_DURATION = 1000
    CLEAR_HISTORY_FEEDBACK_DURATION = 1000
    STATUS_DISPLAY_DURATION = 3000
    SETTINGS_FEEDBACK_DURATION = 3000
    TRAY_MESSAGE_DURATION = 2000

    # Window management delays
    WINDOW_FLAG_DELAY = 100
    RESIZE_FINALIZE_DELAY = 10
    REQUEST_EXECUTE_DELAY = 50
    WORKER_CLEANUP_DELAY = 100
    STATUS_HIDE_DELAY = 2000


class AnimationConfig:
    """Animation configuration constants"""
    # Resize animations
    RESIZE_DURATION = Timing.RESIZE_ANIMATION_DURATION
    RESIZE_FAST_DURATION = Timing.RESIZE_ANIMATION_FAST_DURATION

    # Thinking animation
    THINKING_UPDATE_INTERVAL = Timing.THINKING_ANIMATION_INTERVAL
    THINKING_COLORS = Colors.ANIMATION_COLORS

    # Easing curves for animations
    RESIZE_EASING = QEasingCurve.OutQuart
    RESIZE_FAST_EASING = QEasingCurve.OutQuad
    FADE_EASING = QEasingCurve.OutCubic

    # Animation performance settings
    DISABLE_UPDATES_DURING_RESIZE = True
    SMOOTH_PIXMAP_TRANSFORM = True

# =============================================================================
# TEXT CONSTANTS
# =============================================================================


class Text:
    """Text constants and messages"""
    # Placeholder and labels
    INPUT_PLACEHOLDER = "Ask AI anything..."

    # Button text
    SETTINGS_BUTTON = "⚙"
    COPY_BUTTON = "📋"
    COPY_SUCCESS = "✓"

    # Tray menu items
    TRAY_SHOW = "Show"
    TRAY_HIDE = "Hide"
    TRAY_SETTINGS = "Settings"
    TRAY_QUIT = "Quit"
    TRAY_TOOLTIP = "AI Launcher"

    # Status messages
    STATUS_THINKING = "Thinking... 🤔"
    STATUS_STREAMING = "Streaming... ⚡"
    STATUS_COMPLETE = "✓ Response complete"
    STATUS_ERROR = "Error occurred"
    STATUS_NO_TEXT_TO_COPY = "No text to copy"
    STATUS_COPY_FAILED = "Copy failed"

    # Tray messages
    TRAY_BACKGROUND_MESSAGE = "Application is running in the background"
    TRAY_BACKGROUND_TITLE = "AI Launcher"

    # Error messages
    ERROR_PREFIX = "❌ Error: "
    ERROR_PROCESSING_RESPONSE = "Error processing response: "
    ERROR_COPYING_CLIPBOARD = "Error copying to clipboard: "
    ERROR_CANCELLING_REQUEST = "Error cancelling API request: "
    ERROR_CHUNK_HANDLING = "Error handling chunk: "

    # Settings feedback
    SETTINGS_SAVED_PREFIX = "✓ Settings saved! Request delay: "
    SETTINGS_SAVED_SUFFIX = "s"

    # System tray
    TRAY_NOT_AVAILABLE = "System tray is not available on this system"

    # AI tray icon text
    TRAY_ICON_TEXT = "AI"

    # Settings Dialogue
    SETTINGS_DIALOGUE_LABEL = "AI Launcher Settings"
    # API Settings
    SETTINGS_DIALOGUE_API_KEY_LABEL = "API Key:"
    SETTINGS_DIALOGUE_API_KEY_PLACEHOLDER = "Enter your API key..."
    SETTINGS_DIALOGUE_API_BASE_LABEL = "API base URL:"
    SETTINGS_DIALOGUE_API_BASE_PLACEHOLDER = "API base URL..."
    # LLM Model
    SETTINGS_DIALOGUE_LLM_MODEL_PLACEHOLDER = "Model name..."
    # Request Delay
    SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_LABEL = "Request Delay (seconds):"
    SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_PLACEHOLDER = "Delay in seconds (0.1-10.0)..."
    # Hotkey
    SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_LABEL = "Global Hotkey:"
    SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_PLACEHOLDER = "e.g., <alt>+x, <ctrl>+<shift>+l..."
    # Clear Previous Response When Window Minimizes
    SETTINGS_DIALOGUE_CLEAR_LAST_RESPONSE_ON_MINIMIZE_LABEL = "Clear Last Response:"
    SETTINGS_DIALOGUE_CLEAR_LAST_RESPONSE_ON_MINIMIZE_MESSAGE = "Clear last response when window reopens"
    # Clear Conversation History on Hide
    SETTINGS_DIALOGUE_CLEAR_CONVERSATION_HISTORY_ON_MINIMIZE_LABEL = "Clear Conversation:"
    SETTINGS_DIALOGUE_CLEAR_CONVERSATION_HISTORY_ON_MINIMIZE_MESSAGE = "Clear conversation history when window reopens"
    # Settings Hotkey Buttons
    SETTINGS_DIALOG_HOTKEY_BUTTON_NAME = "Hotkey\nRecorder"
    MAIN_HOTKEY_DIALOG_HOTKEY_TITLE = "Record Main Hotkey"
    STT_HOTKEY_DIALOG_HOTKEY_TITLE = "Record STT Hotkey"
    HOTKEY_DIALOG_INSTRUCTIONS = "Hold the keys you want, then click 'Save'"
    HOTKEY_DIALOG_HOTKEY_DISPLAY = "Press keys..."
    HOTKEY_DIALOG_TITLE = "Press your desired hotkey combination"

    ABOUT_DIALOGUE_LABEL = "About This Project"
    ABOUT_DIALOGUE_TEXT = """
<h3>🚀 AI Launcher</h3>
<p>🖥️ A modern, lightweight desktop AI assistant with a sleek system tray interface offering quick access to AI conversations via global hotkeys ⌨️ and real-time streaming responses ⏳.</p>

<h4>🛠️ Technologies:</h4>
<ul>
  <li>🐍 Python</li>
  <li>🎨 PyQt5</li>
  <li>🤖 OpenAI-compatible APIs</li>
  <li>🎹 pynput (for global hotkeys)</li>
</ul>

<h4>👤 Author:</h4>
<p>constLiakos (📧 <a href="mailto:constliakos@gmail.com">constliakos@gmail.com</a>)</p>
<p>GitHub:  <a href="https://github.com/constLiakos/AI-Launcher" target="_blank" rel="noopener noreferrer">https://github.com/constLiakos/AI-Launcher</a></p>
        """

# =============================================================================
# KEYBOARD SHORTCUTS
# =============================================================================


class Shortcuts:
    """Keyboard shortcut constants"""
    ESCAPE = Qt.Key_Escape
    QUIT = "Ctrl+Q"
    SETTINGS = "Ctrl+S"
    ENTER = Qt.Key_Return

# =============================================================================
# STYLING CONSTANTS
# =============================================================================


class Style:
    """Style-related constants"""
    # Border radius
    CONTAINER_BORDER_RADIUS = 20
    INPUT_BORDER_RADIUS = 20
    BUTTON_BORDER_RADIUS = 8

    # Border width
    INPUT_BORDER_WIDTH = 3

    # Font sizes
    INPUT_FONT_SIZE = 16
    TRAY_ICON_FONT_SIZE = 12

    # Opacity values
    BACKGROUND_OPACITY_NORMAL = 0.8
    BACKGROUND_OPACITY_FOCUS = 1.0

    # Shadow
    SHADOW_BLUR_RADIUS = 30
    SHADOW_X_OFFSET = 0
    SHADOW_Y_OFFSET = 10

# =============================================================================
# SYSTEM TRAY
# =============================================================================


class TrayIcon:
    """System tray icon constants"""
    SIZE = 32
    FONT_FAMILY = "Arial"
    FONT_WEIGHT = 700  # Bold

# =============================================================================
# ANIMATION PHASES
# =============================================================================


class Animation:
    """Animation-related constants"""
    THINKING_PHASES = 6
    EASING_CURVE = "OutCubic"  # For QEasingCurve


class InputSettings:
    """Input Area Settings"""
    IS_MULTILINE_INPUT = True
    MAX_HEIGHT = 300
    MULTILINE_SINGLE_LINE_HEIGHT = 50  # Height equivalent to single line
    MULTILINE_EXPANSION_STEP = 25      # Height increase per line
    MAX_WINDOW_EXPANSION = 200         # Maximum additional window height
    BASE_PADDING = 40
    LINE_HEIGHT = 20