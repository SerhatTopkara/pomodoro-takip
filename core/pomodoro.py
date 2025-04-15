from PyQt6.QtCore import QObject, pyqtSignal

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from core.timer import TimerCore

class PomodoroManager(QObject):
    # Sinyaller
    session_changed = pyqtSignal(str, int)  # (session_type, duration_in_minutes)
    session_completed = pyqtSignal(str)  # session_type
    all_completed = pyqtSignal()  # Tüm pomodoro döngüsü tamamlandığında
    
    def __init__(self, timer_core, db_manager):
        super().__init__()
        self.timer = timer_core
        self.db_manager = db_manager
        
        # Sayaç sinyallerine bağlan
        self.timer.completed.connect(self._on_timer_completed)
        
        # Ayarları yükle
        self._load_settings()
        
        # Pomodoro durum takibi
        self.current_session_type = "work"  # work, short_break, long_break
        self.completed_work_sessions = 0
        
        # Pygame ses modülünü başlat
        pygame.mixer.init()
        # Alarm dosyası direkt proje kök dizininde 
        self.alarm_file = os.path.abspath("alarm.wav")
        
        
        
        
    
    def _load_settings(self):
        """Veritabanından ayarları yükle."""
        settings = self.db_manager.get_settings()
        self.work_duration = settings['work_duration']
        self.short_break_duration = settings['short_break_duration']
        self.long_break_duration = settings['long_break_duration']
        self.sessions_before_long_break = settings['sessions_before_long_break']
        self.sound_enabled = settings['sound_enabled']
    
    def start_next_session(self):
        """Bir sonraki seansı başlat."""
        if self.current_session_type == "work":
            # Çalışma seansı başlat
            self.timer.start(self.work_duration)
            self.session_changed.emit("work", self.work_duration)
        
        elif self.current_session_type == "short_break":
            # Kısa mola başlat
            self.timer.start(self.short_break_duration)
            self.session_changed.emit("short_break", self.short_break_duration)
        
        elif self.current_session_type == "long_break":
            # Uzun mola başlat
            self.timer.start(self.long_break_duration)
            self.session_changed.emit("long_break", self.long_break_duration)
    
    def _on_timer_completed(self):
        """Sayaç tamamlandığında çağrılır."""
        # Alarm çal.
        if self.sound_enabled:
            try:
                # Pygame ile ses çalma
                pygame.mixer.music.load(self.alarm_file)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Ses çalınırken hata: {e}")
        
        # Mevcut seansın tipini kaydet.
        completed_session_type = self.current_session_type
        
        # Bir sonraki seans tipini belirle.
        if self.current_session_type == "work":
            self.completed_work_sessions += 1
            
            # Uzun mola zamanı mı kontrol et.
            if self.completed_work_sessions >= self.sessions_before_long_break:
                self.current_session_type = "long_break"
                self.completed_work_sessions = 0
            else:
                self.current_session_type = "short_break"
        
        else:  # Mola sonrası.
            self.current_session_type = "work"
        
        # Şimdi session_completed sinyalini gönder.
        self.session_completed.emit(completed_session_type)
        
        # Bir sonraki seansı otomatik olarak başlat.
        self.start_next_session()
    
    def reset(self):
        """Pomodoro döngüsünü sıfırla"""
        self.timer.reset()
        self.current_session_type = "work"
        self.completed_work_sessions = 0