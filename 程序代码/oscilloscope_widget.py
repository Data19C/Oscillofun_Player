from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QFont


class OscilloscopeWidget(QWidget):
    """改进的示波器显示组件，支持坐标轴反转功能"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 500)
        self.setSizePolicy(1, 1)

        self.current_frame_data = None
        self.display_range = [-0.7, 0.7, -0.7, 0.7]
        self.point_color = Qt.green
        self.point_size = 2
        self.x_reversed = False  # X轴反转标志
        self.y_reversed = False  # Y轴反转标志

    def set_frame_data(self, frame_data):
        """设置当前帧的数据"""
        self.current_frame_data = frame_data
        self.update()

    def set_display_range(self, display_range):
        """设置显示范围"""
        self.display_range = display_range
        self.update()

    def set_x_axis_reversed(self, reversed):
        """设置X轴反转"""
        self.x_reversed = reversed
        self.update()

    def set_y_axis_reversed(self, reversed):
        """设置Y轴反转"""
        self.y_reversed = reversed
        self.update()

    def toggle_x_axis(self):
        """切换X轴方向"""
        self.x_reversed = not self.x_reversed
        self.update()
        return self.x_reversed

    def toggle_y_axis(self):
        """切换Y轴方向"""
        self.y_reversed = not self.y_reversed
        self.update()
        return self.y_reversed

    def paintEvent(self, event):
        """绘制示波器界面 - X-Y模式"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        width = self.width()
        height = self.height()

        self.draw_grid(painter, width, height)

        if self.current_frame_data is not None and len(self.current_frame_data) > 0:
            self.draw_xy_points(painter, width, height)

        self.draw_title(painter, width)
        self.draw_axis_labels(painter, width, height)  # 添加坐标轴标签

    def draw_grid(self, painter, width, height):
        """绘制网格和坐标轴"""
        pen = QPen(QColor(50, 50, 50))
        pen.setWidth(1)
        painter.setPen(pen)

        grid_size = 5
        for i in range(1, grid_size):
            y = i * height // grid_size
            painter.drawLine(0, y, width, y)
            x = i * width // grid_size
            painter.drawLine(x, 0, x, height)

        pen.setColor(QColor(100, 100, 100))
        painter.setPen(pen)
        center_x = width // 2
        center_y = height // 2

        # 绘制坐标轴方向指示器[4,6](@ref)
        self.draw_axis_indicators(painter, width, height)

    def draw_axis_indicators(self, painter, width, height):
        """绘制坐标轴方向指示器（左侧Y轴箭头，下方X轴箭头）"""
        pen = QPen(QColor(255, 255, 0))  # 黄色指示器
        pen.setWidth(2)
        painter.setPen(pen)

        center_x = width // 2
        center_y = height // 2
        arrow_size = 10
        margin = 30  # 边距

        # Y轴方向指示器（左侧）
        if self.y_reversed:
            # Y轴反向：箭头向下（左侧）
            y_arrow_x = margin
            y_arrow_y = center_y
            painter.drawLine(y_arrow_x, y_arrow_y, y_arrow_x, y_arrow_y + arrow_size)
            painter.drawLine(y_arrow_x, y_arrow_y + arrow_size, y_arrow_x - arrow_size // 2,
                             y_arrow_y + arrow_size // 2)
            painter.drawLine(y_arrow_x, y_arrow_y + arrow_size, y_arrow_x + arrow_size // 2,
                             y_arrow_y + arrow_size // 2)
        else:
            # Y轴正向：箭头向上（左侧）
            y_arrow_x = margin
            y_arrow_y = center_y
            painter.drawLine(y_arrow_x, y_arrow_y, y_arrow_x, y_arrow_y - arrow_size)
            painter.drawLine(y_arrow_x, y_arrow_y - arrow_size, y_arrow_x - arrow_size // 2,
                             y_arrow_y - arrow_size // 2)
            painter.drawLine(y_arrow_x, y_arrow_y - arrow_size, y_arrow_x + arrow_size // 2,
                             y_arrow_y - arrow_size // 2)

        # X轴方向指示器（下方）
        if self.x_reversed:
            # X轴反向：箭头向左（下方）
            x_arrow_x = center_x
            x_arrow_y = height - margin
            painter.drawLine(x_arrow_x, x_arrow_y, x_arrow_x - arrow_size, x_arrow_y)
            painter.drawLine(x_arrow_x - arrow_size, x_arrow_y, x_arrow_x - arrow_size // 2,
                             x_arrow_y - arrow_size // 2)
            painter.drawLine(x_arrow_x - arrow_size, x_arrow_y, x_arrow_x - arrow_size // 2,
                             x_arrow_y + arrow_size // 2)
        else:
            # X轴正向：箭头向右（下方）
            x_arrow_x = center_x
            x_arrow_y = height - margin
            painter.drawLine(x_arrow_x, x_arrow_y, x_arrow_x + arrow_size, x_arrow_y)
            painter.drawLine(x_arrow_x + arrow_size, x_arrow_y, x_arrow_x + arrow_size // 2,
                             x_arrow_y - arrow_size // 2)
            painter.drawLine(x_arrow_x + arrow_size, x_arrow_y, x_arrow_x + arrow_size // 2,
                             x_arrow_y + arrow_size // 2)

    def draw_xy_points(self, painter, width, height):
        """绘制X-Y模式的数据点，支持坐标轴反转[4,6](@ref)"""
        if len(self.current_frame_data.shape) == 1:
            return

        pen = QPen(self.point_color)
        pen.setWidth(self.point_size)
        painter.setPen(pen)

        x_min, x_max, y_min, y_max = self.display_range
        center_x = width // 2
        center_y = height // 2

        x_scale = width / (x_max - x_min) if x_max != x_min else 1
        y_scale = height / (y_max - y_min) if y_max != y_min else 1

        for i in range(len(self.current_frame_data)):
            if i >= len(self.current_frame_data):
                break

            if self.current_frame_data.shape[1] >= 2:
                x_val = self.current_frame_data[i, 0]
                y_val = self.current_frame_data[i, 1]
            else:
                x_val = self.current_frame_data[i, 0] if len(self.current_frame_data.shape) > 1 else \
                    self.current_frame_data[i]
                y_val = 0

            # 应用坐标轴反转[6](@ref)
            if self.x_reversed:
                x_val = -x_val
            if self.y_reversed:
                y_val = -y_val

            # 将数据坐标转换为屏幕坐标[5](@ref)
            x_screen = int(center_x + x_val * x_scale)
            y_screen = int(center_y - y_val * y_scale)  # 屏幕坐标Y轴向下

            painter.drawPoint(x_screen, y_screen)

    def draw_title(self, painter, width):
        """绘制标题和坐标轴状态"""
        pen = QPen(QColor(255, 255, 255))
        font = QFont("Arial", 14, QFont.Bold)
        painter.setPen(pen)
        painter.setFont(font)

        title_text = "Oscillofun - X-Y Mode"
        text_width = painter.fontMetrics().width(title_text)
        painter.drawText((width - text_width) // 2, 30, title_text)

        # 显示坐标轴状态
        axis_status = f"X轴: {'反向' if self.x_reversed else '正向'}, Y轴: {'反向' if self.y_reversed else '正向'}"
        status_font = QFont("Arial", 10)
        painter.setFont(status_font)
        status_width = painter.fontMetrics().width(axis_status)
        painter.drawText((width - status_width) // 2, 55, axis_status)

    def draw_axis_labels(self, painter, width, height):
        """绘制坐标轴标签"""
        pen = QPen(QColor(200, 200, 200))
        font = QFont("Arial", 8)
        painter.setPen(pen)
        painter.setFont(font)

        center_x = width // 2
        center_y = height // 2
