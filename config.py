"""
Configuration file for MÜDEK Alumni Survey System.
"""
import os
from pathlib import Path

# --- 1. PROJE YOLU (EN BAŞTA OLMALI) ---
BASE_DIR = Path(__file__).parent.absolute()
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
CAMPAIGN_LOG_PATH = LOGS_DIR / "campaign_log.csv"

# --- 2. TARAYICI AYARLARI (BOT İÇİN ÖZEL PROFİL) ---
# Bot, proje klasörü içinde 'bot_chrome_data' adında kendine ait temiz bir Chrome açar.
# Bu sayede "Dosya kilitli" hatası asla almazsın.
CHROME_PROFILE_PATH = os.path.join(BASE_DIR, "bot_chrome_data")
CHROME_PROFILE_NAME = ""  # Boş bırakıyoruz

BROWSER_WIDTH = 1200
BROWSER_HEIGHT = 900
HEADLESS_MODE = False  # LinkedIn güvenliği için False kalmalı

# --- 3. GOOGLE SHEETS AYARLARI ---
SPREADSHEET_NAME = "MUDEK_Alumni_Survey"
WORKSHEET_NAME = "LinkedIn_Contacts"

# Excel sütun isimleri ile kod değişkenleri eşleşmesi
COLUMN_MAPPING = {
    "name": "Ad Soyad",
    "linkedin_url": "LinkedIn URL",
    "graduation_year": "Mezuniyet Yılı",
    "company": "Şirket",
    "position": "Pozisyon",
    "status": "Durum"
}

# --- 4. ZAMANLAMA VE GÜVENLİK LİMİTLERİ ---
DELAY_BETWEEN_PROFILES = 45  # Her kişi arası 45 saniye bekle
PAGE_LOAD_TIMEOUT = 60
ELEMENT_WAIT_TIMEOUT = 30
SHORT_DELAY = 1.5
MEDIUM_DELAY = 3.0

MAX_PROFILES_PER_SESSION = 25  # Günlük en fazla 25 kişiye bak

# --- 5. DURUM KODLARI ---
STATUS_PENDING = "Bekliyor"
STATUS_SENT = "Gönderildi"
STATUS_SKIPPED = "Atlandı"
STATUS_ERROR = "Hata"

# --- 6. MESAJ İÇERİĞİ ---
SURVEY_URL = "https://forms.google.com/ornek-anket-linki"
CONTACT_EMAIL = "ornek@univ.edu.tr"
CONTACT_PHONE = "0555-555-5555"

# --- 7. LOGLAMA AYARLARI ---
LOG_LEVEL = "INFO"
CONSOLE_OUTPUT = True
FILE_LOGGING = True