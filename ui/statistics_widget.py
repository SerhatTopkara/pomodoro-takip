from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QFrame, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

# Matplotlib importları
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta, date

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

class StatisticsWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        
        self.db_manager = db_manager
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """İstatistik arayüzünü oluştur"""
        main_layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel("Çalışma İstatistikleri")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Filtreleme alanı
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Dönem:"))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Son 7 Gün", "Son 30 Gün", "Bu Ay", "Özel Tarih Aralığı"])
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addSpacing(20)
        
        # Özel tarih aralığı için
        self.start_date_label = QLabel("Başlangıç:")
        filter_layout.addWidget(self.start_date_label)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        filter_layout.addWidget(self.start_date_edit)
        
        self.end_date_label = QLabel("Bitiş:")
        filter_layout.addWidget(self.end_date_label)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date_edit)
        
        # Özel tarih aralığı seçili değilse gizle
        self.start_date_label.setVisible(False)
        self.start_date_edit.setVisible(False)
        self.end_date_label.setVisible(False)
        self.end_date_edit.setVisible(False)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Özet bilgiler
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        summary_layout = QHBoxLayout(summary_frame)
        
        # Toplam çalışma süresi
        total_layout = QVBoxLayout()
        total_label = QLabel("Toplam Çalışma")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(total_label)
        
        self.total_time_label = QLabel("0s 0dk")
        self.total_time_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_time_label.setStyleSheet("color: #0066cc;")  # Mavi renk
        total_layout.addWidget(self.total_time_label)
        
        summary_layout.addLayout(total_layout)
        
        # Ortalama günlük süre
        average_layout = QVBoxLayout()
        average_label = QLabel("Günlük Ortalama")
        average_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        average_layout.addWidget(average_label)
        
        self.average_time_label = QLabel("0s 0dk")
        self.average_time_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.average_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.average_time_label.setStyleSheet("color: #0066cc;")  # Mavi renk
        average_layout.addWidget(self.average_time_label)
        
        summary_layout.addLayout(average_layout)
        
        # Toplam seans sayısı
        session_layout = QVBoxLayout()
        session_label = QLabel("Toplam Seans")
        session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        session_layout.addWidget(session_label)
        
        self.session_count_label = QLabel("0")
        self.session_count_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.session_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        session_layout.addWidget(self.session_count_label)
        
        summary_layout.addLayout(session_layout)
        
        main_layout.addWidget(summary_frame)
        
        # Grafik alanı
        self.canvas = MatplotlibCanvas(self, width=10, height=5, dpi=100)
        main_layout.addWidget(self.canvas)
        
        # İstatistikleri güncelle
        self.update_statistics()
    
    def _connect_signals(self):
        """Sinyalleri bağla"""
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        self.start_date_edit.dateChanged.connect(self.update_statistics)
        self.end_date_edit.dateChanged.connect(self.update_statistics)
    
    def _on_period_changed(self, index):
        """Periyot değiştiğinde"""
        # Özel tarih aralığı seçildiyse, tarih editlerini göster
        custom_range = (index == 3)  # "Özel Tarih Aralığı" indeksi
        
        self.start_date_label.setVisible(custom_range)
        self.start_date_edit.setVisible(custom_range)
        self.end_date_label.setVisible(custom_range)
        self.end_date_edit.setVisible(custom_range)
        
        self.update_statistics()
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        # Tarih aralığını belirle
        end_date = datetime.now().date()
        start_date = end_date
        
        period_index = self.period_combo.currentIndex()
        
        if period_index == 0:  # Son 7 Gün
            start_date = end_date - timedelta(days=6)
        elif period_index == 1:  # Son 30 Gün
            start_date = end_date - timedelta(days=29)
        elif period_index == 2:  # Bu Ay
            start_date = end_date.replace(day=1)
        elif period_index == 3:  # Özel Tarih Aralığı
            date_edit = self.start_date_edit.date()
            start_date = date(date_edit.year(), date_edit.month(), date_edit.day())
            
            date_edit = self.end_date_edit.date()
            end_date = date(date_edit.year(), date_edit.month(), date_edit.day())
        
        # Veritabanından istatistikleri çek
        statistics = self.db_manager.get_statistics(start_date, end_date)
        
        # Hiç veri yoksa boş grafik göster
        if not statistics:
            self._clear_graph()
            self._update_summary(0, 0, 0)
            return
        
        # Grafik verilerini oluştur
        dates = [datetime.fromisoformat(stat['work_date']) for stat in statistics]
        durations = [stat['total_duration'] / 3600.0 for stat in statistics]  # Saate çevir
        
        # Toplam süre ve seans sayısı
        total_duration = sum(stat['total_duration'] for stat in statistics)
        total_sessions = sum(stat['session_count'] for stat in statistics)
        
        # Ortalama günlük süre (çalışılan günler üzerinden)
        avg_duration = total_duration / len(statistics)
        
        # Özet bilgileri güncelle
        self._update_summary(total_duration, avg_duration, total_sessions)
        
        # Grafiği çiz
        self._plot_graph(dates, durations)
    
    def _update_summary(self, total_duration, avg_duration, total_sessions):
        """Özet bilgileri güncelle"""
        # Toplam süre
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.total_time_label.setText(f"{int(hours)}s {int(minutes)}dk")
        
        # Ortalama süre
        hours, remainder = divmod(avg_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.average_time_label.setText(f"{int(hours)}s {int(minutes)}dk")
        
        # Toplam seans
        self.session_count_label.setText(str(total_sessions))
    
    def _plot_graph(self, dates, durations):
        """Grafiği çiz"""
        # Önceki grafiği temizle
        self.canvas.axes.clear()
        
        # Grafiği daha anlaşılır hale getir - sadece çubuk grafik kullan
        bars = self.canvas.axes.bar(dates, durations, width=0.6, color='#0066cc', alpha=0.8)
        
        # Çubukların üzerine süreleri yaz
        for bar, duration in zip(bars, durations):
            height = bar.get_height()
            if height > 0:  # Sadece süresi olan günlerde göster
                self.canvas.axes.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                     f'{height:.1f} saat', ha='center', va='bottom', 
                                     fontsize=9, color='#0066cc', fontweight='bold')
        
        # Eksenleri ayarla
        self.canvas.axes.set_ylabel('Çalışma Süresi (Saat)', fontsize=11, fontweight='bold')
        self.canvas.axes.set_xlabel('Tarih', fontsize=11, fontweight='bold')
        
        # Tarih formatını ayarla - daha anlaşılır olması için
        self.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        self.canvas.axes.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 7)))
        
        # Izgara çizgilerini ekle - daha belirgin ve anlaşılır olması için
        self.canvas.axes.grid(axis='y', linestyle='--', alpha=0.4, color='gray')
        
        # X ekseni etiketlerini döndür
        for label in self.canvas.axes.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
        
        # Grafik başlığı ekle
        period_text = self.period_combo.currentText()
        self.canvas.axes.set_title(f"{period_text} Çalışma Süreleri", fontsize=12, fontweight='bold')
        
        # Y ekseni maksimum değerini hafif yükselt (etiketler için)
        if durations:
            y_max = max(durations) * 1.2
            self.canvas.axes.set_ylim(0, y_max)
        
        self.canvas.fig.tight_layout()
        self.canvas.draw()
    
    def _clear_graph(self):
        """Grafiği temizle"""
        self.canvas.axes.clear()
        self.canvas.axes.text(0.5, 0.5, "Bu tarih aralığında veri bulunamadı.", 
                             ha='center', va='center', fontsize=12)
        self.canvas.fig.tight_layout()
        self.canvas.draw() 