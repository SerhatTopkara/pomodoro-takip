from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFrame, QProgressBar, QComboBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
import os
from datetime import datetime, date, timedelta

class TimerWidget(QWidget):
    def __init__(self, timer_core, pomodoro_manager):
        super().__init__()
        
        self.timer_core = timer_core
        self.pomodoro_manager = pomodoro_manager
        
        self._setup_ui()
        self._connect_signals()
        
        # Başlangıç süresini ayarla (çalışma süresi)
        self._update_initial_time()
        
        # Günlük çalışma süresini güncelle.
        self._update_daily_stats()
    
    def _setup_ui(self):
        """Sayaç arayüzünü oluştur"""
        main_layout = QVBoxLayout(self)
        
        # Seans tipi göstergesi
        self.session_label = QLabel("Çalışma Seansı")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(self.session_label)
        
        # Sayaç ekranı
        timer_frame = QFrame()
        timer_frame.setFrameShape(QFrame.Shape.StyledPanel)
        timer_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
        
        timer_layout = QVBoxLayout(timer_frame)
        
        
        
        
        self.time_display = QLabel("")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_display.setFont(QFont("Arial", 60, QFont.Weight.Bold))
        self.time_display.setStyleSheet("color: #0066cc;")  # Mavi renk
        timer_layout.addWidget(self.time_display)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e0e0e0;
                height: 10px;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #0066cc;  /* İlerleme çubuğunu da mavi yap */
                border-radius: 5px;
            }
        """)
        timer_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(timer_frame)
        
        # Kontrol butonları
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Başlat")
        self.start_button.setMinimumSize(QSize(120, 40))
        self.start_button.setFont(QFont("Arial", 12))
        control_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Duraklat")
        self.pause_button.setMinimumSize(QSize(120, 40))
        self.pause_button.setFont(QFont("Arial", 12))
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("Sıfırla")
        self.reset_button.setMinimumSize(QSize(120, 40))
        self.reset_button.setFont(QFont("Arial", 12))
        self.reset_button.setEnabled(False)
        control_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(control_layout)
        
        # Alt bilgi alanı - Çerçeve içinde düzenlenmiş bilgiler
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setStyleSheet("background-color: #2c3e50; border-radius: 8px; padding: 10px;")
        
        info_layout = QVBoxLayout(info_frame)
        
        # Ayarlar bilgisi
        info_label = QLabel("Ayarlara giderek pomodoro sürelerini ve tercihlerinizi değiştirebilirsiniz.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #e0e0e0;")
        info_layout.addWidget(info_label)
        
        # Mevcut durum göstergesi
        self.status_label = QLabel("Şu anki durum: Hazır")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #3498db; padding: 5px; border-radius: 5px; background-color: rgba(52,152,219,0.2);")
        info_layout.addWidget(self.status_label)
        
        # Bugünkü toplam çalışma süresi
        self.today_total_label = QLabel("Bugün toplam: 0 saat 0 dakika")
        self.today_total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.today_total_label.setStyleSheet("color: #2ecc71;")
        info_layout.addWidget(self.today_total_label)
        
        main_layout.addWidget(info_frame)
        main_layout.addStretch()
    
    def _connect_signals(self):
        """Sinyalleri bağla"""
        # Buton sinyalleri
        self.start_button.clicked.connect(self._on_start_clicked)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.reset_button.clicked.connect(self._on_reset_clicked)
        
        # Sayaç sinyalleri
        self.timer_core.tick.connect(self._on_timer_tick)
        self.timer_core.state_changed.connect(self._on_timer_state_changed)
        
        # Pomodoro sinyalleri
        self.pomodoro_manager.session_changed.connect(self._on_session_changed)
        self.pomodoro_manager.session_completed.connect(self._on_session_completed)
    
    def _on_start_clicked(self):
        """Başlat butonu tıklandığında"""
        # Pomodoro seansını başlat
        self.pomodoro_manager.start_next_session()
    
    def _on_pause_clicked(self):
        """Duraklat butonu tıklandığında"""
        if self.timer_core.state == "running":
            self.timer_core.pause()
            self.pause_button.setText("Devam Et")
        else:  # "paused"
            self.timer_core.resume()
            self.pause_button.setText("Duraklat")
    
    def _on_reset_clicked(self):
        """Sıfırla butonu tıklandığında"""
        self.timer_core.reset()
    
    def _on_timer_tick(self, elapsed_seconds):
        """Sayaç her saniye çalıştığında"""
        # Kalan süreyi göster
        remaining_time = self.timer_core.get_remaining_time()
        self.time_display.setText(remaining_time)
        
        # İlerleme çubuğunu güncelle
        if self.timer_core.duration > 0:
            progress = min(100, (elapsed_seconds / self.timer_core.duration) * 100)
            self.progress_bar.setValue(int(progress))
    
    def _on_timer_state_changed(self, state):
        """Sayaç durumu değiştiğinde"""
        # Butonları güncelle
        if state == "running":
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            
            # Durum metnini güncelle
            current_session = self.session_label.text()
            self.status_label.setText(f"Şu anki durum: {current_session} (Devam Ediyor)")
            
        elif state == "paused":
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            
            # Durum metnini güncelle
            current_session = self.session_label.text()
            self.status_label.setText(f"Şu anki durum: {current_session} (Duraklatıldı)")
            
        elif state == "stopped":
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.pause_button.setText("Duraklat")
            self.reset_button.setEnabled(False)
            
            # Durum metnini güncelle
            self.status_label.setText("Şu anki durum: Hazır")
            
            # İlerleme çubuğunu sıfırla
            self.progress_bar.setValue(0)
            
            
            # Seçili seans tipine göre süreyi belirle
            if self.session_label.text() == "Çalışma Seansı":
                duration = self.pomodoro_manager.work_duration
            elif self.session_label.text() == "Kısa Mola":
                duration = self.pomodoro_manager.short_break_duration
            elif self.session_label.text() == "Uzun Mola":
                duration = self.pomodoro_manager.long_break_duration
            
            # Süreyi göster
            hours, remainder = divmod(duration * 60, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_display.setText(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    
    def _on_session_changed(self, session_type, duration):
        """Pomodoro seans tipi değiştiğinde"""
        if session_type == "work":
            self.session_label.setText("Çalışma Seansı")
            self.status_label.setText("Şu anki durum: Çalışma Seansı")
        elif session_type == "short_break":
            self.session_label.setText("Kısa Mola")
            self.status_label.setText("Şu anki durum: Kısa Mola")
        elif session_type == "long_break":
            self.session_label.setText("Uzun Mola")
            self.status_label.setText("Şu anki durum: Uzun Mola")
            
        # Süre göstergesini güncelle
        hours, remainder = divmod(duration * 60, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_display.setText(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    
    def _on_session_completed(self, session_type):
        """Bir seans tamamlandığında"""
        if session_type == "work":
            # Çalışma seansı tamamlandığında günlük istatistikleri güncelle
            self._update_daily_stats()
    
    def _update_initial_time(self):
        """Açılışta ayarlardaki çalışma süresini göster"""
        # Varsayılan olarak çalışma süresini göster
        duration = self.pomodoro_manager.work_duration
        hours, remainder = divmod(duration * 60, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_display.setText(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    
    def _update_daily_stats(self):
        """Bugünkü toplam çalışma süresini hesapla ve göster"""
        # Bugünün başlangıcı (00:00)
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Bugünün sonu (23:59:59)
        today_end = datetime.combine(today, datetime.max.time())
        
        try:
            # Veritabanından bugünkü çalışma seanslarını al
            sessions = self.pomodoro_manager.db_manager.get_sessions_by_date(today)
            
            # Toplam süreyi hesapla (sadece tamamlanan çalışma seansları)
            total_seconds = sum(session['duration'] for session in sessions 
                               if session['is_completed'] and session['session_type'] == 'work')
            
            # Saatlere ve dakikalara dönüştür
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Etiketi güncelle
            self.today_total_label.setText(f"Bugün toplam: {int(hours)} saat {int(minutes)} dakika")
        except Exception as e:
            # Hata durumunda varsayılan mesajı göster
            self.today_total_label.setText("Bugün toplam: 0 saat 0 dakika") 