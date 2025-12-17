import sys
import os
import numpy as np
import librosa
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QFileDialog,
                             QMessageBox, QSlider)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from oscillofun_thread import OscillofunThread
from oscilloscope_widget import OscilloscopeWidget
from 程序代码.audio_player import AudioPlayer


class OscillofunPlayer(QMainWindow):
    """主应用程序窗口"""

    def __init__(self):
        super().__init__()
        self.audio_player = AudioPlayer()
        self.oscillofun_thread = None
        self.current_audio_data = None
        self.sample_rate = None
        self.auto_reset_enabled = True
        self.init_ui()
        self.setup_timers()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Oscillofun播放器 - X-Y模式")
        self.setFixedSize(800, 800)  # 1:1 比例窗口

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # 程序标题
        title_label = QLabel("Oscillofun音频播放器 - X-Y模式")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 音频信息显示
        self.info_label = QLabel("未加载音频文件")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;")
        layout.addWidget(self.info_label)

        # 进度信息显示
        self.progress_label = QLabel("进度: 0%")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        # 控制面板区域
        control_panel_layout = QHBoxLayout()

        # 坐标轴控制
        axis_control_layout = QVBoxLayout()
        self.x_axis_btn = QPushButton("X轴: 正方向")
        self.y_axis_btn = QPushButton("Y轴: 正方向")
        self.x_axis_btn.clicked.connect(self.toggle_x_axis)
        self.y_axis_btn.clicked.connect(self.toggle_y_axis)
        axis_control_layout.addWidget(self.x_axis_btn)
        axis_control_layout.addWidget(self.y_axis_btn)

        # 自动重置控制
        reset_control_layout = QVBoxLayout()
        self.auto_reset_btn = QPushButton("✅ 自动重置: 开")
        self.auto_reset_btn.setCheckable(True)
        self.auto_reset_btn.setChecked(True)
        self.auto_reset_btn.clicked.connect(self.toggle_auto_reset)
        reset_control_layout.addWidget(self.auto_reset_btn)

        # 声音控制
        sound_control_layout = QVBoxLayout()
        self.sound_toggle_btn = QPushButton("🔊 声音: 开")
        self.sound_toggle_btn.setCheckable(True)
        self.sound_toggle_btn.setChecked(True)
        self.sound_toggle_btn.clicked.connect(self.toggle_sound)
        sound_control_layout.addWidget(self.sound_toggle_btn)

        volume_label = QLabel("音量:")
        sound_control_layout.addWidget(volume_label)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.set_volume)
        sound_control_layout.addWidget(self.volume_slider)

        # 将控制面板组合
        control_panel_layout.addLayout(axis_control_layout)
        control_panel_layout.addLayout(reset_control_layout)
        control_panel_layout.addStretch(1)
        control_panel_layout.addLayout(sound_control_layout)

        layout.addLayout(control_panel_layout)

        # 模拟示波器区域
        self.oscilloscope = OscilloscopeWidget()
        layout.addWidget(self.oscilloscope, 1)

        # 添加垂直弹簧
        layout.addStretch(1)

        # 主要功能按钮区域
        button_layout = QHBoxLayout()
        self.select_btn = QPushButton("选择文件")
        self.play_pause_btn = QPushButton("播放/暂停")
        self.reset_btn = QPushButton("重置")
        self.exit_btn = QPushButton("退出")

        self.select_btn.clicked.connect(self.select_file)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.reset_btn.clicked.connect(self.reset_player)
        self.exit_btn.clicked.connect(self.close)

        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.play_pause_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.exit_btn)
        layout.addLayout(button_layout)

        # 初始状态设置
        self.play_pause_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        self.sound_toggle_btn.setEnabled(False)
        self.x_axis_btn.setEnabled(False)
        self.y_axis_btn.setEnabled(False)
        self.auto_reset_btn.setEnabled(False)

    def setup_timers(self):
        """设置定时器"""
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(100)

    def select_file(self):
        """选择音频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音频文件", "",
            "音频文件 (*.wav *.mp3 *.ogg *.flac);;所有文件 (*.*)"
        )

        if file_path:
            try:
                # 使用librosa加载音频文件
                self.current_audio_data, self.sample_rate = librosa.load(file_path, sr=None, mono=False)

                # 确保数据是二维的（立体声）
                if len(self.current_audio_data.shape) == 1:
                    self.current_audio_data = np.column_stack((self.current_audio_data, self.current_audio_data))
                elif self.current_audio_data.shape[0] == 2:
                    self.current_audio_data = self.current_audio_data.T

                # 使用AudioPlayer加载音频文件
                if self.audio_player.load_file(file_path):
                    print("音频文件加载成功，准备播放")

                # 更新音频信息显示
                file_name = os.path.basename(file_path)
                duration = len(self.current_audio_data) / self.sample_rate
                self.info_label.setText(
                    f"文件: {file_name} | 采样率: {self.sample_rate}Hz | 时长: {duration:.2f}秒")

                # 启用所有控制按钮
                self.play_pause_btn.setEnabled(True)
                self.reset_btn.setEnabled(True)
                self.sound_toggle_btn.setEnabled(True)
                self.x_axis_btn.setEnabled(True)
                self.y_axis_btn.setEnabled(True)
                self.auto_reset_btn.setEnabled(True)

                # 准备Oscillofun线程
                self.prepare_oscillofun()

                # 保留功能介绍弹窗
                QMessageBox.information(self, "加载成功",
                                        "音频文件加载成功！\n\nOscillofun特效说明：\n"
                                        "• 左右声道分别作为X轴和Y轴坐标\n"
                                        "• 绿色点显示音频波形在X-Y平面的分布\n"
                                        "• 模拟真实示波器的X-Y模式显示")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法加载音频文件: {str(e)}")

    def prepare_oscillofun(self):
        """准备Oscillofun线程"""
        if self.oscillofun_thread:
            self.oscillofun_thread.stop()

        self.oscillofun_thread = OscillofunThread(
            self.current_audio_data,
            self.sample_rate,
            frame_rate=30,
            direction_coeff=(-1, -1)
        )
        self.oscillofun_thread.update_signal.connect(self.on_oscillofun_update)
        self.oscillofun_thread.finished_signal.connect(self.on_playback_finished)

    def on_oscillofun_update(self, frame_data, frame_number, progress):
        """处理Oscillofun线程的更新信号"""
        self.oscilloscope.set_frame_data(frame_data)
        self.progress_label.setText(f"进度: {progress:.1f}% | 帧: {frame_number}")

    def on_playback_finished(self):
        """播放完成时的处理 - 移除提示框，只进行静默重置"""
        if self.auto_reset_enabled:
            # 自动重置播放器，不显示提示框
            self.reset_player()
        else:
            # 不自动重置，只更新界面状态
            self.play_pause_btn.setText("播放完成")
            self.play_pause_btn.setEnabled(False)
            if self.audio_player:
                self.audio_player.stop()

    def toggle_auto_reset(self):
        """切换自动重置开关"""
        self.auto_reset_enabled = self.auto_reset_btn.isChecked()
        if self.auto_reset_enabled:
            self.auto_reset_btn.setText("✅ 自动重置: 开")
        else:
            self.auto_reset_btn.setText("❌ 自动重置: 关")

    def toggle_play_pause(self):
        """切换播放/暂停状态"""
        if self.oscillofun_thread is None:
            return

        if not self.oscillofun_thread.isRunning():
            # 开始播放
            self.oscillofun_thread.start()
            self.play_pause_btn.setText("暂停")
            if self.audio_player and self.sound_toggle_btn.isChecked():
                self.audio_player.play()
        else:
            if self.oscillofun_thread.paused:
                # 继续播放
                self.oscillofun_thread.resume()
                self.play_pause_btn.setText("暂停")
                if self.audio_player and self.sound_toggle_btn.isChecked():
                    self.audio_player.unpause()
            else:
                # 暂停播放
                self.oscillofun_thread.pause()
                self.play_pause_btn.setText("继续")
                if self.audio_player:
                    self.audio_player.pause()

    def toggle_x_axis(self):
        """切换X轴方向"""
        is_reversed = self.oscilloscope.toggle_x_axis()
        self.x_axis_btn.setText(f"X轴: {'反方向' if is_reversed else '正方向'}")

    def toggle_y_axis(self):
        """切换Y轴方向"""
        is_reversed = self.oscilloscope.toggle_y_axis()
        self.y_axis_btn.setText(f"Y轴: {'反方向' if is_reversed else '正方向'}")

    def toggle_sound(self):
        """切换声音开关"""
        if self.audio_player:
            sound_enabled = self.sound_toggle_btn.isChecked()
            self.audio_player.toggle_sound(sound_enabled)

            if sound_enabled:
                self.sound_toggle_btn.setText("🔊 声音: 开")
                if (self.oscillofun_thread and
                        self.oscillofun_thread.isRunning() and
                        not self.oscillofun_thread.paused):
                    self.audio_player.unpause()
            else:
                self.sound_toggle_btn.setText("🔇 声音: 关")
                self.audio_player.pause()

    def set_volume(self, volume_value):
        """设置音量"""
        if self.audio_player:
            self.audio_player.set_volume(volume_value)

    def reset_player(self):
        """重置播放器"""
        if self.oscillofun_thread:
            self.oscillofun_thread.stop()
            self.oscillofun_thread.seek(0)
            self.oscilloscope.set_frame_data(None)
            self.progress_label.setText("进度: 0%")
            self.play_pause_btn.setText("播放")
            self.play_pause_btn.setEnabled(True)

        if self.audio_player:
            self.audio_player.stop()

        # 重置坐标轴方向
        self.oscilloscope.set_x_axis_reversed(False)
        self.oscilloscope.set_y_axis_reversed(False)
        self.x_axis_btn.setText("X轴: 正方向")
        self.y_axis_btn.setText("Y轴: 正方向")

    def update_ui(self):
        """更新UI显示"""
        pass

    def closeEvent(self, event):
        """关闭应用程序时的清理工作"""
        if self.oscillofun_thread:
            self.oscillofun_thread.stop()
        if self.audio_player:
            self.audio_player.stop()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    player = OscillofunPlayer()
    player.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
