#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QSharedMemory
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
import argparse

# Set High DPI attributes BEFORE creating QApplication
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from launcher import Launcher

class SingleInstanceApp:
    def __init__(self):
        self.server = None
        self.shared_memory = QSharedMemory("AILauncherSingleInstance")
        
    def is_already_running(self):
        """Check if application is already running using shared memory"""
        if self.shared_memory.attach():
            # Already running
            return True
        
        if self.shared_memory.create(1):
            # First instance
            return False
        
        # Error occurred
        return True
    
    def send_show_command(self):
        """Send command to existing instance to show window"""
        socket = QLocalSocket()
        socket.connectToServer("AILauncherIPC")
        if socket.waitForConnected(1000):
            socket.write(b"SHOW")
            socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
            return True
        return False
    
    def setup_ipc_server(self, launcher:Launcher):
        """Setup IPC server to listen for show commands"""
        self.server = QLocalServer()
        # Remove any existing server
        QLocalServer.removeServer("AILauncherIPC")
        
        if self.server.listen("AILauncherIPC"):
            self.server.newConnection.connect(lambda: self.handle_new_connection(launcher))
            return True
        return False
    
    def handle_new_connection(self, launcher:Launcher):
        """Handle incoming IPC connection"""
        socket = self.server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self.handle_message(socket, launcher))
    
    def handle_message(self, socket, launcher:Launcher):
        """Handle IPC message"""
        data = socket.readAll().data()
        if data == b"SHOW":
            launcher.show_window()
        socket.disconnectFromHost()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Launcher")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    app.setApplicationName("AI Launcher")

    # Single instance management
    single_instance = SingleInstanceApp()
    
    if single_instance.is_already_running():
        print("Application already running. Showing existing instance...")
        if single_instance.send_show_command():
            print("Show command sent successfully.")
        else:
            print("Failed to communicate with existing instance.")
        sys.exit(0)
    
    launcher = Launcher(debug=args.debug)
    
    # Setup IPC server for this instance
    if not single_instance.setup_ipc_server(launcher):
        print("Warning: Could not setup IPC server")
    
    launcher.show()
    
    try:
        sys.exit(app.exec_())
    finally:
        if single_instance.shared_memory:
            single_instance.shared_memory.detach()