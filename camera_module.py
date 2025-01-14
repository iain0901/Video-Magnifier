import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
import time

class CameraModule(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.camera = None
        self.running = False
        self.frame_width = 1920
        self.frame_height = 1080
        self.autofocus = True
        self.focus_value = 0
        self.current_frame = None
        
        # 初始化攝影機
        self.init_camera()
    
    def init_camera(self):
        """初始化攝影機，如果指定的攝影機無法開啟，則嘗試其他可用的攝影機"""
        print(f"嘗試開啟攝影機 {self.camera_id}...")
        
        # 首先嘗試使用 DirectShow
        self.camera = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        if not self.camera.isOpened():
            print("使用 DirectShow 開啟失敗，嘗試其他方式...")
            self.camera = cv2.VideoCapture(self.camera_id)
        
        # 如果仍然無法開啟，嘗試其他攝影機
        if not self.camera.isOpened():
            print("嘗試尋找可用的攝影機...")
            for i in range(5):  # 嘗試前5個攝影機
                if i == self.camera_id:
                    continue
                print(f"嘗試攝影機 {i}...")
                self.camera = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if self.camera.isOpened():
                    self.camera_id = i
                    print(f"成功開啟攝影機 {i}")
                    break
                self.camera = cv2.VideoCapture(i)
                if self.camera.isOpened():
                    self.camera_id = i
                    print(f"成功開啟攝影機 {i}")
                    break
        
        if not self.camera.isOpened():
            raise Exception("無法開啟任何攝影機，請確認攝影機是否正確連接")
        
        # 設定攝影機參數
        self.set_camera_properties()
    
    def set_camera_properties(self):
        """設定攝影機屬性"""
        try:
            # 設定解析度
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            
            # 設定自動對焦
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1 if self.autofocus else 0)
            
            # 如果是手動對焦，設定對焦值
            if not self.autofocus:
                self.camera.set(cv2.CAP_PROP_FOCUS, self.focus_value)
            
            # 獲取實際設定的解析度
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"攝影機實際解析度: {actual_width}x{actual_height}")
            
        except Exception as e:
            print(f"設定攝影機屬性時發生錯誤: {str(e)}")
    
    def run(self):
        """執行攝影機擷取執行緒"""
        self.running = True
        while self.running:
            if self.camera is None or not self.camera.isOpened():
                print("攝影機未開啟，嘗試重新初始化...")
                try:
                    self.init_camera()
                except Exception as e:
                    print(f"重新初始化攝影機失敗: {str(e)}")
                    time.sleep(1)
                    continue
            
            ret, frame = self.camera.read()
            if ret:
                # 轉換為 RGB 格式
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame = frame
                self.frame_ready.emit(frame)
            else:
                print("讀取影格失敗")
                time.sleep(0.1)
    
    def stop(self):
        """停止攝影機擷取"""
        self.running = False
        self.wait()
        if self.camera is not None:
            self.camera.release()
            self.camera = None
    
    def set_resolution(self, width, height):
        """設定攝影機解析度"""
        self.frame_width = width
        self.frame_height = height
        if self.camera is not None and self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    def set_focus(self, value):
        """設定對焦值"""
        self.focus_value = value
        self.autofocus = False
        if self.camera is not None and self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            self.camera.set(cv2.CAP_PROP_FOCUS, value)
    
    def set_autofocus(self, enabled):
        """設定自動對焦"""
        self.autofocus = enabled
        if self.camera is not None and self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1 if enabled else 0)
    
    def get_frame(self):
        """獲取當前的攝影機畫面"""
        if self.camera is None or not self.camera.isOpened():
            return None
            
        ret, frame = self.camera.read()
        if ret:
            # 轉換為 RGB 格式
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame = frame
            return frame
        return None