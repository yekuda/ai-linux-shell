# AI-SH - AI-Powered Server Management

AI-SH (AI Shell), doğal dil komutlarıyla Linux sunucularınızı yönetmenize olanak sağlayan, Google Gemini destekli bir araçtır.

## 🌟 Özellikler

- 🤖 **AI-Destekli Komut Üretimi**: Türkçe veya İngilizce doğal dil komutlarınızı Linux terminal komutlarına çevirir
- 🔒 **Güvenli SSH Bağlantısı**: Paramiko ile güvenli sunucu bağlantısı
- ✅ **Manuel Onay**: Komutlar çalıştırılmadan önce onayınızı alır
- ⚡ **Hızlı Model**: Gemini 2.5 Flash Lite modeli ile hızlı yanıtlar

## 📋 Gereksinimler

- Python 3.7+
- Google Gemini API anahtarı
- SSH erişimi olan bir Linux sunucusu

## 🚀 Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/KULLANICI_ADINIZ/ai-server.git
cd ai-server
```

2. Gerekli paketleri yükleyin:
```bash
pip install paramiko google-generativeai python-dotenv
```

3. `.env.example` dosyasını `.env` olarak kopyalayın ve bilgilerinizi girin:
```bash
cp .env.example .env
```

4. `.env` dosyasını düzenleyin:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SERVER_HOST=your_server_ip
SERVER_USER=your_username
SERVER_PASS=your_password
```

## 💻 Kullanım

Programı çalıştırın:
```bash
python main.py
```

Ardından Türkçe veya İngilizce komutlarınızı yazın:
```
Görev > disk kullanımını göster
Görev > son 10 log satırını göster
Görev > çalışan servisleri listele
```

## 🔐 Güvenlik

- `.env` dosyası asla GitHub'a yüklenmez (`.gitignore` ile korunur)
- Tüm komutlar çalıştırılmadan önce manuel onaya tabidir
- SSH bağlantısı güvenli şekilde yapılır

## 📝 Lisans

MIT License

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır. Büyük değişiklikler için lütfen önce bir issue açın.
