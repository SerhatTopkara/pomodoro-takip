from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSpinBox, QCheckBox, QPushButton, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        
        self.setWindowTitle("Pomodoro Ayarları")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Ayarlar diyalog arayüzünü oluştur"""
        main_layout = QVBoxLayout(self)
        
        # Zaman ayarları grubu
        time_group = QGroupBox("Zaman Ayarları")
        time_layout = QFormLayout(time_group)
        
        self.work_spinbox = QSpinBox()
        self.work_spinbox.setRange(1, 120)
        self.work_spinbox.setSuffix(" dk")
        time_layout.addRow("Çalışma Süresi:", self.work_spinbox)
        
        self.short_break_spinbox = QSpinBox()
        self.short_break_spinbox.setRange(1, 60)
        self.short_break_spinbox.setSuffix(" dk")
        time_layout.addRow("Kısa Mola Süresi:", self.short_break_spinbox)
        
        self.long_break_spinbox = QSpinBox()
        self.long_break_spinbox.setRange(5, 120)
        self.long_break_spinbox.setSuffix(" dk")
        time_layout.addRow("Uzun Mola Süresi:", self.long_break_spinbox)
        
        self.sessions_spinbox = QSpinBox()
        self.sessions_spinbox.setRange(1, 10)
        self.sessions_spinbox.setSuffix(" seans")
        time_layout.addRow("Uzun Mola Öncesi Seans Sayısı:", self.sessions_spinbox)
        
        main_layout.addWidget(time_group)
        
        # Bildirim ayarları grubu
        notification_group = QGroupBox("Bildirim Ayarları")
        notification_layout = QVBoxLayout(notification_group)
        
        self.sound_checkbox = QCheckBox("Süre dolduğunda alarm çal")
        notification_layout.addWidget(self.sound_checkbox)
        
        main_layout.addWidget(notification_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self._save_settings)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def _load_settings(self):
        """Ayarları veritabanından yükle"""
        settings = self.db_manager.get_settings()
        
        self.work_spinbox.setValue(settings['work_duration'])
        self.short_break_spinbox.setValue(settings['short_break_duration'])
        self.long_break_spinbox.setValue(settings['long_break_duration'])
        self.sessions_spinbox.setValue(settings['sessions_before_long_break'])
        self.sound_checkbox.setChecked(bool(settings['sound_enabled']))
    
    def _save_settings(self):
        """Ayarları veritabanına kaydet"""
        settings = {
            'work_duration': self.work_spinbox.value(),
            'short_break_duration': self.short_break_spinbox.value(),
            'long_break_duration': self.long_break_spinbox.value(),
            'sessions_before_long_break': self.sessions_spinbox.value(),
            'sound_enabled': 1 if self.sound_checkbox.isChecked() else 0
        }
        
        self.db_manager.update_settings(settings)
        self.accept() 