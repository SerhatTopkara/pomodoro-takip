from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                           QLabel, QListWidget, QFrame, QListWidgetItem)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, date

class CalendarWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        
        self.db_manager = db_manager
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Takvim arayüzünü oluştur"""
        main_layout = QHBoxLayout(self)
        
        # Sol taraf: Takvim
        calendar_layout = QVBoxLayout()
        
        calendar_label = QLabel("Çalışma Günleri")
        calendar_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        calendar_layout.addWidget(calendar_label)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        calendar_layout.addWidget(self.calendar)
        
        # Takvimin altında toplam süre bilgisi 
        self.month_summary_label = QLabel("Bu ay toplam: 0 saat")
        self.month_summary_label.setStyleSheet("color: #0066cc;")  # Mavi renk
        calendar_layout.addWidget(self.month_summary_label)
        
        main_layout.addLayout(calendar_layout, 2)  # 2/3 oranında alan kapla
        
        # Sağ taraf: Seçili günün çalışma seansları
        sessions_layout = QVBoxLayout()
        
        self.date_label = QLabel("Seçili Gün: " + QDate.currentDate().toString("dd.MM.yyyy"))
        self.date_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        sessions_layout.addWidget(self.date_label)
        
        # Toplam çalışma süresini mavi yap
        self.total_label = QLabel("Toplam Çalışma: 0 saat")
        self.total_label.setStyleSheet("color: #0066cc;")  # Mavi renk
        sessions_layout.addWidget(self.total_label)
        
        # Seans listesi
        self.sessions_list = QListWidget()
        sessions_layout.addWidget(self.sessions_list)
        
        main_layout.addLayout(sessions_layout, 1)  # 1/3 oranında alan kapla
        
        # Takvimi bugüne ayarla
        self.calendar.setSelectedDate(QDate.currentDate())
        self.update_calendar()
    
    def _connect_signals(self):
        """Sinyalleri bağla"""
        self.calendar.selectionChanged.connect(self._on_date_selected)
    
    def _on_date_selected(self):
        """Takvimde bir gün seçildiğinde"""
        selected_date = self.calendar.selectedDate()
        selected_date_py = date(selected_date.year(), selected_date.month(), selected_date.day())
        self.date_label.setText(f"Seçili Gün: {selected_date_py.strftime('%d.%m.%Y')}")
        
        # Seçili günün çalışma seanslarını göster
        self._load_sessions_for_date(selected_date_py)
    
    def _load_sessions_for_date(self, date):
        """Belirli bir günün çalışma seanslarını yükle"""
        self.sessions_list.clear()
        
        # Veritabanından seansları al
        sessions = self.db_manager.get_sessions_by_date(date)
        
        total_duration = 0
        
        for session in sessions:
            if session['session_type'] == 'work':
                # Başlangıç ve bitiş zamanları
                start_time = datetime.fromisoformat(session['start_time'])
                end_time = datetime.fromisoformat(session['end_time'])
                
                # Süreyi formatlayarak göster
                duration = session['duration']
                total_duration += duration
                
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                # Liste öğesi oluştur
                item_text = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} | {hours}s {minutes}dk"
                
                if session['is_completed']:
                    item_text += " | Tamamlandı"
                else:
                    item_text += " | Yarım kaldı"
                
                item = QListWidgetItem(item_text)
                self.sessions_list.addItem(item)
        
        # Toplam süreyi göster
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.total_label.setText(f"Toplam Çalışma: {hours}s {minutes}dk")
    
    def update_calendar(self):
        """Takvimi güncelle - Çalışılan günleri işaretle"""
        # Mevcut ayın 1. günü ve son günü
        current_year_month = self.calendar.yearShown(), self.calendar.monthShown()
        first_day = QDate(current_year_month[0], current_year_month[1], 1)
        last_day = first_day.addMonths(1).addDays(-1)
        
        # Veritabanından bu aralıktaki çalışma günlerini çek
        start_date = date(first_day.year(), first_day.month(), first_day.day())
        end_date = date(last_day.year(), last_day.month(), last_day.day())
        
        statistics = self.db_manager.get_statistics(start_date, end_date)
        
        # Ay toplamını hesapla
        total_monthly_duration = sum(stat['total_duration'] for stat in statistics)
        hours, remainder = divmod(total_monthly_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.month_summary_label.setText(f"Bu ay toplam: {hours}s {minutes}dk")
        
        # Seçili günün seanslarını göster
        selected_date = self.calendar.selectedDate()
        selected_date_py = date(selected_date.year(), selected_date.month(), selected_date.day())
        self._load_sessions_for_date(selected_date_py) 