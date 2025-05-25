"""
Constants for the AI Launcher application.
Contains all UI dimensions, colors, timings, and text constants.
"""

from PyQt5.QtCore import Qt, QEasingCurve
from PyQt5.QtGui import QColor

# =============================================================================
# LLM Config
# =============================================================================

class LLM:
    DEFAULT_API_BASE = 'https://api.openai.com/v1'
    DEFAULT_LLM_MODEL = 'gpt-4.1-mini'


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
    COMPACT_WIDTH = 600
    COMPACT_HEIGHT = 90
    
    # Expanded mode (with response)
    EXPANDED_WIDTH = 650
    EXPANDED_HEIGHT = 450
    
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
    RESPONSE_MIN_HEIGHT = 250
    RESPONSE_MAX_HEIGHT = 340
    RESPONSE_MARGIN_BOTTOM = 100  # Space for input area
    
    # Margins and spacing
    CONTAINER_MARGIN_HORIZONTAL = 20
    CONTAINER_MARGIN_VERTICAL = 15
    CONTAINER_SPACING = 15
    INPUT_LAYOUT_SPACING = 15
    
    # Copy button positioning
    COPY_BUTTON_MARGIN = 10

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
    CLASSIC = "Classic"
    DARK = "Dark"
    DEFAULT_THEME = CLASSIC

# =============================================================================
# TIMING AND ANIMATION
# =============================================================================

class Timing:
    """Timing constants for animations and delays"""
    # Request delays
    DEFAULT_REQUEST_DELAY_SECONDS = 1.0
    
    # Animation durations
    RESIZE_ANIMATION_DURATION = 200
    RESIZE_ANIMATION_FAST_DURATION = 50
    THINKING_ANIMATION_INTERVAL = 440
    
    # UI feedback delays
    COPY_FEEDBACK_DURATION = 2000
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
    ## API Settings
    SETTINGS_DIALOGUE_API_KEY_LABEL = "API Key:"
    SETTINGS_DIALOGUE_API_KEY_PLACEHOLDER = "Enter your API key..."
    SETTINGS_DIALOGUE_API_BASE_LABEL = "API base URL:"
    SETTINGS_DIALOGUE_API_BASE_PLACEHOLDER = "API base URL..."
    ## LLM Model
    SETTINGS_DIALOGUE_LLM_MODEL_PLACEHOLDER = "Model name..."
    # Request Delay
    SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_LABEL = "Request Delay (seconds):"
    SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_PLACEHOLDER = "Delay in seconds (0.1-10.0)..."
    # Hotkey
    SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_LABEL = "Global Hotkey:"
    SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_PLACEHOLDER = "e.g., <alt>+x, <ctrl>+<shift>+l..."

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