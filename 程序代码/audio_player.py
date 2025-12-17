import pygame


class AudioPlayer:
    """音频播放控制类"""

    def __init__(self):
        pygame.mixer.init()
        self.current_file = None
        self.is_playing = False
        self.sound_enabled = True
        self.volume = 0.8

    def load_file(self, file_path):
        """加载音频文件"""
        try:
            pygame.mixer.music.load(file_path)
            self.current_file = file_path
            pygame.mixer.music.set_volume(self.volume)
            return True
        except Exception as e:
            print(f"加载音频文件失败: {e}")
            return False

    def play(self):
        """播放音频"""
        if self.current_file and self.sound_enabled:
            try:
                pygame.mixer.music.play()
                self.is_playing = True
            except Exception as e:
                print(f"播放音频失败: {e}")

    def pause(self):
        """暂停播放"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False

    def unpause(self):
        """继续播放"""
        if not self.is_playing and self.sound_enabled:
            pygame.mixer.music.unpause()
            self.is_playing = True

    def stop(self):
        """停止播放"""
        pygame.mixer.music.stop()
        self.is_playing = False

    def set_volume(self, volume_percent):
        """设置音量 (0-100)"""
        self.volume = max(0, min(1.0, volume_percent / 100.0))
        pygame.mixer.music.set_volume(self.volume)

    def toggle_sound(self, enabled):
        """切换声音开关"""
        self.sound_enabled = enabled
        if not enabled and self.is_playing:
            self.pause()
