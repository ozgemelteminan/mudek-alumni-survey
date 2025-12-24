#!/usr/bin/env python3
"""
MÜDEK Alumni Survey - FULL AUTO (No Human Loop)
"""
import time
import config
from sheets_reader import GoogleSheetsReader
from linkedin_automation import LinkedInAutomation

def main():
    print("\n🚀 OTOMATİK MOD BAŞLATILIYOR (SADECE BAĞLANTILAR İÇİN)...")
    
    # 1. Excel'i Oku
    sheets = GoogleSheetsReader()
    pending_list = sheets.get_pending_alumni()
    print(f"📄 Listede {len(pending_list)} kişi var.")

    if not pending_list:
        print("🎉 Yapılacak iş yok.")
        return

    # 2. Botu Aç
    bot = LinkedInAutomation()
    if not bot.check_login_status():
        print("❌ Önce giriş yapmalısın! Tarayıcıda giriş yap ve Enter'a bas.")
        input()
    
    # 3. Seri Gönderim Döngüsü
    count = 0
    for person in pending_list:
        if count >= config.MAX_PROFILES_PER_SESSION:
            print("🛑 Günlük limit doldu.")
            break

        name = person.get('name', '')
        url = person.get('linkedin_url', '')
        if not url.startswith("http"): url = "https://" + url
        row_num = person.get('_row_num')
        
        print(f"[{count+1}] {name}...", end=" ")

        # Mesajı Hazırla
        first_name = name.split()[0] if name else "Mezunumuz"
        msg = (
            f"Merhaba {first_name}, nasılsın?\n\n"
            f"{person.get('graduation_year', '')} mezunlarımız için MÜDEK kapsamında anket yapıyoruz. "
            f"Katkın çok değerli: {config.SURVEY_URL}\n\n"
            f"Sevgiler, Özge"
        )

        # GÖNDER (Soru sormadan)
        status = bot.send_message_fast(url, msg)

        if status == 'sent':
            sheets.update_status(row_num, "Gönderildi")
            print("✅ GÖNDERİLDİ")
        else:
            sheets.update_status(row_num, "Hata")
            print("❌ HATA")

        count += 1
        # Her kişi arası 5 saniye bekle (Ban yememek için minimum süre)
        time.sleep(5) 

    bot.close()
    print("🏁 İşlem Tamamlandı.")

if __name__ == "__main__":
    main()