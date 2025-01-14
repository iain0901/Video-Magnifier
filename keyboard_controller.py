from pynput import keyboard
from PyQt5.QtCore import QObject, pyqtSignal

class KeyboardController(QObject):
    zoom_in_signal = pyqtSignal()
    zoom_out_signal = pyqtSignal()
    reset_signal = pyqtSignal()
    fullscreen_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.listener = None
        self.zoom_in_key = '+'
        self.zoom_out_key = '-'
        self.reset_key = '0'
        
    def on_press(self, key):
        """處理按鍵按下事件"""
        try:
            if key.char == self.zoom_in_key:
                self.zoom_in_signal.emit()
            elif key.char == self.zoom_out_key:
                self.zoom_out_signal.emit()
            elif key.char == self.reset_key:
                self.reset_signal.emit()
        except AttributeError:
            if key == keyboard.Key.f11:
                self.fullscreen_signal.emit()
            elif key == keyboard.Key.esc:
                return False
                
    def start(self):
        """開始監聽鍵盤事件"""
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
            
    def stop(self):
        """停止監聽鍵盤事件"""
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
            
    def update_keys(self, zoom_in_key, zoom_out_key, reset_key):
        """更新快捷鍵設定"""
        self.zoom_in_key = zoom_in_key
        self.zoom_out_key = zoom_out_key
        self.reset_key = reset_key 