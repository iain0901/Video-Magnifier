from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox, 
                            QLabel, QPushButton, QGroupBox, QSpinBox, QCheckBox,
                            QTabWidget, QWidget, QGridLayout, QLineEdit, QSlider, QFileDialog)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont
import cv2
import os
from translations import get_text

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings('MagnifierApp', 'Settings')
        self.current_language = self.settings.value('language', 'zh_TW')
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QGroupBox {
                color: #ffffff;
                font-size: 14px;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                margin-top: 12px;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QSpinBox {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
            }
            QSlider {
                background-color: transparent;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #3d3d3d;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: none;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4d4d4d;
            }
        """)
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.setWindowTitle(get_text('settings_title', self.current_language))
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # 創建分頁
        tab_widget = QTabWidget()
        
        # 攝影機設定分頁
        camera_tab = QWidget()
        camera_layout = QVBoxLayout()
        
        # 攝影機選擇
        camera_group = QGroupBox(get_text('camera_settings', self.current_language))
        camera_group_layout = QGridLayout()
        
        camera_label = QLabel(get_text('select_camera', self.current_language))
        self.camera_combo = QComboBox()
        self.refresh_camera_list()
        
        # 自動對焦設定
        self.autofocus_check = QCheckBox(get_text('enable_autofocus', self.current_language))
        self.focus_value = QSlider(Qt.Horizontal)
        self.focus_value.setRange(0, 100)
        self.focus_value.setValue(50)
        self.focus_value.setEnabled(False)
        
        camera_group_layout.addWidget(camera_label, 0, 0)
        camera_group_layout.addWidget(self.camera_combo, 0, 1)
        camera_group_layout.addWidget(self.autofocus_check, 1, 0)
        camera_group_layout.addWidget(self.focus_value, 1, 1)
        
        camera_group.setLayout(camera_group_layout)
        camera_layout.addWidget(camera_group)
        
        # 解析度設定
        resolution_group = QGroupBox(get_text('resolution', self.current_language))
        resolution_layout = QGridLayout()
        
        resolution_layout.addWidget(QLabel(get_text('width', self.current_language)), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(640, 3840)
        self.width_spin.setValue(1280)
        resolution_layout.addWidget(self.width_spin, 0, 1)
        
        resolution_layout.addWidget(QLabel(get_text('height', self.current_language)), 1, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(480, 2160)
        self.height_spin.setValue(720)
        resolution_layout.addWidget(self.height_spin, 1, 1)
        
        resolution_group.setLayout(resolution_layout)
        camera_layout.addWidget(resolution_group)
        
        camera_tab.setLayout(camera_layout)
        
        # 遮罩設定分頁
        mask_tab = QWidget()
        mask_layout = QVBoxLayout()
        
        mask_group = QGroupBox(get_text('mask_settings', self.current_language))
        mask_grid = QGridLayout()
        
        self.mask_mode = QComboBox()
        self.mask_mode.addItems([
            get_text('horizontal_mask', self.current_language),
            get_text('vertical_mask', self.current_language),
            get_text('rectangle_mask', self.current_language),
            get_text('ellipse_mask', self.current_language)
        ])
        mask_grid.addWidget(QLabel(get_text('mask_mode', self.current_language)), 0, 0)
        mask_grid.addWidget(self.mask_mode, 0, 1)
        
        self.mask_opacity = QSlider(Qt.Horizontal)
        self.mask_opacity.setRange(0, 100)
        self.mask_opacity.setValue(50)
        mask_grid.addWidget(QLabel(get_text('mask_opacity', self.current_language)), 1, 0)
        mask_grid.addWidget(self.mask_opacity, 1, 1)
        
        self.mask_size = QSlider(Qt.Horizontal)
        self.mask_size.setRange(10, 90)
        self.mask_size.setValue(30)
        mask_grid.addWidget(QLabel(get_text('mask_size', self.current_language)), 2, 0)
        mask_grid.addWidget(self.mask_size, 2, 1)
        
        mask_group.setLayout(mask_grid)
        mask_layout.addWidget(mask_group)
        mask_tab.setLayout(mask_layout)
        
        # 輔助線設定分頁
        guide_tab = QWidget()
        guide_layout = QVBoxLayout()
        
        guide_group = QGroupBox(get_text('guide_settings', self.current_language))
        guide_grid = QGridLayout()
        
        self.guide_mode = QComboBox()
        self.guide_mode.addItems([
            get_text('cross', self.current_language),
            get_text('grid', self.current_language),
            get_text('center', self.current_language),
            get_text('reading_line', self.current_language)
        ])
        guide_grid.addWidget(QLabel(get_text('guide_mode', self.current_language)), 0, 0)
        guide_grid.addWidget(self.guide_mode, 0, 1)
        
        self.guide_color = QComboBox()
        self.guide_color.addItems([
            get_text('green', self.current_language),
            get_text('red', self.current_language),
            get_text('blue', self.current_language),
            get_text('yellow', self.current_language),
            get_text('white', self.current_language)
        ])
        guide_grid.addWidget(QLabel(get_text('guide_color', self.current_language)), 1, 0)
        guide_grid.addWidget(self.guide_color, 1, 1)
        
        self.guide_thickness = QSpinBox()
        self.guide_thickness.setRange(1, 5)
        self.guide_thickness.setValue(1)
        guide_grid.addWidget(QLabel(get_text('guide_thickness', self.current_language)), 2, 0)
        guide_grid.addWidget(self.guide_thickness, 2, 1)
        
        guide_group.setLayout(guide_grid)
        guide_layout.addWidget(guide_group)
        guide_tab.setLayout(guide_layout)
        
        # 控制設定分頁
        control_tab = QWidget()
        control_layout = QVBoxLayout()
        
        # 移動控制設定
        move_group = QGroupBox(get_text('move_control', self.current_language))
        move_grid = QGridLayout()
        
        self.move_speed = QSpinBox()
        self.move_speed.setRange(1, 10)
        self.move_speed.setValue(5)
        move_grid.addWidget(QLabel(get_text('move_speed', self.current_language)), 0, 0)
        move_grid.addWidget(self.move_speed, 0, 1)
        
        self.invert_mouse = QCheckBox(get_text('invert_mouse', self.current_language))
        move_grid.addWidget(self.invert_mouse, 1, 0, 1, 2)
        
        move_group.setLayout(move_grid)
        control_layout.addWidget(move_group)
        
        # 快捷鍵設定
        shortcut_group = QGroupBox(get_text('shortcut_settings', self.current_language))
        shortcut_grid = QGridLayout()
        
        shortcut_grid.addWidget(QLabel(get_text('zoom_in', self.current_language)), 0, 0)
        self.zoom_in_key = QLineEdit('+')
        shortcut_grid.addWidget(self.zoom_in_key, 0, 1)
        
        shortcut_grid.addWidget(QLabel(get_text('zoom_out', self.current_language)), 1, 0)
        self.zoom_out_key = QLineEdit('-')
        shortcut_grid.addWidget(self.zoom_out_key, 1, 1)
        
        shortcut_grid.addWidget(QLabel(get_text('reset', self.current_language)), 2, 0)
        self.reset_key = QLineEdit('0')
        shortcut_grid.addWidget(self.reset_key, 2, 1)
        
        shortcut_grid.addWidget(QLabel(get_text('move_up', self.current_language)), 3, 0)
        self.move_up_key = QLineEdit('W')
        shortcut_grid.addWidget(self.move_up_key, 3, 1)
        
        shortcut_grid.addWidget(QLabel(get_text('move_down', self.current_language)), 4, 0)
        self.move_down_key = QLineEdit('S')
        shortcut_grid.addWidget(self.move_down_key, 4, 1)
        
        shortcut_grid.addWidget(QLabel(get_text('move_left', self.current_language)), 5, 0)
        self.move_left_key = QLineEdit('A')
        shortcut_grid.addWidget(self.move_left_key, 5, 1)
        
        shortcut_grid.addWidget(QLabel(get_text('move_right', self.current_language)), 6, 0)
        self.move_right_key = QLineEdit('D')
        shortcut_grid.addWidget(self.move_right_key, 6, 1)
        
        shortcut_group.setLayout(shortcut_grid)
        control_layout.addWidget(shortcut_group)
        
        # 影像變換設定
        transform_group = QGroupBox(get_text('image_transform', self.current_language))
        transform_grid = QGridLayout()
        
        # 翻轉設定
        self.flip_horizontal = QCheckBox(get_text('flip_horizontal', self.current_language))
        self.flip_vertical = QCheckBox(get_text('flip_vertical', self.current_language))
        transform_grid.addWidget(self.flip_horizontal, 0, 0)
        transform_grid.addWidget(self.flip_vertical, 0, 1)
        
        # 旋轉設定
        transform_grid.addWidget(QLabel(get_text('rotation_angle', self.current_language)), 1, 0)
        self.rotation_angle = QComboBox()
        self.rotation_angle.addItems(['0°', '90°', '180°', '270°'])
        transform_grid.addWidget(self.rotation_angle, 1, 1)
        
        transform_group.setLayout(transform_grid)
        control_layout.addWidget(transform_group)
        
        control_tab.setLayout(control_layout)
        
        # 介面設定分頁
        ui_tab = QWidget()
        ui_layout = QVBoxLayout()
        
        layout_group = QGroupBox(get_text('interface_settings', self.current_language))
        layout_grid = QGridLayout()
        
        self.fullscreen_check = QCheckBox(get_text('fullscreen', self.current_language))
        layout_grid.addWidget(self.fullscreen_check, 0, 0)
        
        layout_grid.addWidget(QLabel(get_text('button_position', self.current_language)), 1, 0)
        self.button_position = QComboBox()
        self.button_position.addItems([
            get_text('right', self.current_language),
            get_text('left', self.current_language),
            get_text('top', self.current_language),
            get_text('bottom', self.current_language)
        ])
        layout_grid.addWidget(self.button_position, 1, 1)
        
        layout_grid.addWidget(QLabel(get_text('control_width', self.current_language)), 2, 0)
        self.control_width = QSpinBox()
        self.control_width.setRange(10, 30)
        self.control_width.setValue(20)
        self.control_width.setSuffix('%')
        layout_grid.addWidget(self.control_width, 2, 1)
        
        layout_grid.addWidget(QLabel(get_text('language', self.current_language)), 3, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(['繁體中文', 'English'])
        self.language_combo.setCurrentText('繁體中文' if self.current_language == 'zh_TW' else 'English')
        layout_grid.addWidget(self.language_combo, 3, 1)
        
        # 添加功能塊顯示控制
        function_group = QGroupBox(get_text('function_display', self.current_language))
        function_grid = QGridLayout()
        
        self.show_zoom = QCheckBox(get_text('show_zoom_control', self.current_language))
        self.show_color = QCheckBox(get_text('show_color_mode', self.current_language))
        self.show_filter = QCheckBox(get_text('show_filter', self.current_language))
        self.show_assist = QCheckBox(get_text('show_assist', self.current_language))
        self.show_transform = QCheckBox(get_text('show_transform', self.current_language))
        self.show_function = QCheckBox(get_text('show_function', self.current_language))
        
        function_grid.addWidget(self.show_zoom, 0, 0)
        function_grid.addWidget(self.show_color, 0, 1)
        function_grid.addWidget(self.show_filter, 1, 0)
        function_grid.addWidget(self.show_assist, 1, 1)
        function_grid.addWidget(self.show_transform, 2, 0)
        function_grid.addWidget(self.show_function, 2, 1)
        
        function_group.setLayout(function_grid)
        ui_layout.addWidget(function_group)
        
        layout_group.setLayout(layout_grid)
        ui_layout.addWidget(layout_group)
        ui_tab.setLayout(ui_layout)
        
        # 新增儲存設定分頁
        save_tab = QWidget()
        save_layout = QVBoxLayout()
        
        # 截圖設定
        screenshot_group = QGroupBox(get_text('screenshot_settings', self.current_language))
        screenshot_grid = QGridLayout()
        
        screenshot_grid.addWidget(QLabel(get_text('screenshot_path', self.current_language)), 0, 0)
        self.screenshot_path = QLineEdit()
        self.screenshot_path.setText(os.path.expanduser('~/Pictures'))
        browse_screenshot = QPushButton(get_text('browse', self.current_language))
        browse_screenshot.clicked.connect(lambda: self.browse_folder(self.screenshot_path))
        screenshot_grid.addWidget(self.screenshot_path, 0, 1)
        screenshot_grid.addWidget(browse_screenshot, 0, 2)
        
        screenshot_grid.addWidget(QLabel(get_text('screenshot_format', self.current_language)), 1, 0)
        self.screenshot_format = QComboBox()
        self.screenshot_format.addItems(['PNG', 'JPG', 'BMP'])
        screenshot_grid.addWidget(self.screenshot_format, 1, 1)
        
        screenshot_group.setLayout(screenshot_grid)
        save_layout.addWidget(screenshot_group)
        
        # 錄影設定
        recording_group = QGroupBox(get_text('recording_settings', self.current_language))
        recording_grid = QGridLayout()
        
        recording_grid.addWidget(QLabel(get_text('recording_path', self.current_language)), 0, 0)
        self.recording_path = QLineEdit()
        self.recording_path.setText(os.path.expanduser('~/Videos'))
        browse_recording = QPushButton(get_text('browse', self.current_language))
        browse_recording.clicked.connect(lambda: self.browse_folder(self.recording_path))
        recording_grid.addWidget(self.recording_path, 0, 1)
        recording_grid.addWidget(browse_recording, 0, 2)
        
        recording_grid.addWidget(QLabel(get_text('video_format', self.current_language)), 1, 0)
        self.video_format = QComboBox()
        self.video_format.addItems(['MP4', 'AVI', 'WMV'])
        recording_grid.addWidget(self.video_format, 1, 1)
        
        recording_grid.addWidget(QLabel(get_text('video_quality', self.current_language)), 2, 0)
        self.video_quality = QComboBox()
        self.video_quality.addItems([
            get_text('high_quality', self.current_language),
            get_text('medium_quality', self.current_language),
            get_text('low_quality', self.current_language)
        ])
        recording_grid.addWidget(self.video_quality, 2, 1)
        
        recording_grid.addWidget(QLabel(get_text('audio_source', self.current_language)), 3, 0)
        self.audio_source = QComboBox()
        self.audio_source.addItems([
            get_text('none', self.current_language),
            get_text('system_audio', self.current_language),
            get_text('microphone', self.current_language)
        ])
        recording_grid.addWidget(self.audio_source, 3, 1)
        
        recording_group.setLayout(recording_grid)
        save_layout.addWidget(recording_group)
        
        save_tab.setLayout(save_layout)
        
        # 添加顏色設定分頁
        color_tab = QWidget()
        color_layout = QVBoxLayout()
        
        # 對比色設定
        contrast_group = QGroupBox(get_text('contrast_settings', self.current_language))
        contrast_grid = QGridLayout()
        
        # 前景色設定
        contrast_grid.addWidget(QLabel(get_text('foreground_color', self.current_language)), 0, 0)
        self.foreground_color = QComboBox()
        self.foreground_color.addItems([
            get_text('white', self.current_language),
            get_text('black', self.current_language),
            get_text('yellow', self.current_language),
            get_text('green', self.current_language),
            get_text('blue', self.current_language),
            get_text('red', self.current_language),
            get_text('custom', self.current_language)
        ])
        contrast_grid.addWidget(self.foreground_color, 0, 1)
        
        # 背景色設定
        contrast_grid.addWidget(QLabel(get_text('background_color', self.current_language)), 1, 0)
        self.background_color = QComboBox()
        self.background_color.addItems([
            get_text('black', self.current_language),
            get_text('white', self.current_language),
            get_text('blue', self.current_language),
            get_text('yellow', self.current_language),
            get_text('green', self.current_language),
            get_text('red', self.current_language),
            get_text('custom', self.current_language)
        ])
        contrast_grid.addWidget(self.background_color, 1, 1)
        
        # 自訂前景色RGB值
        self.custom_fg_group = QGroupBox(get_text('custom_fg_settings', self.current_language))
        fg_layout = QGridLayout()
        
        self.fg_red = QSpinBox()
        self.fg_green = QSpinBox()
        self.fg_blue = QSpinBox()
        for spin in [self.fg_red, self.fg_green, self.fg_blue]:
            spin.setRange(0, 255)
            spin.setEnabled(False)
            
        fg_layout.addWidget(QLabel('R:'), 0, 0)
        fg_layout.addWidget(self.fg_red, 0, 1)
        fg_layout.addWidget(QLabel('G:'), 1, 0)
        fg_layout.addWidget(self.fg_green, 1, 1)
        fg_layout.addWidget(QLabel('B:'), 2, 0)
        fg_layout.addWidget(self.fg_blue, 2, 1)
        
        self.custom_fg_group.setLayout(fg_layout)
        contrast_grid.addWidget(self.custom_fg_group, 2, 0, 1, 2)
        
        # 自訂背景色RGB值
        self.custom_bg_group = QGroupBox(get_text('custom_bg_settings', self.current_language))
        bg_layout = QGridLayout()
        
        self.bg_red = QSpinBox()
        self.bg_green = QSpinBox()
        self.bg_blue = QSpinBox()
        for spin in [self.bg_red, self.bg_green, self.bg_blue]:
            spin.setRange(0, 255)
            spin.setEnabled(False)
            
        bg_layout.addWidget(QLabel('R:'), 0, 0)
        bg_layout.addWidget(self.bg_red, 0, 1)
        bg_layout.addWidget(QLabel('G:'), 1, 0)
        bg_layout.addWidget(self.bg_green, 1, 1)
        bg_layout.addWidget(QLabel('B:'), 2, 0)
        bg_layout.addWidget(self.bg_blue, 2, 1)
        
        self.custom_bg_group.setLayout(bg_layout)
        contrast_grid.addWidget(self.custom_bg_group, 3, 0, 1, 2)
        
        contrast_group.setLayout(contrast_grid)
        color_layout.addWidget(contrast_group)
        color_tab.setLayout(color_layout)
        
        # 添加分頁
        tab_widget.addTab(camera_tab, get_text('camera', self.current_language))
        tab_widget.addTab(mask_tab, get_text('mask', self.current_language))
        tab_widget.addTab(guide_tab, get_text('guide_line', self.current_language))
        tab_widget.addTab(control_tab, get_text('control', self.current_language))
        tab_widget.addTab(ui_tab, get_text('interface', self.current_language))
        tab_widget.addTab(save_tab, get_text('save', self.current_language))
        tab_widget.addTab(color_tab, get_text('color_settings', self.current_language))
        
        layout.addWidget(tab_widget)
        
        # 按鈕
        button_layout = QHBoxLayout()
        save_button = QPushButton(get_text('save', self.current_language))
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton(get_text('cancel', self.current_language))
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 連接信號
        self.autofocus_check.stateChanged.connect(self.toggle_focus_slider)
        self.foreground_color.currentTextChanged.connect(self.update_fg_controls)
        self.background_color.currentTextChanged.connect(self.update_bg_controls)
        
    def toggle_focus_slider(self, state):
        """切換對焦滑桿啟用狀態"""
        self.focus_value.setEnabled(state == Qt.Checked)
        
    def refresh_camera_list(self):
        self.camera_combo.clear()
        for i in range(10):  # 檢查前10個攝影機
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                self.camera_combo.addItem(get_text('camera_id', self.current_language).format(i), i)
                cap.release()
                
    def save_settings(self):
        """儲存所有設定"""
        try:
            # 儲存攝影機設定
            self.settings.setValue('camera_id', self.camera_combo.currentData())
            self.settings.setValue('autofocus', self.autofocus_check.isChecked())
            self.settings.setValue('focus_value', self.focus_value.value())
            self.settings.setValue('width', self.width_spin.value())
            self.settings.setValue('height', self.height_spin.value())
            
            # 儲存遮罩設定
            self.settings.setValue('mask_mode', self.mask_mode.currentText())
            self.settings.setValue('mask_opacity', self.mask_opacity.value())
            self.settings.setValue('mask_size', self.mask_size.value())
            
            # 儲存輔助線設定
            self.settings.setValue('guide_mode', self.guide_mode.currentText())
            self.settings.setValue('guide_color', self.guide_color.currentText())
            self.settings.setValue('guide_thickness', self.guide_thickness.value())
            
            # 儲存控制設定
            self.settings.setValue('move_speed', self.move_speed.value())
            self.settings.setValue('invert_mouse', self.invert_mouse.isChecked())
            self.settings.setValue('zoom_in_key', self.zoom_in_key.text())
            self.settings.setValue('zoom_out_key', self.zoom_out_key.text())
            self.settings.setValue('reset_key', self.reset_key.text())
            self.settings.setValue('move_up_key', self.move_up_key.text())
            self.settings.setValue('move_down_key', self.move_down_key.text())
            self.settings.setValue('move_left_key', self.move_left_key.text())
            self.settings.setValue('move_right_key', self.move_right_key.text())
            
            # 儲存影像變換設定
            self.settings.setValue('flip_horizontal', self.flip_horizontal.isChecked())
            self.settings.setValue('flip_vertical', self.flip_vertical.isChecked())
            self.settings.setValue('rotation_angle', int(self.rotation_angle.currentText().replace('°', '')))
            
            # 儲存介面設定
            self.settings.setValue('fullscreen', self.fullscreen_check.isChecked())
            self.settings.setValue('button_position', self.button_position.currentText())
            self.settings.setValue('control_width', self.control_width.value())
            
            # 儲存儲存設定
            self.settings.setValue('screenshot_path', self.screenshot_path.text())
            self.settings.setValue('screenshot_format', self.screenshot_format.currentText())
            self.settings.setValue('recording_path', self.recording_path.text())
            self.settings.setValue('video_format', self.video_format.currentText())
            self.settings.setValue('video_quality', self.video_quality.currentText())
            self.settings.setValue('audio_source', self.audio_source.currentText())
            
            # 儲存顏色設定
            self.settings.setValue('foreground_color', self.foreground_color.currentText())
            self.settings.setValue('background_color', self.background_color.currentText())
            
            # 儲存自訂顏色
            self.settings.setValue('custom_fg_red', self.fg_red.value())
            self.settings.setValue('custom_fg_green', self.fg_green.value())
            self.settings.setValue('custom_fg_blue', self.fg_blue.value())
            
            self.settings.setValue('custom_bg_red', self.bg_red.value())
            self.settings.setValue('custom_bg_green', self.bg_green.value())
            self.settings.setValue('custom_bg_blue', self.bg_blue.value())
            
            # 儲存語言設定
            self.settings.setValue('language', 'zh_TW' if self.language_combo.currentText() == '繁體中文' else 'en_US')
            
            # 儲存功能塊顯示設定
            self.settings.setValue('show_zoom', self.show_zoom.isChecked())
            self.settings.setValue('show_color', self.show_color.isChecked())
            self.settings.setValue('show_filter', self.show_filter.isChecked())
            self.settings.setValue('show_assist', self.show_assist.isChecked())
            self.settings.setValue('show_transform', self.show_transform.isChecked())
            self.settings.setValue('show_function', self.show_function.isChecked())
            
            # 同步設定
            self.settings.sync()
            
            # 通知主視窗更新設定
            if self.parent:
                self.parent.apply_settings()
                
            print("設定已成功儲存")
            self.accept()
            
        except Exception as e:
            print(f"儲存設定時發生錯誤: {str(e)}")
            
    def load_settings(self):
        """載入所有設定"""
        try:
            # 載入攝影機設定
            camera_id = self.settings.value('camera_id', 0, type=int)
            index = self.camera_combo.findData(camera_id)
            if index >= 0:
                self.camera_combo.setCurrentIndex(index)
                
            self.autofocus_check.setChecked(self.settings.value('autofocus', True, type=bool))
            self.focus_value.setValue(self.settings.value('focus_value', 50, type=int))
            self.width_spin.setValue(self.settings.value('width', 1280, type=int))
            self.height_spin.setValue(self.settings.value('height', 720, type=int))
            
            # 載入遮罩設定
            mask_mode = self.settings.value('mask_mode', get_text('horizontal_mask', self.current_language))
            self.mask_mode.setCurrentText(get_text(mask_mode, self.current_language))
            self.mask_opacity.setValue(self.settings.value('mask_opacity', 50, type=int))
            self.mask_size.setValue(self.settings.value('mask_size', 30, type=int))
            
            # 載入輔助線設定
            guide_mode = self.settings.value('guide_mode', get_text('cross', self.current_language))
            self.guide_mode.setCurrentText(get_text(guide_mode, self.current_language))
            guide_color = self.settings.value('guide_color', get_text('green', self.current_language))
            self.guide_color.setCurrentText(get_text(guide_color, self.current_language))
            self.guide_thickness.setValue(self.settings.value('guide_thickness', 1, type=int))
            
            # 載入控制設定
            self.move_speed.setValue(self.settings.value('move_speed', 5, type=int))
            self.invert_mouse.setChecked(self.settings.value('invert_mouse', False, type=bool))
            self.zoom_in_key.setText(self.settings.value('zoom_in_key', '+'))
            self.zoom_out_key.setText(self.settings.value('zoom_out_key', '-'))
            self.reset_key.setText(self.settings.value('reset_key', '0'))
            self.move_up_key.setText(self.settings.value('move_up_key', 'W'))
            self.move_down_key.setText(self.settings.value('move_down_key', 'S'))
            self.move_left_key.setText(self.settings.value('move_left_key', 'A'))
            self.move_right_key.setText(self.settings.value('move_right_key', 'D'))
            
            # 載入影像變換設定
            self.flip_horizontal.setChecked(self.settings.value('flip_horizontal', False, type=bool))
            self.flip_vertical.setChecked(self.settings.value('flip_vertical', False, type=bool))
            self.rotation_angle.setCurrentText(f"{self.settings.value('rotation_angle', 0, type=int)}°")
            
            # 載入介面設定
            self.fullscreen_check.setChecked(self.settings.value('fullscreen', False, type=bool))
            button_position = self.settings.value('button_position', get_text('right', self.current_language))
            self.button_position.setCurrentText(get_text(button_position, self.current_language))
            self.control_width.setValue(self.settings.value('control_width', 20, type=int))
            
            # 載入儲存設定
            self.screenshot_path.setText(self.settings.value('screenshot_path', os.path.expanduser('~/Pictures')))
            self.screenshot_format.setCurrentText(self.settings.value('screenshot_format', 'PNG'))
            self.recording_path.setText(self.settings.value('recording_path', os.path.expanduser('~/Videos')))
            self.video_format.setCurrentText(self.settings.value('video_format', 'MP4'))
            video_quality = self.settings.value('video_quality', get_text('high_quality', self.current_language))
            self.video_quality.setCurrentText(get_text(video_quality, self.current_language))
            audio_source = self.settings.value('audio_source', get_text('none', self.current_language))
            self.audio_source.setCurrentText(get_text(audio_source, self.current_language))
            
            # 載入顏色設定
            fg_color = self.settings.value('foreground_color', get_text('white', self.current_language))
            bg_color = self.settings.value('background_color', get_text('black', self.current_language))
            self.foreground_color.setCurrentText(get_text(fg_color, self.current_language))
            self.background_color.setCurrentText(get_text(bg_color, self.current_language))
            
            # 載入自訂顏色
            self.fg_red.setValue(self.settings.value('custom_fg_red', 255, type=int))
            self.fg_green.setValue(self.settings.value('custom_fg_green', 255, type=int))
            self.fg_blue.setValue(self.settings.value('custom_fg_blue', 255, type=int))
            
            self.bg_red.setValue(self.settings.value('custom_bg_red', 0, type=int))
            self.bg_green.setValue(self.settings.value('custom_bg_green', 0, type=int))
            self.bg_blue.setValue(self.settings.value('custom_bg_blue', 0, type=int))
            
            # 載入語言設定
            self.language_combo.setCurrentText('繁體中文' if self.settings.value('language', 'zh_TW') == 'zh_TW' else 'English')
            
            # 載入功能塊顯示設定
            self.show_zoom.setChecked(self.settings.value('show_zoom', True, type=bool))
            self.show_color.setChecked(self.settings.value('show_color', True, type=bool))
            self.show_filter.setChecked(self.settings.value('show_filter', True, type=bool))
            self.show_assist.setChecked(self.settings.value('show_assist', True, type=bool))
            self.show_transform.setChecked(self.settings.value('show_transform', True, type=bool))
            self.show_function.setChecked(self.settings.value('show_function', True, type=bool))
            
            # 更新控制項狀態
            self.update_fg_controls(self.foreground_color.currentText())
            self.update_bg_controls(self.background_color.currentText())
            
            print("設定已成功載入")
            
        except Exception as e:
            print(f"載入設定時發生錯誤: {str(e)}")
            
    def browse_folder(self, line_edit):
        """開啟資料夾選擇對話框"""
        folder = QFileDialog.getExistingDirectory(self, get_text('choose_folder', self.current_language), 
                                                line_edit.text())
        if folder:
            line_edit.setText(folder)
            
    def update_fg_controls(self, text):
        """更新前景色控制項狀態"""
        is_custom = text == get_text('custom', self.current_language)
        for spin in [self.fg_red, self.fg_green, self.fg_blue]:
            spin.setEnabled(is_custom)
            
    def update_bg_controls(self, text):
        """更新背景色控制項狀態"""
        is_custom = text == get_text('custom', self.current_language)
        for spin in [self.bg_red, self.bg_green, self.bg_blue]:
            spin.setEnabled(is_custom) 