import paramiko
import google.generativeai as genai
import getpass
import os
from dotenv import load_dotenv

# ---------- ENV YÜKLEME ----------
load_dotenv()

GEMINI_API = os.getenv("GEMINI_API_KEY")

# GÜNCELLEME: Listenizdeki en uygun hızlı model seçildi
MODEL = "gemini-2.5-flash-lite"

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_USER = os.getenv("SERVER_USER")
SERVER_PASS = os.getenv("SERVER_PASS")
# -----------------------------------

# ENV kontrolü
if not GEMINI_API:
    print("❌ HATA: .env içinde GEMINI_API_KEY bulunamadı!")
    exit(1)
if not SERVER_HOST or not SERVER_USER or not SERVER_PASS:
    print("❌ HATA: .env içinde SERVER_HOST / SERVER_USER / SERVER_PASS eksik!")
    exit(1)

genai.configure(api_key=GEMINI_API)


def ai_to_commands(prompt):
    """Doğal dili çalıştırılabilir Linux komutlarına çevirir."""
    
    system_message = (
        "Sadece Linux terminal komutları üret. "
        "Kullanıcı ne sorarsa sorsun asla açıklama yazma. "
        "Asla yorum yapma. "
        "Sadece çalıştırılabilir komutlar üret. "
        "Eğer soru gereksizse bile bir komut üret. "
        "Komutları asla İngilizce açıklama içermeyecek. "
        "Her komut ayrı satırda olacak. "
        "Terminal olmayan çıktı yazma."
    )


    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system_message
    )

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Temizlik: Markdown bloklarını kaldır
        text = text.replace("```bash", "").replace("```sh", "").replace("```", "").strip()
        return text
        
    except Exception as e:
        print(f"\n❌ API Hatası: {e}")
        return ""


def run():
    print(f"=== AI-SH (Gemini: {MODEL}) — Yapay Zeka Destekli Sunucu Yönetimi ===\n")

    print(f"Sunucuya bağlanılıyor: {SERVER_HOST} ...\n")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASS)
        print("✅ Bağlantı başarılı!\n")
    except Exception as e:
        print(f"❌ Bağlantı Hatası: {e}")
        exit(1)

    while True:
        try:
            user_input = input("\nGörev > ").strip()
        except KeyboardInterrupt:
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            break

        if not user_input:
            continue

        print("\n🤖 Gemini komutları üretiyor...")
        commands = ai_to_commands(user_input)

        if not commands:
            print("❌ Komut üretilemedi veya hata oluştu.")
            continue

        print("\n--- ÖNERİLEN KOMUTLAR ---")
        print(commands)
        print("-------------------------")

        approve = input("Uygulansın mı? (y/n): ").lower()
        if approve != "y":
            print("❌ İptal edildi.")
            continue

        print("\n🚀 Komutlar uygulanıyor...\n")
        
        for cmd in commands.split("\n"):
            cmd = cmd.strip()
            if not cmd:
                continue

            print(f"▶ Çalıştırılıyor: {cmd}")
            
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd)
                out = stdout.read().decode().strip()
                err = stderr.read().decode().strip()

                if out:
                    print(f"[ÇIKTI]\n{out}")
                if err:
                    print(f"[HATA]\n{err}")
            except Exception as e:
                print(f"Komut çalıştırma hatası: {e}")

    ssh.close()
    print("\n🔒 Bağlantı kapatıldı.")


if __name__ == "__main__":
    run()