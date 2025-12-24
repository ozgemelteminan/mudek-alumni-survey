"""
Configuration file for MÜDEK Alumni Survey System.
Modify these settings according to your needs.
"""

import os
from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================

# Base directory of the project
BASE_DIR = Path(__file__).parent.absolute()

# Path to Google API credentials JSON file
CREDENTIALS_PATH = BASE_DIR / "credentials.json"

# Path to logs directory
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Campaign log file
CAMPAIGN_LOG_PATH = LOGS_DIR / "campaign_log.csv"

# =============================================================================
# GOOGLE SHEETS CONFIGURATION
# =============================================================================

# Name of your Google Spreadsheet
SPREADSHEET_NAME = "MUDEK_Alumni_Survey"

# Name of the worksheet containing alumni data
WORKSHEET_NAME = "LinkedIn_Contacts"

# Expected column names in the spreadsheet
COLUMN_MAPPING = {
    "name": "Ad Soyad",              # Alumni full name
    "linkedin_url": "LinkedIn URL",   # LinkedIn profile URL
    "graduation_year": "Mezuniyet Yılı",  # Graduation year
    "company": "Şirket",              # Current company
    "position": "Pozisyon",           # Current position
    "email": "E-posta",               # Email (optional)
    "status": "Durum"                 # Status tracking column
}

# =============================================================================
# BROWSER CONFIGURATION
# =============================================================================

# Chrome user data directory (to use existing LinkedIn session)
# Windows: C:/Users/USERNAME/AppData/Local/Google/Chrome/User Data
# macOS: /Users/USERNAME/Library/Application Support/Google/Chrome
# Linux: /home/USERNAME/.config/google-chrome
CHROME_PROFILE_PATH = None  # Set to None to use a fresh browser

# Specific Chrome profile to use (e.g., "Profile 1", "Default")
CHROME_PROFILE_NAME = "Default"

# Browser window size
BROWSER_WIDTH = 1200
BROWSER_HEIGHT = 900

# Headless mode (set to True for background operation - NOT RECOMMENDED for LinkedIn)
HEADLESS_MODE = False

# =============================================================================
# AUTOMATION TIMING SETTINGS
# =============================================================================

# Delay between processing each profile (in seconds)
# Recommended: 30-60 seconds to avoid detection
DELAY_BETWEEN_PROFILES = 45

# Page load timeout (in seconds)
PAGE_LOAD_TIMEOUT = 20

# Element wait timeout (in seconds)
ELEMENT_WAIT_TIMEOUT = 15

# Short delays for natural behavior (in seconds)
SHORT_DELAY = 1.5
MEDIUM_DELAY = 3.0

# =============================================================================
# CAMPAIGN SETTINGS
# =============================================================================

# Maximum number of profiles to process in one session
# Recommended: 20-30 per day to avoid account restrictions
MAX_PROFILES_PER_SESSION = 25

# Skip already processed profiles (checks 'status' column)
SKIP_PROCESSED = True

# Status values
STATUS_PENDING = "Bekliyor"
STATUS_SENT = "Gönderildi"
STATUS_SKIPPED = "Atlandı"
STATUS_ERROR = "Hata"

# =============================================================================
# SURVEY INFORMATION
# =============================================================================

# Survey URL to include in messages
SURVEY_URL = "https://forms.google.com/your-survey-link-here"

# Department/Faculty information
DEPARTMENT_NAME = "Bilgisayar Mühendisliği Bölümü"
FACULTY_NAME = "Mühendislik Fakültesi"
UNIVERSITY_NAME = "XYZ Üniversitesi"

# Contact information
CONTACT_EMAIL = "mudek@university.edu.tr"
CONTACT_PHONE = "+90 XXX XXX XX XX"

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# Enable console output
CONSOLE_OUTPUT = True

# Enable file logging
FILE_LOGGING = True
