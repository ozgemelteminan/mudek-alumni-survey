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

# --- TARAYICI AYARLARI (MAC İÇİN SABİTLENDİ) ---
# Senin bilgisayarındaki Chrome profil yolu
CHROME_PROFILE_PATH = "/Users/ozgemelteminan/Library/Application Support/Google/Chrome"
CHROME_PROFILE_NAME = "Default"  # Genelde 'Default' klasörüdür

BROWSER_WIDTH = 1200
BROWSER_HEIGHT = 900
HEADLESS_MODE = False  # LinkedIn güvenliği için False kalmalı

# --- ZAMANLAMA VE GÜVENLİK LİMİTLERİ ---
DELAY_BETWEEN_PROFILES = 45  # Her kişi arası 45 saniye bekle
PAGE_LOAD_TIMEOUT = 20
ELEMENT_WAIT_TIMEOUT = 10
SHORT_DELAY = 1.5
MEDIUM_DELAY = 3.0

MAX_PROFILES_PER_SESSION = 25  # Günlük en fazla 25 kişiye bak (Ban riskine karşı)

# --- DURUM KODLARI ---
STATUS_PENDING = "Bekliyor"
STATUS_SENT = "Gönderildi"
STATUS_SKIPPED = "Atlandı"
STATUS_ERROR = "Hata"

# --- MESAJ İÇERİĞİ ---
SURVEY_URL = "https://forms.google.com/ornek-anket-linki"