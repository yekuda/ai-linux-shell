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
        "Sen bir Linux sistem yöneticisi asistanısın. "
        "Kullanıcının Türkçe veya İngilizce sorularını Linux terminal komutlarına çevir.\n"
        "\n"
        "KURALLAR:\n"
        "- SADECE çalıştırılabilir komutlar üret\n"
        "- Asla açıklama, yorum veya markdown kod bloğu ekleme\n"
        "- Her komut ayrı satırda olacak\n"
        "- Kullanıcının niyetini doğru anla ve en uygun komutu seç\n"
        "- Örnek: 'disk kullanımı' → df -h, 'çalışan servisler' → systemctl list-units --type=service --state=running\n"
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


def ai_interpret_results(user_question, commands, outputs):
    """Komut çıktılarını yorumlayarak kullanıcı dostu cevap üretir."""
    
    system_message = (
        "Sen bir sunucu asistanısın. "
        "Kullanıcının sorusuna göre komut çıktılarını yorumla ve "
        "KISA, AÇIK ve ANLAŞILIR bir Türkçe cevap ver. "
        "Teknik detaylara girmeden özet geç. "
        "Cevabın maksimum 2-3 cümle olsun."
    )
    
    prompt = f"""
Kullanıcının Sorusu: {user_question}

Çalıştırılan Komutlar:
{commands}

Komut Çıktıları:
{outputs}

Yukarıdaki bilgilere göre kullanıcının sorusunu KISA ve NET bir şekilde Türkçe cevapla.
"""

    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system_message
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
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
        
        # Tüm çıktıları topla
        all_outputs = []
        
        for cmd in commands.split("\n"):
            cmd = cmd.strip()
            if not cmd:
                continue

            print(f"▶ Çalıştırılıyor: {cmd}")
            
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd)
                out = stdout.read().decode().strip()
                err = stderr.read().decode().strip()

                # Çıktıları biriktir
                if out:
                    all_outputs.append(f"[{cmd}]\n{out}")
                if err:
                    all_outputs.append(f"[{cmd} - HATA]\n{err}")
                    
            except Exception as e:
                error_msg = f"[{cmd} - İSTİSNA]\n{str(e)}"
                all_outputs.append(error_msg)
                print(f"Komut çalıştırma hatası: {e}")

        # AI'dan sonuçları yorumlamasını iste
        if all_outputs:
            print("\n🤖 Sonuçlar yorumlanıyor...\n")
            combined_output = "\n\n".join(all_outputs)
            summary = ai_interpret_results(user_input, commands, combined_output)
            
            if summary:
                print("=" * 60)
                print(f"📊 ÖZET: {summary}")
                print("=" * 60)
            
            # Ham çıktıyı görmek isteyenler için
            while True:
                show_details = input("\nDetaylı çıktıyı görmek ister misiniz? (y/n): ").lower().strip()
                if show_details == "y":
                    print("\n--- DETAYLI ÇIKTI ---")
                    print(combined_output)
                    print("---------------------")
                    break
                elif show_details == "n" or not show_details:
                    break
                else:
                    print("⚠️  Lütfen sadece 'y' veya 'n' girin.")

    ssh.close()
    print("\n🔒 Bağlantı kapatıldı.")


if __name__ == "__main__":
    run()