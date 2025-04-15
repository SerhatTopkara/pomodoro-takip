import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.database import DatabaseManager

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Takip")

    # Gerekli dizinleri oluştur.
    os.makedirs("data", exist_ok=True)
    os.makedirs("resources/sounds", exist_ok=True)

    # Veritabanı bağlantısını oluştur.
    db_manager = DatabaseManager()
    db_manager.setup_database()

    # Ana pencereyi oluştur ve göster.
    window = MainWindow(db_manager)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()


