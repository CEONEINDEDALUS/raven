import cv2
import numpy as np
import base64
import gc
import threading
import time
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, QPoint
from PyQt6.QtGui import QImage, QPixmap, QPainter, QRegion, QPolygon


class CameraOverlayThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        self.camera_index = 0
        self.frame_skip_counter = 0
        self.frame_skip_rate = 2
        
    def start_camera(self, camera_index=0):
        self.camera_index = camera_index
        self.running = True
        self.start()
        
    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.wait()
        
    def run(self):
        try:
            indices_to_try = [self.camera_index] + [i for i in range(10) if i != self.camera_index]
            self.cap = None
            
            for idx in indices_to_try:
                test_cap = cv2.VideoCapture(idx)
                if test_cap.isOpened():
                    ret, _ = test_cap.read()
                    if ret:
                        self.cap = test_cap
                        self.camera_index = idx
                        break
                    else:
                        test_cap.release()
                else:
                    if test_cap:
                        test_cap.release()
            
            if not self.cap or not self.cap.isOpened():
                self.error_occurred.emit("Could not open any camera device")
                return
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_FPS, 15)
            
            while self.running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.frame_skip_counter += 1
                    if self.frame_skip_counter >= self.frame_skip_rate:
                        self.frame_skip_counter = 0
                        self.frame_ready.emit(frame)
                else:
                    self.error_occurred.emit("Failed to read frame from camera")
                    break
                    
                time.sleep(0.01)
                    
        except Exception as e:
            self.error_occurred.emit(f"Camera error: {str(e)}")
        finally:
            if self.cap:
                self.cap.release()


class FShapedOverlay(QWidget):
    """F-shaped camera overlay window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Raven Vision")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self.vertical_width = 80
        self.vertical_height = 200
        self.horizontal_width = 120
        self.horizontal_height = 40
        self.bar_thickness = 8
        
        self.setFixedSize(self.horizontal_width + 10, self.vertical_height + 10)
        
        self.setup_ui()
        self.camera_thread = CameraOverlayThread()
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.error_occurred.connect(self.show_error)
        
        self.current_frame = None
        self.frame_buffer = None
        self.last_frame_time = 0
        self.frame_rate_limit = 10
        
    def setup_ui(self):
        """Setup the overlay UI with F-shaped layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.camera_labels = []
        
        self.vertical_label = QLabel()
        self.vertical_label.setFixedSize(self.vertical_width, self.vertical_height)
        self.vertical_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 34, 34, 180);
                border: 1px solid #00FFFF;
                border-radius: 4px;
            }
        """)
        self.vertical_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vertical_label.setText("📷")
        
        self.top_horizontal_label = QLabel()
        self.top_horizontal_label.setFixedSize(self.horizontal_width, self.horizontal_height)
        self.top_horizontal_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 34, 34, 180);
                border: 1px solid #00FFFF;
                border-radius: 4px;
            }
        """)
        self.top_horizontal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.top_horizontal_label.setText("VISION")
        
        self.middle_horizontal_label = QLabel()
        self.middle_horizontal_label.setFixedSize(self.horizontal_width - 20, self.horizontal_height)
        self.middle_horizontal_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 34, 34, 180);
                border: 1px solid #00FFFF;
                border-radius: 4px;
            }
        """)
        self.middle_horizontal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.middle_horizontal_label.setText("ACTIVE")
        
        self.vertical_label.move(5, 5)
        self.top_horizontal_label.move(self.vertical_width - 10, 5)
        self.middle_horizontal_label.move(self.vertical_width - 10, 60)
        
    def start_camera(self, camera_index=0):
        self.camera_thread.start_camera(camera_index)
        
    def update_frame(self, frame):
        """Update camera frame with RAM optimization"""
        try:
            current_time = time.time()
            
            if current_time - self.last_frame_time < (1.0 / self.frame_rate_limit):
                return
            self.last_frame_time = current_time
            
            self.current_frame = frame
            
            small_frame = cv2.resize(frame, (self.vertical_width - 10, self.vertical_height - 20))
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            height, width, channels = rgb_frame.shape
            bytes_per_line = channels * width
            
            qt_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            self.vertical_label.setPixmap(pixmap)
            
            if int(current_time) % 5 == 0:
                gc.collect()
                
        except Exception as e:
            self.show_error(f"Frame processing error: {str(e)}")
            
    def show_error(self, error_msg):
        """Show error in overlay"""
        self.vertical_label.setText("❌")
        self.vertical_label.setStyleSheet("""
            QLabel {
                background-color: rgba(68, 0, 0, 180);
                border: 1px solid #FF4444;
                border-radius: 4px;
                color: #FF4444;
            }
        """)
        
    def capture_frame_for_analysis(self):
        """Capture current frame and return it as base64 for LLM analysis"""
        try:
            if self.current_frame is not None:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                _, buffer = cv2.imencode('.jpg', self.current_frame, encode_param)
                base64_image = base64.b64encode(buffer).decode('utf-8')
                
                buffer = None
                return base64_image
            else:
                return None
        except Exception:
            pass
            return None
            
    def position_near_window(self, main_window):
        """Position the overlay near the main window's top-left corner"""
        if main_window:
            main_geo = main_window.geometry()
            
            overlay_x = main_geo.x() - self.width() - 10
            overlay_y = main_geo.y() + 30
            
            screen = self.screen()
            if screen:
                screen_geo = screen.geometry()
                if overlay_x < screen_geo.x():
                    overlay_x = main_geo.x() + main_geo.width() + 10
                if overlay_y < screen_geo.y():
                    overlay_y = screen_geo.y() + 10
                    
            self.move(overlay_x, overlay_y)
            
    def closeEvent(self, event):
        self.camera_thread.stop_camera()
        event.accept()


class CameraOverlayManager(QObject):
    """Manager class to handle camera overlay functionality for Raven"""
    
    open_overlay_signal = pyqtSignal(object)
    close_overlay_signal = pyqtSignal()
    position_overlay_signal = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.overlay = None
        self.main_window = None
        
        self.open_overlay_signal.connect(self._open_overlay_slot)
        self.close_overlay_signal.connect(self._close_overlay_slot)
        self.position_overlay_signal.connect(self._position_overlay_slot)
        
    def open_overlay(self, parent=None):
        """Open the camera overlay - thread-safe version"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QThread
            
            app = QApplication.instance()
            if app is None:
                return "Cannot open overlay: GUI not initialized"
                
            current_thread = QThread.currentThread()
            main_thread = app.thread()
            
            if current_thread != main_thread:
                self.open_overlay_signal.emit(parent)
                return "Overlay opening request sent"
            else:
                return self._create_overlay(parent)
                
        except Exception as e:
            return f"Failed to open overlay: {str(e)}"
    
    def _create_overlay(self, parent=None):
        """Actually create the overlay (must be called from main thread)"""
        try:
            if self.overlay is None or not self.overlay.isVisible():
                self.overlay = FShapedOverlay(None)
                if parent:
                    self.main_window = parent
                self.overlay.show()
                self.overlay.start_camera()
                
                if self.main_window:
                    self.overlay.position_near_window(self.main_window)
                    
                return "Camera overlay opened successfully"
            else:
                self.overlay.raise_()
                return "Camera overlay is already open"
        except Exception as e:
            return f"Failed to create overlay: {str(e)}"
    
    def _open_overlay_slot(self, parent):
        """Slot to handle open overlay signal (runs in main thread)"""
        self._create_overlay(parent)
    
    def close_overlay(self):
        """Close the camera overlay - thread-safe version"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QThread
            
            app = QApplication.instance()
            if app is None:
                return "Cannot close overlay: GUI not initialized"
                
            current_thread = QThread.currentThread()
            main_thread = app.thread()
            
            if current_thread != main_thread:
                self.close_overlay_signal.emit()
                return "Overlay close request sent"
            else:
                return self._close_overlay()
                
        except Exception as e:
            return f"Failed to close overlay: {str(e)}"
    
    def _close_overlay(self):
        """Actually close the overlay (must be called from main thread)"""
        try:
            if self.overlay and self.overlay.isVisible():
                self.overlay.close()
                self.overlay = None
                return "Camera overlay closed"
            else:
                return "Camera overlay is not open"
        except Exception as e:
            return f"Failed to close overlay: {str(e)}"
    
    def _close_overlay_slot(self):
        """Slot to handle close overlay signal (runs in main thread)"""
        self._close_overlay()
    
    def position_overlay(self, main_window):
        """Position overlay near main window - thread-safe version"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QThread
            
            app = QApplication.instance()
            if app is None:
                return
                
            current_thread = QThread.currentThread()
            main_thread = app.thread()
            
            if current_thread != main_thread:
                self.position_overlay_signal.emit(main_window)
            else:
                self._position_overlay_direct(main_window)
                
        except Exception:
            pass
    
    def _position_overlay_direct(self, main_window):
        """Direct positioning (must be called from main thread)"""
        if self.overlay and self.overlay.isVisible() and main_window:
            self.overlay.position_near_window(main_window)
    
    def _position_overlay_slot(self, main_window):
        """Slot to handle position overlay signal (runs in main thread)"""
        self._position_overlay_direct(main_window)
    
    def is_overlay_open(self):
        """Check if camera overlay is currently open"""
        return self.overlay is not None and self.overlay.isVisible()
    
    def is_camera_open(self):
        """Alias for is_overlay_open for backward compatibility"""
        return self.is_overlay_open()
    
    def open_camera(self, parent=None):
        """Alias for open_overlay for backward compatibility"""
        return self.open_overlay(parent)
    
    def close_camera(self):
        """Alias for close_overlay for backward compatibility"""
        return self.close_overlay()
    
    def capture_and_analyze_frame(self, vision_prompt="What do you see in this image?"):
        """Capture current frame and return it for analysis"""
        try:
            if self.overlay and self.overlay.isVisible():
                return self.overlay.capture_frame_for_analysis()
            else:
                return None
        except Exception:
            pass
            return None