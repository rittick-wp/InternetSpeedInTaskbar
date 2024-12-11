import sys
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDesktopWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, QEvent
from PyQt5.QtGui import QFont, QPainter, QColor, QPixmap
import win32gui
import win32con

class NetworkSpeedMonitor(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create a pixmap buffer to reduce flickering
        self.buffer = QPixmap()
        
        self.initUI()

        # Initial network stats
        self.prev_sent = psutil.net_io_counters().bytes_sent
        self.prev_recv = psutil.net_io_counters().bytes_recv

        # Timer to update network speed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_network_speed)
        self.timer.start(1000)

        # Timer to ensure always-on-top status
        self.always_on_top_timer = QTimer(self)
        self.always_on_top_timer.timeout.connect(self.ensure_always_on_top)
        self.always_on_top_timer.start(50)

    def initUI(self):
        # Comprehensive window flags to minimize blinking
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint |
            Qt.NoDropShadowWindowHint
        )

        # Advanced rendering optimizations
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Increase width to provide more space
        self.setFixedSize(120, 46)

        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 10, 10, 10)  # Increased left margin
        layout.setSpacing(3)

        # Upload speed label
        self.upload_label = QLabel('U: 0.00 KB/s')
        self.upload_label.setFont(QFont('Inter', 8))
        self.upload_label.setStyleSheet('color: #616161; background: transparent;')
        self.upload_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.upload_label)

        # Download speed label
        self.download_label = QLabel('D: 0.00 KB/s')
        self.download_label.setFont(QFont('Inter', 8))
        self.download_label.setStyleSheet('color: #616161; background: transparent;')
        self.download_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.download_label)

        self.setLayout(layout)

        # Position the window
        self.position_window()

    def position_window(self):
        screen = QDesktopWidget().screenGeometry()
        
        # More flexible positioning strategy
        x = screen.width() - self.width() - 260  # Small margin from right edge
        y = screen.height() - self.height() - 0  # Adjust to avoid taskbar
        
        self.move(x, y)

    def paintEvent(self, event):
        # Double-buffering technique to reduce flickering
        self.buffer = QPixmap(self.size())
        self.buffer.fill(Qt.transparent)
        
        painter = QPainter(self.buffer)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        
        # Slightly softer background with better anti-aliasing
        painter.setBrush(QColor(33, 33, 33, 1))
        painter.drawRoundedRect(self.rect(), 23, 23)
        
        painter.end()
        
        # Paint the buffer to screen
        screen_painter = QPainter(self)
        screen_painter.drawPixmap(0, 0, self.buffer)

    def update_network_speed(self):
        try:
            net_io_counters = psutil.net_io_counters()
            upload_speed = net_io_counters.bytes_sent - self.prev_sent
            download_speed = net_io_counters.bytes_recv - self.prev_recv

            self.upload_label.setText(f'U: {self.convert_bytes(upload_speed)}')
            self.download_label.setText(f'D: {self.convert_bytes(download_speed)}')

            self.prev_sent = net_io_counters.bytes_sent
            self.prev_recv = net_io_counters.bytes_recv

            # Trigger repaint with minimal overhead
            self.update()
        except Exception as e:
            print(f"Network speed update error: {e}")

    def convert_bytes(self, bytes_per_sec):
        if bytes_per_sec >= 1024 * 1024:
            return f'{bytes_per_sec / (1024 * 1024):.2f}  MB/S'
        elif bytes_per_sec >= 1024:
            return f'{bytes_per_sec / 1024:.2f}  KB/S'
        else:
            return f'{bytes_per_sec:.2f}  B/S'

    def ensure_always_on_top(self):
        """Advanced always-on-top maintenance."""
        try:
            hwnd = self.winId().__int__()
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | 
                win32con.SWP_NOSIZE | 
                win32con.SWP_NOACTIVATE | 
                win32con.SWP_ASYNCWINDOWPOS
            )
        except Exception as e:
            print(f"Always-on-top error: {e}")

def main():
    app = QApplication(sys.argv)
    
    # Optional: Improve overall application rendering
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    monitor = NetworkSpeedMonitor()
    monitor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()