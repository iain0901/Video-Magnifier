import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                          QHBoxLayout, QPushButton, QLabel, QStyle, QSizePolicy, QGroupBox, QComboBox, QSlider)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor, QIcon
from camera_module import CameraModule
from image_processor import ImageProcessor
from keyboard_controller import KeyboardController
from settings_dialog import SettingsDialog
import cv2
import os
from translations import get_text

class MagnifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('MagnifierApp', 'Settings')
        self.current_language = self.settings.value('language', 'zh_TW')
        self.mouse_pressed = False
        self.last_pos = None
        self.move_speed = 5
        self.invert_mouse = False
        self.is_recording = False
        self.video_writer = None
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.setWindowTitle(get_text('app_title', self.current_language))
        self.setGeometry(100, 100, 1280, 720)
        
        # 設置深色主題
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QGroupBox {
                color: #ffffff;
                font-size: 14px;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                margin-top: 12px;
            }
        """)
        
        # 初始化模組
        self.camera = CameraModule(self.settings.value('camera_id', 0, type=int))
        self.processor = ImageProcessor()
        self.keyboard = KeyboardController(self)
        
        # 設置主視窗
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 創建主佈局
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # 創建影像顯示區域
        self.image_widget = QWidget()
        self.image_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_layout.addWidget(self.image_label)
        self.image_widget.setLayout(self.image_layout)
        
        # 創建控制面板
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout()
        self.setup_controls()
        self.control_panel.setLayout(self.control_layout)
        
        # 根據設定配置佈局
        self.apply_layout_settings()
        
        # 設置定時器更新影像
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms = ~33fps
        
        # 啟動攝影機
        self.camera.frame_ready.connect(self.process_frame)
        self.camera.start()
        
    def setup_controls(self):
        """設置控制按鈕"""
        # 主控制面板
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout()
        
        # 1. 放大縮小控制（最常用）
        zoom_group = QGroupBox(get_text('zoom_control', self.current_language))
        zoom_group.setCheckable(True)
        zoom_group.setChecked(False)  # 預設收合
        zoom_layout = QVBoxLayout()
        zoom_content = QWidget()
        zoom_content_layout = QVBoxLayout()
        
        self.zoom_in_btn = QPushButton(get_text('zoom_in', self.current_language))
        self.zoom_out_btn = QPushButton(get_text('zoom_out', self.current_language))
        self.reset_btn = QPushButton(get_text('reset', self.current_language))
        
        for btn in [self.zoom_in_btn, self.zoom_out_btn, self.reset_btn]:
            btn.setMinimumHeight(40)
            zoom_content_layout.addWidget(btn)
            
        zoom_content.setLayout(zoom_content_layout)
        zoom_layout.addWidget(zoom_content)
        zoom_group.setLayout(zoom_layout)
        zoom_group.toggled.connect(lambda checked: zoom_content.setVisible(checked))
        zoom_content.setVisible(False)  # 預設隱藏
        self.control_layout.addWidget(zoom_group)
        
        # 2. 濾鏡控制（常用功能）
        filter_group = QGroupBox(get_text('filter', self.current_language))
        filter_group.setCheckable(True)
        filter_group.setChecked(False)  # 預設收合
        filter_layout = QVBoxLayout()
        filter_content = QWidget()
        filter_content_layout = QVBoxLayout()
        
        self.normal_btn = QPushButton(get_text('normal', self.current_language))
        self.contrast_btn = QPushButton(get_text('high_contrast', self.current_language))
        self.gray_btn = QPushButton(get_text('grayscale', self.current_language))
        self.inverse_btn = QPushButton(get_text('inverse', self.current_language))
        
        for btn in [self.normal_btn, self.contrast_btn, self.gray_btn, self.inverse_btn]:
            btn.setMinimumHeight(40)
            btn.setCheckable(True)
            filter_content_layout.addWidget(btn)
            
        filter_content.setLayout(filter_content_layout)
        filter_layout.addWidget(filter_content)
        filter_group.setLayout(filter_layout)
        filter_group.toggled.connect(lambda checked: filter_content.setVisible(checked))
        filter_content.setVisible(False)  # 預設隱藏
        self.control_layout.addWidget(filter_group)
        
        # 3. 顏色模式控制
        color_group = QGroupBox(get_text('color_mode', self.current_language))
        color_group.setCheckable(True)
        color_group.setChecked(False)  # 預設收合
        color_layout = QVBoxLayout()
        color_content = QWidget()
        color_content_layout = QVBoxLayout()
        
        self.color_combo = QComboBox()
        self.color_mode_map = {
            get_text('normal', self.current_language): 'normal',
            get_text('white_on_black', self.current_language): 'white_on_black',
            get_text('black_on_white', self.current_language): 'black_on_white',
            get_text('yellow_on_black', self.current_language): 'yellow_on_black',
            get_text('yellow_on_blue', self.current_language): 'yellow_on_blue',
            get_text('green_on_black', self.current_language): 'green_on_black',
            get_text('blue_on_yellow', self.current_language): 'blue_on_yellow'
        }
        self.color_combo.addItems(list(self.color_mode_map.keys()))
        color_content_layout.addWidget(self.color_combo)
        
        color_content.setLayout(color_content_layout)
        color_layout.addWidget(color_content)
        color_group.setLayout(color_layout)
        color_group.toggled.connect(lambda checked: color_content.setVisible(checked))
        color_content.setVisible(False)  # 預設隱藏
        self.control_layout.addWidget(color_group)
        
        # 4. 輔助功能
        assist_group = QGroupBox(get_text('assist', self.current_language))
        assist_group.setCheckable(True)
        assist_group.setChecked(False)  # 預設收合
        assist_layout = QVBoxLayout()
        assist_content = QWidget()
        assist_content_layout = QVBoxLayout()
        
        self.mask_btn = QPushButton(get_text('mask', self.current_language))
        self.guide_btn = QPushButton(get_text('guide_line', self.current_language))
        
        for btn in [self.mask_btn, self.guide_btn]:
            btn.setMinimumHeight(40)
            btn.setCheckable(True)
            assist_content_layout.addWidget(btn)
            
        assist_content.setLayout(assist_content_layout)
        assist_layout.addWidget(assist_content)
        assist_group.setLayout(assist_layout)
        assist_group.toggled.connect(lambda checked: assist_content.setVisible(checked))
        assist_content.setVisible(False)  # 預設隱藏
        self.control_layout.addWidget(assist_group)
        
        # 5. 影像變換控制
        transform_group = QGroupBox(get_text('image_transform', self.current_language))
        transform_group.setCheckable(True)
        transform_group.setChecked(False)  # 預設收合
        transform_layout = QVBoxLayout()
        transform_content = QWidget()
        transform_content_layout = QVBoxLayout()
        
        self.flip_h_btn = QPushButton(get_text('flip_h', self.current_language))
        self.flip_v_btn = QPushButton(get_text('flip_v', self.current_language))
        self.rotate_btn = QPushButton(get_text('rotate_90', self.current_language))
        
        self.flip_h_btn.setCheckable(True)
        self.flip_v_btn.setCheckable(True)
        
        for btn in [self.flip_h_btn, self.flip_v_btn, self.rotate_btn]:
            btn.setMinimumHeight(40)
            transform_content_layout.addWidget(btn)
            
        transform_content.setLayout(transform_content_layout)
        transform_layout.addWidget(transform_content)
        transform_group.setLayout(transform_layout)
        transform_group.toggled.connect(lambda checked: transform_content.setVisible(checked))
        transform_content.setVisible(False)  # 預設隱藏
        self.control_layout.addWidget(transform_group)
        
        # 6. 功能按鈕
        function_group = QGroupBox(get_text('functions', self.current_language))
        function_group.setCheckable(True)
        function_group.setChecked(False)  # 預設收合
        function_layout = QVBoxLayout()
        function_content = QWidget()
        function_content_layout = QVBoxLayout()
        
        self.screenshot_btn = QPushButton(get_text('screenshot', self.current_language))
        self.record_btn = QPushButton(get_text('start_recording', self.current_language))
        self.settings_btn = QPushButton(get_text('settings', self.current_language))
        self.fullscreen_btn = QPushButton(get_text('fullscreen', self.current_language))
        
        for btn in [self.screenshot_btn, self.record_btn, self.settings_btn, self.fullscreen_btn]:
            btn.setMinimumHeight(40)
            function_content_layout.addWidget(btn)
            
        function_content.setLayout(function_content_layout)
        function_layout.addWidget(function_content)
        function_group.setLayout(function_layout)
        function_group.toggled.connect(lambda checked: function_content.setVisible(checked))
        function_content.setVisible(False)  # 預設隱藏
        self.control_layout.addWidget(function_group)
        
        # 7. 亮度控制（移到最下方）
        brightness_group = QGroupBox(get_text('brightness_control', self.current_language))
        brightness_group.setCheckable(True)
        brightness_group.setChecked(False)  # 預設收合
        brightness_layout = QVBoxLayout()
        brightness_content = QWidget()
        brightness_content_layout = QVBoxLayout()
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(lambda v: self.processor.set_brightness(v))
        brightness_content_layout.addWidget(self.brightness_slider)
        
        brightness_content.setLayout(brightness_content_layout)
        brightness_layout.addWidget(brightness_content)
        brightness_group.setLayout(brightness_layout)
        brightness_group.toggled.connect(lambda checked: brightness_content.setVisible(checked))
        brightness_content.setVisible(False)  # 預設隱藏
        self.control_layout.addWidget(brightness_group)
        
        # 添加彈性空間
        self.control_layout.addStretch()
        
        # 設置控制面板
        self.control_panel.setLayout(self.control_layout)
        
        # 儲存功能組引用
        self.zoom_group = zoom_group
        self.brightness_group = brightness_group
        self.filter_group = filter_group
        self.color_group = color_group
        self.assist_group = assist_group
        self.transform_group = transform_group
        self.function_group = function_group
        
        # 連接信號
        self.connect_signals()
        
    def toggle_advanced_controls(self):
        """切換進階控制的顯示狀態"""
        if self.advanced_container.isVisible():
            self.advanced_container.hide()
            self.expand_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        else:
            self.advanced_container.show()
            self.expand_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
            
    def connect_signals(self):
        """連接所有信號"""
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_btn.clicked.connect(self.reset_zoom)
        
        self.color_combo.currentTextChanged.connect(self.change_color_mode)
        
        self.normal_btn.clicked.connect(lambda: self.processor.set_filter_mode('normal'))
        self.contrast_btn.clicked.connect(lambda: self.processor.set_filter_mode('high_contrast'))
        self.gray_btn.clicked.connect(lambda: self.processor.set_filter_mode('grayscale'))
        self.inverse_btn.clicked.connect(lambda: self.processor.set_filter_mode('inverse'))
        
        self.mask_btn.clicked.connect(lambda: self.processor.toggle_mask(self.mask_btn.isChecked()))
        self.guide_btn.clicked.connect(lambda: self.processor.toggle_guide_line(self.guide_btn.isChecked()))
        
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.settings_btn.clicked.connect(self.show_settings)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        
        self.flip_h_btn.clicked.connect(self.toggle_horizontal_flip)
        self.flip_v_btn.clicked.connect(self.toggle_vertical_flip)
        self.rotate_btn.clicked.connect(self.rotate_image)
        
    def change_language(self, text):
        """變更語言"""
        self.current_language = 'zh_TW' if text == '繁體中文' else 'en_US'
        self.settings.setValue('language', self.current_language)
        self.settings.sync()
        
        # 更新所有文字
        self.setWindowTitle(get_text('app_title', self.current_language))
        self.retranslate_ui()
        
    def retranslate_ui(self):
        """更新界面文字"""
        # 更新按鈕文字
        self.zoom_in_btn.setText(get_text('zoom_in', self.current_language))
        self.zoom_out_btn.setText(get_text('zoom_out', self.current_language))
        self.reset_btn.setText(get_text('reset', self.current_language))
        
        self.normal_btn.setText(get_text('normal', self.current_language))
        self.contrast_btn.setText(get_text('high_contrast', self.current_language))
        self.gray_btn.setText(get_text('grayscale', self.current_language))
        self.inverse_btn.setText(get_text('inverse', self.current_language))
        
        self.mask_btn.setText(get_text('mask', self.current_language))
        self.guide_btn.setText(get_text('guide_line', self.current_language))
        
        self.screenshot_btn.setText(get_text('screenshot', self.current_language))
        self.record_btn.setText(get_text('start_recording' if not self.is_recording else 'stop_recording', 
                                       self.current_language))
        self.settings_btn.setText(get_text('settings', self.current_language))
        self.fullscreen_btn.setText(get_text('fullscreen' if not self.isFullScreen() else 'exit_fullscreen', 
                                           self.current_language))
        
        self.flip_h_btn.setText(get_text('flip_h', self.current_language))
        self.flip_v_btn.setText(get_text('flip_v', self.current_language))
        self.rotate_btn.setText(get_text('rotate_90', self.current_language))
        
        # 更新下拉選單選項
        current_mode = self.color_combo.currentText()
        self.color_combo.clear()
        self.color_combo.addItems([
            get_text('normal', self.current_language),
            get_text('white_on_black', self.current_language),
            get_text('black_on_white', self.current_language),
            get_text('yellow_on_black', self.current_language),
            get_text('yellow_on_blue', self.current_language),
            get_text('green_on_black', self.current_language),
            get_text('blue_on_yellow', self.current_language)
        ])
        
        # 更新顏色模式映射
        self.color_mode_map = {
            get_text('normal', self.current_language): 'normal',
            get_text('white_on_black', self.current_language): 'white_on_black',
            get_text('black_on_white', self.current_language): 'black_on_white',
            get_text('yellow_on_black', self.current_language): 'yellow_on_black',
            get_text('yellow_on_blue', self.current_language): 'yellow_on_blue',
            get_text('green_on_black', self.current_language): 'green_on_black',
            get_text('blue_on_yellow', self.current_language): 'blue_on_yellow'
        }
        
        # 更新分組框標題
        for group in self.findChildren(QGroupBox):
            if group.title() == '縮放控制' or group.title() == 'Zoom Control':
                group.setTitle(get_text('zoom_control', self.current_language))
            elif group.title() == '顏色模式' or group.title() == 'Color Mode':
                group.setTitle(get_text('color_mode', self.current_language))
            elif group.title() == '濾鏡' or group.title() == 'Filter':
                group.setTitle(get_text('filter', self.current_language))
            elif group.title() == '輔助功能' or group.title() == 'Assistance':
                group.setTitle(get_text('assist', self.current_language))
            elif group.title() == '功能' or group.title() == 'Functions':
                group.setTitle(get_text('functions', self.current_language))
            elif group.title() == '影像變換' or group.title() == 'Image Transform':
                group.setTitle(get_text('image_transform', self.current_language))
        
    def change_color_mode(self, text):
        """變更顏色模式"""
        mode = self.color_mode_map.get(text, 'normal')
        self.processor.set_color_mode(mode)
        # 強制更新畫面
        if self.processor.last_frame is not None:
            self.process_frame(self.processor.last_frame)
        
    def apply_layout_settings(self):
        """應用佈局設定"""
        self.main_layout.removeWidget(self.image_widget)
        self.main_layout.removeWidget(self.control_panel)
        
        position = self.settings.value('button_position', '右側')
        control_width = self.settings.value('control_width', 20, type=int)
        
        # 設置控制面板寬度
        self.control_panel.setFixedWidth(int(self.width() * control_width / 100))
        
        if position == '右側':
            self.main_layout.addWidget(self.image_widget)
            self.main_layout.addWidget(self.control_panel)
        elif position == '左側':
            self.main_layout.addWidget(self.control_panel)
            self.main_layout.addWidget(self.image_widget)
        elif position in ['頂部', '底部']:
            self.main_layout = QVBoxLayout()
            self.central_widget.setLayout(self.main_layout)
            self.control_panel.setFixedHeight(100)
            if position == '頂部':
                self.main_layout.addWidget(self.control_panel)
                self.main_layout.addWidget(self.image_widget)
            else:
                self.main_layout.addWidget(self.image_widget)
                self.main_layout.addWidget(self.control_panel)
                
    def process_frame(self, frame):
        """處理攝影機影像"""
        if frame is not None:
            processed_frame = self.processor.process_frame(frame)
            if processed_frame is not None:
                # 如果正在錄影，寫入影片
                if self.is_recording and self.video_writer is not None:
                    # 調整影片大小以符合設定的品質
                    video_quality = self.settings.value('video_quality', '高品質')
                    if video_quality != '高品質':
                        height, width = processed_frame.shape[:2]
                        if video_quality == '低品質':
                            width = width // 2
                            height = height // 2
                        else:  # 中等品質
                            width = int(width * 0.75)
                            height = int(height * 0.75)
                        processed_frame = cv2.resize(processed_frame, (width, height))
                    
                    # 轉換顏色空間並寫入影片
                    self.video_writer.write(cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR))
                
                # 顯示影像
                height, width, channel = processed_frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(processed_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(q_image).scaled(
                    self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    
    def update_frame(self):
        """更新影像"""
        frame = self.camera.get_frame()
        if frame is not None:
            self.process_frame(frame)
            
    def zoom_in(self):
        """放大影像"""
        self.processor.zoom_in()
        
    def zoom_out(self):
        """縮小影像"""
        self.processor.zoom_out()
        
    def reset_zoom(self):
        """重置縮放"""
        self.processor.reset_zoom()
        
    def take_screenshot(self):
        """截圖"""
        from datetime import datetime
        screenshot_path = self.settings.value('screenshot_path', os.path.expanduser('~/Pictures'))
        screenshot_format = self.settings.value('screenshot_format', 'PNG').lower()
        filename = os.path.join(screenshot_path, f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{screenshot_format}')
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # 儲存截圖
        frame = self.camera.get_frame()
        if frame is not None:
            cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
    def toggle_recording(self):
        """切換錄影狀態"""
        if not self.is_recording:
            # 開始錄影
            from datetime import datetime
            recording_path = self.settings.value('recording_path', os.path.expanduser('~/Videos'))
            video_format = self.settings.value('video_format', 'MP4').lower()
            video_quality = self.settings.value('video_quality', '高品質')
            
            # 確保目錄存在
            os.makedirs(recording_path, exist_ok=True)
            
            # 設置檔案名稱
            filename = os.path.join(recording_path, f'recording_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{video_format}')
            
            # 設置編碼器和品質
            if video_format == 'mp4':
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            elif video_format == 'avi':
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
            else:  # wmv
                fourcc = cv2.VideoWriter_fourcc(*'WMV1')
                
            # 設置解析度和幀率
            frame = self.camera.get_frame()
            if frame is not None:
                height, width = frame.shape[:2]
                
                # 根據品質設置解析度
                if video_quality == '低品質':
                    width = width // 2
                    height = height // 2
                elif video_quality == '中等品質':
                    width = int(width * 0.75)
                    height = int(height * 0.75)
                
                self.video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (width, height))
                self.is_recording = True
                self.record_btn.setText('停止錄影')
                self.record_btn.setStyleSheet('background-color: #ff4444;')
        else:
            # 停止錄影
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
            self.is_recording = False
            self.record_btn.setText('開始錄影')
            self.record_btn.setStyleSheet('')
            
    def show_settings(self):
        """顯示設定對話框"""
        dialog = SettingsDialog(self)
        dialog.exec_()
        
    def toggle_fullscreen(self):
        """切換全螢幕"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText('全螢幕')
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText('退出全螢幕')
            
    def apply_settings(self):
        """應用新的設定"""
        try:
            # 停止當前的攝影機
            if hasattr(self, 'camera'):
                self.timer.stop()  # 停止更新定時器
                self.camera.stop()
                self.camera.release()
                
            # 斷開所有信號連接
            try:
                self.camera.frame_ready.disconnect()
            except:
                pass
                
            # 重新創建攝影機
            camera_id = self.settings.value('camera_id', 0, type=int)
            self.camera = CameraModule(camera_id)
            
            # 設置攝影機參數
            self.camera.set_autofocus(self.settings.value('autofocus', True, type=bool))
            self.camera.set_focus(self.settings.value('focus_value', 50, type=int))
            
            # 設置解析度
            width = self.settings.value('width', 1280, type=int)
            height = self.settings.value('height', 720, type=int)
            self.camera.set_resolution(width, height)
            
            # 更新影像變換設定
            self.camera.set_flip(
                horizontal=self.settings.value('flip_horizontal', False, type=bool),
                vertical=self.settings.value('flip_vertical', False, type=bool)
            )
            self.camera.set_rotation(self.settings.value('rotation_angle', 0, type=int))
            
            # 更新按鈕狀態
            self.flip_h_btn.setChecked(self.settings.value('flip_horizontal', False, type=bool))
            self.flip_v_btn.setChecked(self.settings.value('flip_vertical', False, type=bool))
            
            # 更新移動控制
            self.move_speed = self.settings.value('move_speed', 5, type=int)
            self.invert_mouse = self.settings.value('invert_mouse', False, type=bool)
            
            # 更新快捷鍵
            self.keyboard.update_keys(
                self.settings.value('zoom_in_key', '+'),
                self.settings.value('zoom_out_key', '-'),
                self.settings.value('reset_key', '0')
            )
            
            # 更新佈局
            self.apply_layout_settings()
            
            # 更新顏色模式
            color_text = next((k for k, v in self.color_mode_map.items() 
                             if v == self.settings.value('color_mode', 'normal')), '正常')
            self.color_combo.setCurrentText(color_text)
            
            # 如果需要全螢幕
            if self.settings.value('fullscreen', False, type=bool):
                self.showFullScreen()
                self.fullscreen_btn.setText('退出全螢幕')
            
            # 重新連接信號並啟動攝影機
            self.camera.frame_ready.connect(self.process_frame)
            self.camera.start()
            
            # 重新啟動更新定時器
            self.timer.start(30)
            
            # 更新功能塊顯示狀態
            self.zoom_group.setVisible(self.settings.value('show_zoom', True, type=bool))
            self.color_group.setVisible(self.settings.value('show_color', True, type=bool))
            self.filter_group.setVisible(self.settings.value('show_filter', True, type=bool))
            self.assist_group.setVisible(self.settings.value('show_assist', True, type=bool))
            self.transform_group.setVisible(self.settings.value('show_transform', True, type=bool))
            self.function_group.setVisible(self.settings.value('show_function', True, type=bool))
            
            print(f"成功切換到攝影機 {camera_id}")
            
        except Exception as e:
            print(f"切換攝影機時發生錯誤: {str(e)}")
            # 如果切換失敗，嘗試回到預設攝影機
            try:
                self.camera = CameraModule(0)
                self.camera.frame_ready.connect(self.process_frame)
                self.camera.start()
                self.timer.start(30)
                print("已回到預設攝影機")
            except Exception as e2:
                print(f"無法回到預設攝影機: {str(e2)}")
        
    def load_settings(self):
        """載入設定"""
        if self.settings.value('fullscreen', False, type=bool):
            self.showFullScreen()
            self.fullscreen_btn.setText('退出全螢幕')
            
    def closeEvent(self, event):
        """關閉程式時的清理工作"""
        # 停止錄影
        if self.is_recording:
            self.toggle_recording()
            
        self.keyboard.stop()
        self.camera.stop()
        self.camera.release()
        event.accept()
        
    def mousePressEvent(self, event):
        """滑鼠按下事件"""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.last_pos = event.pos()
            
    def mouseReleaseEvent(self, event):
        """滑鼠釋放事件"""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
            
    def mouseMoveEvent(self, event):
        """滑鼠移動事件"""
        if self.mouse_pressed and self.last_pos is not None:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            
            if self.invert_mouse:
                dx = -dx
                dy = -dy
                
            # 根據移動速度調整
            dx = dx * self.move_speed // 5
            dy = dy * self.move_speed // 5
            
            # 移動影像處理器的視野
            self.processor.move(-dx, -dy)
            
            self.last_pos = event.pos()
            
    def keyPressEvent(self, event):
        """鍵盤按下事件"""
        speed = self.move_speed * 5
        if event.text().upper() == self.settings.value('move_up_key', 'W'):
            self.processor.move(0, -speed)
        elif event.text().upper() == self.settings.value('move_down_key', 'S'):
            self.processor.move(0, speed)
        elif event.text().upper() == self.settings.value('move_left_key', 'A'):
            self.processor.move(-speed, 0)
        elif event.text().upper() == self.settings.value('move_right_key', 'D'):
            self.processor.move(speed, 0)
        else:
            super().keyPressEvent(event)
        
    def toggle_horizontal_flip(self):
        """切換水平翻轉"""
        self.camera.set_flip(horizontal=self.flip_h_btn.isChecked())
        
    def toggle_vertical_flip(self):
        """切換垂直翻轉"""
        self.camera.set_flip(vertical=self.flip_v_btn.isChecked())
        
    def rotate_image(self):
        """旋轉影像"""
        current_angle = self.settings.value('rotation_angle', 0, type=int)
        new_angle = (current_angle + 90) % 360
        self.camera.set_rotation(new_angle)
        self.settings.setValue('rotation_angle', new_angle)
        
    def toggle_group_content(self, layout, show):
        """切換功能塊內容的顯示狀態"""
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setVisible(show)
                
def main():
    app = QApplication(sys.argv)
    window = MagnifierApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 