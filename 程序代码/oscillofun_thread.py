import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


class OscillofunThread(QThread):
    """专门处理Oscillofun显示效果的线程"""
    update_signal = pyqtSignal(np.ndarray, int, float)  # 发送帧数据，当前帧数，完成百分比
    finished_signal = pyqtSignal()  # 新增：播放完成信号

    def __init__(self, data, fs, frame_rate=30, direction_coeff=(-1, -1)):
        super().__init__()
        self.data = data
        self.fs = fs
        self.frame_rate = frame_rate
        self.direction_coeff = direction_coeff
        self.is_running = False
        self.paused = False
        self.frame_size = fs // frame_rate
        self.total_frames = len(data) // self.frame_size
        self.current_frame = 0
        self.display_range = [-0.7, 0.7, -0.7, 0.7]

    def run(self):
        """运行Oscillofun显示线程"""
        self.is_running = True
        self.paused = False

        while self.is_running and self.current_frame < self.total_frames:
            if not self.paused:
                start_idx = self.current_frame * self.frame_size
                end_idx = min(start_idx + self.frame_size, len(self.data))
                frame_data = self.data[start_idx:end_idx]

                if len(frame_data.shape) == 2 and frame_data.shape[1] == 2:
                    frame_data[:, 0] = self.direction_coeff[0] * frame_data[:, 0]
                    frame_data[:, 1] = self.direction_coeff[1] * frame_data[:, 1]

                progress = (end_idx / len(self.data)) * 100
                self.update_signal.emit(frame_data, self.current_frame, progress)
                self.current_frame += 1

                # 检测播放是否完成
                if self.current_frame >= self.total_frames:
                    self.finished_signal.emit()  # 发射播放完成信号
                    break

            self.msleep(1000 // self.frame_rate)

    def pause(self):
        """暂停播放"""
        self.paused = True

    def resume(self):
        """继续播放"""
        self.paused = False

    def stop(self):
        """停止线程"""
        self.is_running = False
        self.wait()

    def seek(self, frame_number):
        """跳转到指定帧"""
        if 0 <= frame_number < self.total_frames:
            self.current_frame = frame_number

    def get_progress(self):
        """获取当前播放进度百分比"""
        if self.total_frames > 0:
            return (self.current_frame / self.total_frames) * 100
        return 0
