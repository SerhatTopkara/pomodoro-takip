from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from datetime import datetime, timedelta

class TimerCore(QObject):

    tick = pyqtSignal(int) # Geçen süre(saniye)
    completed = pyqtSignal() # Süre tamamlandığında
    state_changed = pyqtSignal(str) # Durum değiştiğinde

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_tick)
        self.timer.setInterval(1000)

        self.start_time = None
        self.pause_time = None
        self.elapsed_seconds = 0
        self.duration = 0 # Hedef süre(saniye)
        self.state = "stopped" 
    
    def start(self, duration_minutes=25):

        self.duration = duration_minutes * 60

        if self.state == "paused":
            # Duraklatılmış ise kaldığı yerden devam et.
            self.elapsed_seconds = (datetime.now() - self.start_time).total_seconds() - self.pause_time.total_seconds()
        else:

            self.start_time = datetime.now()
            self.elapsed_seconds = 0

        self.state = "running"
        self.timer.start()
        self.state_changed.emit(self.state)

    def pause(self):
        
        if self.state == "running":
            self.timer.stop()
            self.pause_time = datetime.now() - self.start_time
            self.state = "paused"
            self.state_changed.emit(self.state)

    def resume(self):

        if self.state == "paused":
            self.start_time = datetime.now() - self.pause_time
            self.state = "running"
            self.timer.start()
            self.state_changed.emit(self.state)

    def reset(self):

        self.timer.stop()
        self.elapsed_seconds = 0
        self.start_time = None
        self.pause_time = None
        self.state = "stopped"
        self.state_changed.emit(self.state)
        self.tick.emit(0)

    def get_elapsed_time(self):

        hours, remainder = divmod(self.elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def get_remaining_time(self):

        remaining = max(0, self.duration - self.elapsed_seconds)
        hours, remainder = divmod(remaining, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def _on_tick(self):

        self.elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
        self.tick.emit(int(self.elapsed_seconds))

        # Süre doldu mu?
        if self.elapsed_seconds >= self.duration:
            self.timer.stop()
            self.state = "stopped"
            self.state_changed.emit(self.state)
            self.completed.emit()   