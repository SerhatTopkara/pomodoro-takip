# Pomodoro Takip Uygulaması

Pomodoro Takip Uygulaması, çalışma sürelerinizi etkin bir şekilde yönetmenize ve izlemenize yardımcı olan masaüstü uygulamasıdır. 
Pomodoro tekniği ile çalışma veriminizi artırın ve gün içindeki çalışma performansınızı takip edin.

![Ekran Alıntısı](https://github.com/user-attachments/assets/38a17e5f-602a-4955-b721-436dd56fa091)


## Özellikler

- **Pomodoro Tekniği Uygulaması**: Çalışma ve mola döngüleri ile verimli çalışma
- **Özelleştirilebilir Süreler**: Çalışma süreleri, kısa mola, uzun mola ve döngü sayılarını ayarlama
- **Otomatik Döngü**: Çalışma ve mola süreleri arasında otomatik geçiş
- **Sesli Uyarı**: Süre tamamlandığında sesli bildirim
- **Günlük Çalışma İstatistikleri**: Günlük toplam çalışma süresini takip etme
- **Geçmiş Çalışma Verileri**: Takvim üzerinde geçmiş çalışmaları görüntüleme
- **Grafik Analizi**: Çalışma sürelerinizi grafiklerle analiz etme

## Kurulum

### Gereksinimler

- Python 3.8 veya üstü
- PyQt6
- Matplotlib
- Pygame (ses özellikleri için)

### Adım Adım Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/SerhatTopkara/pomodoro-takip.git
cd pomodoro-takip
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python3 -m venv pomodoro_env
source pomodoro_env/bin/activate  # Linux/macOS
# VEYA
pomodoro_env\Scripts\activate.bat  # Windows
```

3. Gerekli paketleri yükleyin:
```bash
pip install PyQt6 matplotlib pygame
```

4. Uygulamayı çalıştırın:
```bash
python main.py
```

## Kullanım

1. **Başlangıç**: Ana ekranda "Başlat" butonuna tıklayarak pomodoro döngünüzü başlatın.
2. **Duraklatma/Devam Ettirme**: İhtiyaç duyduğunuzda "Duraklat" veya "Devam Et" butonlarını kullanın.
3. **Sıfırlama**: Gerekirse "Sıfırla" butonu ile mevcut pomodoro oturumunu sıfırlayın.
4. **Ayarlar**: Ayarlar bölümünden süreleri kendi ihtiyaçlarınıza göre düzenleyin.
5. **İstatistikler**: "İstatistikler" sekmesini kullanarak çalışma verilerinizi görselleştirin.
6. **Takvim**: "Takvim" sekmesinde geçmiş çalışma kayıtlarınızı görüntüleyin.

## Pomodoro Tekniği Nedir?

Pomodoro Tekniği, Francesco Cirillo tarafından 1980'lerde geliştirilen bir zaman yönetimi yöntemidir. Teknik, şu temel adımlardan oluşur:

1. Bir görev belirleyin
2. 25 dakika (bir pomodoro) boyunca kesintisiz çalışın
3. Kısa bir mola verin (5 dakika)
4. 4 pomodoro tamamlandıktan sonra uzun bir mola verin (15-30 dakika)
5. Döngüyü tekrarlayın

Bu uygulama, Pomodoro Tekniği'ni kişiselleştirmenize olanak tanır ve çalışma alışkanlıklarınızı optimize etmenize yardımcı olur.

