from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from ui.timer_widget import TimerWidget
from ui.calendar_widget import CalendarWidget
from ui.statistics_widget import StatisticsWidget
from ui.settings_dialog import SettingsDialog

from core.timer import TimerCore
from core.pomodoro import PomodoroManager

import os
import sys
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        
        self.db_manager = db_manager
        
        # Pencere özelliklerini ayarla.
        self.setWindowTitle("Pomodoro Takip Uygulaması")
        self.setMinimumSize(800, 600)
        
        # Çekirdek bileşenleri oluştur.
        self.timer_core = TimerCore()
        self.pomodoro_manager = PomodoroManager(self.timer_core, self.db_manager)
        
        # Arayüz kurulumu.
        self._setup_ui()
        
        # Sinyalleri bağla.
        self._connect_signals()
    
    def _setup_ui(self):
        """Ana arayüzü kur"""
        # Ana widget ve layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Sekmeler
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Sayaç sekmesi
        self.timer_widget = TimerWidget(self.timer_core, self.pomodoro_manager)
        self.tab_widget.addTab(self.timer_widget, "Sayaç")
        
        # Takvim sekmesi
        self.calendar_widget = CalendarWidget(self.db_manager)
        self.tab_widget.addTab(self.calendar_widget, "Takvim")
        
        # İstatistik sekmesi
        self.statistics_widget = StatisticsWidget(self.db_manager)
        self.tab_widget.addTab(self.statistics_widget, "İstatistikler")
        
        # Alt menü butonları
        button_layout = QHBoxLayout()
        
        # Ayarlar butonu
        self.settings_button = QPushButton("Ayarlar")
        self.settings_button.clicked.connect(self._open_settings)
        button_layout.addWidget(self.settings_button)
        
        
        
        
        
        
        main_layout.addLayout(button_layout)
        
        self.setCentralWidget(central_widget)
    
    def _connect_signals(self):
        """Sinyalleri bağla"""
        # Pomodoro seansı tamamlandığında
        self.pomodoro_manager.session_completed.connect(self._on_session_completed)
        
        # Sekme değiştiğinde
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _on_session_completed(self, session_type):
        """Bir seans tamamlandığında"""
        # Sadece çalışma seanslarını veritabanına kaydet.
        if session_type == "work":
            start_time = self.timer_core.start_time
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())
            
            self.db_manager.save_session(
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                is_completed=True,
                session_type="work"
            )
            
            
            
            
            if self.tab_widget.currentIndex() == 1:  # Takvim sekmesi
                self.calendar_widget.update_calendar()
            elif self.tab_widget.currentIndex() == 2:  # İstatistik sekmesi
                self.statistics_widget.update_statistics()
    
    def _on_tab_changed(self, index):
        """Sekme değiştiğinde"""
        if index == 1:  # Takvim sekmesi
            self.calendar_widget.update_calendar()
        elif index == 2:  # İstatistik sekmesi
            self.statistics_widget.update_statistics()
    
    def _open_settings(self):
        """Ayarlar penceresini aç"""
        dialog = SettingsDialog(self.db_manager, self)
        if dialog.exec():
            # Ayarlar değiştiyse, pomodoro yöneticisini güncelle
            self.pomodoro_manager._load_settings()
    
    def closeEvent(self, event):
        """Uygulama kapatılırken"""
        # Devam eden bir çalışma seansı varsa sor
        if self.timer_core.state == "running" and self.pomodoro_manager.current_session_type == "work":
            reply = QMessageBox.question(
                self, 
                "Çıkış Onayı",
                "Devam eden bir çalışma seansı var. Çıkmak istediğinize emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Mevcut seansı kaydet
                start_time = self.timer_core.start_time
                end_time = datetime.now()
                duration = int((end_time - start_time).total_seconds())
                
                self.db_manager.save_session(
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    is_completed=False,
                    session_type="work"
                )
                
                # Veritabanı bağlantısını kapat
                self.db_manager.close()
                event.accept()
            else:
                event.ignore()
        else:
            # Veritabanı bağlantısını kapat
            self.db_manager.close()
            event.accept() 