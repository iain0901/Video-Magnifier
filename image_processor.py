import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.zoom_factors = [1.0, 1.5, 2.0, 3.0, 4.0]
        self.current_zoom_index = 0
        self.zoom_factor = self.zoom_factors[self.current_zoom_index]
        self.pan_x = 0
        self.pan_y = 0
        self.color_mode = 'normal'
        self.filter_mode = 'normal'
        self.show_mask = False
        self.show_guide_line = False
        self.mask_mode = 'horizontal'
        self.mask_opacity = 50
        self.mask_size = 30
        self.guide_mode = 'cross'
        self.guide_color = (0, 255, 0)  # 綠色
        self.guide_thickness = 1
        self.last_frame = None
        self.last_processed_frame = None
        self.brightness = 0  # 亮度調整值，範圍 -100 到 100
        
    def process_frame(self, frame):
        """處理影像"""
        if frame is None:
            return None
            
        self.last_frame = frame.copy()
        processed_frame = frame.copy()
        
        # 套用亮度調整
        processed_frame = self.apply_brightness(processed_frame)
        
        # 套用縮放和平移
        if self.zoom_factor != 1.0 or self.pan_x != 0 or self.pan_y != 0:
            height, width = frame.shape[:2]
            
            # 計算ROI大小和位置
            roi_width = int(width / self.zoom_factor)
            roi_height = int(height / self.zoom_factor)
            
            # 計算最大平移範圍
            max_pan_x = int(width * (1 - 1/self.zoom_factor) / 2)
            max_pan_y = int(height * (1 - 1/self.zoom_factor) / 2)
            
            # 限制平移範圍
            self.pan_x = max(-max_pan_x, min(max_pan_x, self.pan_x))
            self.pan_y = max(-max_pan_y, min(max_pan_y, self.pan_y))
            
            # 計算ROI的起始點
            roi_x = int((width - roi_width) / 2 - self.pan_x)
            roi_y = int((height - roi_height) / 2 - self.pan_y)
            
            # 確保ROI在影像範圍內
            roi_x = max(0, min(width - roi_width, roi_x))
            roi_y = max(0, min(height - roi_height, roi_y))
            
            # 裁剪ROI並縮放回原始大小
            roi = frame[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
            processed_frame = cv2.resize(roi, (width, height), interpolation=cv2.INTER_LINEAR)
            
        # 套用顏色模式
        if self.color_mode != 'normal':
            processed_frame = self.apply_color_mode(processed_frame)
            
        # 套用濾鏡
        if self.filter_mode != 'normal':
            processed_frame = self.apply_filter(processed_frame)
            
        # 套用遮罩
        if self.show_mask:
            processed_frame = self.apply_mask(processed_frame)
            
        # 套用輔助線
        if self.show_guide_line:
            processed_frame = self.apply_guide_line(processed_frame)
            
        self.last_processed_frame = processed_frame.copy()
        return processed_frame
        
    def zoom_in(self):
        """放大"""
        if self.current_zoom_index < len(self.zoom_factors) - 1:
            self.current_zoom_index += 1
            self.zoom_factor = self.zoom_factors[self.current_zoom_index]
            if self.last_frame is not None:
                return self.process_frame(self.last_frame)
        return None
        
    def zoom_out(self):
        """縮小"""
        if self.current_zoom_index > 0:
            self.current_zoom_index -= 1
            self.zoom_factor = self.zoom_factors[self.current_zoom_index]
            if self.last_frame is not None:
                return self.process_frame(self.last_frame)
        return None
        
    def reset_zoom(self):
        """重置縮放"""
        self.current_zoom_index = 0
        self.zoom_factor = self.zoom_factors[self.current_zoom_index]
        self.pan_x = 0
        self.pan_y = 0
        if self.last_frame is not None:
            return self.process_frame(self.last_frame)
        return None
        
    def move(self, dx, dy):
        """移動視野"""
        if self.zoom_factor > 1.0:
            # 根據縮放因子調整移動速度
            dx = int(dx * self.zoom_factor)
            dy = int(dy * self.zoom_factor)
            
            # 更新平移位置
            self.pan_x += dx
            self.pan_y += dy
            
            if self.last_frame is not None:
                return self.process_frame(self.last_frame)
        return None
        
    def set_color_mode(self, mode):
        """設置顏色模式"""
        self.color_mode = mode
        if self.last_frame is not None:
            return self.process_frame(self.last_frame)
        return None
        
    def apply_color_mode(self, frame):
        """套用顏色模式"""
        if self.color_mode == 'white_on_black':
            return 255 - frame
        elif self.color_mode == 'black_on_white':
            return frame
        elif self.color_mode == 'yellow_on_black':
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            yellow = np.zeros_like(frame)
            yellow[gray > 128] = [255, 255, 0]  # 黃色
            return yellow
        elif self.color_mode == 'yellow_on_blue':
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            colored = np.zeros_like(frame)
            colored[gray > 128] = [255, 255, 0]  # 黃色
            colored[gray <= 128] = [0, 0, 255]  # 藍色
            return colored
        elif self.color_mode == 'green_on_black':
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            green = np.zeros_like(frame)
            green[gray > 128] = [0, 255, 0]  # 綠色
            return green
        elif self.color_mode == 'blue_on_yellow':
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            colored = np.zeros_like(frame)
            colored[gray > 128] = [0, 0, 255]  # 藍色
            colored[gray <= 128] = [255, 255, 0]  # 黃色
            return colored
        return frame
        
    def set_filter_mode(self, mode):
        """設置濾鏡模式"""
        self.filter_mode = mode
        if self.last_frame is not None:
            return self.process_frame(self.last_frame)
        return None
        
    def apply_filter(self, frame):
        """套用濾鏡"""
        if self.filter_mode == 'high_contrast':
            # 轉換到 LAB 色彩空間
            lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
            # 分離通道
            l, a, b = cv2.split(lab)
            # 對亮度通道進行 CLAHE（限制對比度自適應直方圖均衡化）
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            # 合併通道
            enhanced_lab = cv2.merge((cl, a, b))
            # 轉回 RGB
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
            # 增加銳利度
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            return sharpened
        elif self.filter_mode == 'grayscale':
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        elif self.filter_mode == 'inverse':
            return 255 - frame
        return frame
        
    def toggle_mask(self, show):
        """切換遮罩顯示"""
        self.show_mask = show
        if self.last_frame is not None:
            return self.process_frame(self.last_frame)
        return None
        
    def apply_mask(self, frame):
        """套用遮罩"""
        height, width = frame.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        if self.mask_mode == 'horizontal':
            mask_height = int(height * self.mask_size / 100)
            y1 = (height - mask_height) // 2
            y2 = y1 + mask_height
            mask[y1:y2, :] = 255
        elif self.mask_mode == 'vertical':
            mask_width = int(width * self.mask_size / 100)
            x1 = (width - mask_width) // 2
            x2 = x1 + mask_width
            mask[:, x1:x2] = 255
        elif self.mask_mode == 'rectangle':
            mask_height = int(height * self.mask_size / 100)
            mask_width = int(width * self.mask_size / 100)
            y1 = (height - mask_height) // 2
            y2 = y1 + mask_height
            x1 = (width - mask_width) // 2
            x2 = x1 + mask_width
            mask[y1:y2, x1:x2] = 255
        elif self.mask_mode == 'ellipse':
            center = (width // 2, height // 2)
            axes = (int(width * self.mask_size / 200), int(height * self.mask_size / 200))
            cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
            
        # 創建半透明遮罩
        alpha = self.mask_opacity / 100
        mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        return cv2.addWeighted(frame, 1, mask_rgb, alpha, 0)
        
    def toggle_guide_line(self, show):
        """切換輔助線顯示"""
        self.show_guide_line = show
        if self.last_frame is not None:
            return self.process_frame(self.last_frame)
        return None
        
    def apply_guide_line(self, frame):
        """套用輔助線"""
        height, width = frame.shape[:2]
        result = frame.copy()
        
        if self.guide_mode == 'cross':
            # 繪製十字線
            cv2.line(result, (width//2, 0), (width//2, height), self.guide_color, self.guide_thickness)
            cv2.line(result, (0, height//2), (width, height//2), self.guide_color, self.guide_thickness)
        elif self.guide_mode == 'grid':
            # 繪製網格
            for x in range(width//3, width, width//3):
                cv2.line(result, (x, 0), (x, height), self.guide_color, self.guide_thickness)
            for y in range(height//3, height, height//3):
                cv2.line(result, (0, y), (width, y), self.guide_color, self.guide_thickness)
        elif self.guide_mode == 'center':
            # 繪製中心點
            center = (width//2, height//2)
            size = 20
            cv2.line(result, (center[0]-size, center[1]), (center[0]+size, center[1]), 
                    self.guide_color, self.guide_thickness)
            cv2.line(result, (center[0], center[1]-size), (center[0], center[1]+size), 
                    self.guide_color, self.guide_thickness)
        elif self.guide_mode == 'reading_line':
            # 繪製閱讀線
            y = height//2
            cv2.line(result, (0, y), (width, y), self.guide_color, self.guide_thickness)
            
        return result 
        
    def set_brightness(self, value):
        """設置亮度"""
        self.brightness = max(-100, min(100, value))
        if self.last_frame is not None:
            return self.process_frame(self.last_frame)
        return None
        
    def apply_brightness(self, frame):
        """套用亮度調整"""
        if self.brightness != 0:
            if self.brightness > 0:
                alpha = 1.0
                beta = self.brightness * 2.55  # 將 0-100 映射到 0-255
            else:
                alpha = 1.0 + (self.brightness / 100.0)  # 降低亮度時調整對比度
                beta = 0
            return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        return frame 