"""
Configuration file for MÜDEK Alumni Survey System.
"""
import os
from pathlib import Path

# --- PROJE YOLU ---
BASE_DIR = Path(__file__).parent.absolute()
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
CAMPAIGN_LOG_PATH = LOGS_DIR / "campaign_log.csv"

# --- 2. TARAYICI AYARLARI (BOT) ---
# Bot, proje klasörü içinde 'bot_chrome_data' adında kendine ait temiz bir Chrome açar.
CHROME_PROFILE_PATH = os.path.join(BASE_DIR, "bot_chrome_data")
CHROME_PROFILE_NAME = ""  

BROWSER_WIDTH = 1200
BROWSER_HEIGHT = 900
HEADLESS_MODE = False  # LinkedIn güvenliği için False kalmalıymış?

# --- GOOGLE SHEETS AYARLARI ---
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

# --- ZAMANLAMA VE GÜVENLİK LİMİTLERİ ---
DELAY_BETWEEN_PROFILES = 45  
PAGE_LOAD_TIMEOUT = 60
ELEMENT_WAIT_TIMEOUT = 30
SHORT_DELAY = 1.5
MEDIUM_DELAY = 3.0

MAX_PROFILES_PER_SESSION = 25  # Günlük en fazla 25 kişiye bak (spam riskini azaltmak için)

# --- DURUM KODLARI ---
STATUS_PENDING = "Bekliyor"
STATUS_SENT = "Gönderildi"
STATUS_SKIPPED = "Atlandı"
STATUS_ERROR = "Hata"

# --- MESAJ İÇERİĞİ ---
SURVEY_URL = "https://forms.google.com/ornek-anket-linki"
CONTACT_EMAIL = "ornek@univ.edu.tr"  # İsteğe bağlı ileride eklenebilir
CONTACT_PHONE = "0555-555-5555"      # İsteğe bağlı ileride eklenebilir

# --- LOGLAMA AYARLARI ---
LOG_LEVEL = "INFO"
CONSOLE_OUTPUT = True
FILE_LOGGING = True