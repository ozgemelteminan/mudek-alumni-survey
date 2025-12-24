import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import config
from logger_utils import setup_logger

logger = setup_logger(__name__)

# --- SELECTORLAR ---
SELECTORS = {
    # 1. Ana Mavi Buton
    "primary_message_button": [
        "//span[text()='Mesaj gönder']",
        "//button[contains(., 'Mesaj gönder')]",
        "//span[text()='Mesaj']",
        "//button[contains(@class, 'message-anywhere-button')]",
        "//div[contains(@class, 'pv-top-card')]//button"
    ],
    # 2. Popup Kapatıcılar
    "popup_close_buttons": [
        "//button[@aria-label='Dismiss']",
        "//button[@aria-label='Kapat']",
        "//button[contains(@class, 'artdeco-modal__dismiss')]",
        "//button[@aria-label='Close']",
        "//svg[@data-test-icon='close-medium']/ancestor::button"
    ],
    # 3. Daha Fazla Menüsü
    "more_button": [
        "//button[contains(@aria-label, 'Daha Fazla')]",
        "//button[contains(@aria-label, 'More actions')]",
        "//span[text()='Daha Fazla']"
    ],
    "menu_message_option": [
        "//div[contains(@class, 'artdeco-dropdown__content')]//span[contains(text(), 'Mesaj gönder')]",
        "//div[contains(@class, 'artdeco-dropdown__content')]//div[contains(text(), 'Mesaj')]"
    ],
    # 4. Sohbet Elemanları
    "message_textbox": [
        "div.msg-form__contenteditable[role='textbox']",
        "div[role='textbox']"
    ],
    "send_button": [
        "//button[@type='submit' and not(@disabled)]", # Sadece aktif butonlar
        "//button[contains(@class, 'msg-form__send-button')]",
        "//button[text()='Gönder']"
    ],
    "close_chat": [
        "//button[contains(@class, 'msg-overlay-bubble-header__control--close-btn')]"
    ]
}

class LinkedInAutomation:
    def __init__(self):
        self.profile_path = config.CHROME_PROFILE_PATH
        self._setup_browser()
    
    def _setup_browser(self):
        options = Options()
        if self.profile_path:
            options.add_argument(f"user-data-dir={self.profile_path}")
            if config.CHROME_PROFILE_NAME:
                options.add_argument(f"profile-directory={config.CHROME_PROFILE_NAME}")
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--remote-debugging-port=9223") 
        options.add_argument(f"--window-size={config.BROWSER_WIDTH},{config.BROWSER_HEIGHT}")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def check_login_status(self):
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            return "login" not in self.driver.current_url
        except: return False

    def force_click(self, element):
        try:
            self.driver.execute_script("arguments[0].click();", element)
        except:
            element.click()

    def handle_popups(self):
        try:
            for xpath in SELECTORS["popup_close_buttons"]:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    if el.is_displayed():
                        logger.info("🧹 Popup temizleniyor...")
                        self.force_click(el)
                        time.sleep(1)
        except: pass

    def send_message_fast(self, url, message):
        try:
            logger.info(f"Profil açılıyor: {url}")
            self.driver.get(url)
            time.sleep(4) 
            self.handle_popups()

            # --- ADIM 1: BUTONA TIKLA ---
            msg_btn = None
            for xpath in SELECTORS["primary_message_button"]:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for el in elements:
                        if el.is_displayed():
                            msg_btn = el
                            break
                    if msg_btn: break
                except: continue
            
            if msg_btn:
                logger.info(f"✅ Buton bulundu, tıklanıyor...")
                self.force_click(msg_btn)
                time.sleep(2)
            else:
                logger.error("❌ Mesaj butonu bulunamadı.")
                return 'error'

            # --- ADIM 2: SOHBET KUTUSU ---
            textbox = None
            try:
                textbox = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["message_textbox"][0])))
            except:
                self.handle_popups() # popup kontrolü
                try:
                    self.force_click(msg_btn) # Tekrar dene
                    time.sleep(2)
                    textbox = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["message_textbox"][0])))
                except:
                    logger.error("❌ Sohbet kutusu açılmadı.")
                    return 'error'

            # --- ADIM 3: YAZ VE GÖNDER ---
            logger.info("Mesaj yazılıyor...")
            textbox.clear()
            textbox.send_keys(message)
            time.sleep(1) 

            # Gönder butonunu bul
            send_btn = None
            for xpath in SELECTORS["send_button"]:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for btn in elements:
                        # Hem görünür hem de aktif (disabled değil) olmalı
                        if btn.is_displayed() and btn.is_enabled():
                            send_btn = btn
                            break
                    if send_btn: break
                except: continue
            
            if send_btn:
                logger.info("📤 Gönder butonuna basılıyor...")
                self.force_click(send_btn)
                time.sleep(2)
                
                # Sohbeti kapat
                try:
                    close = self.driver.find_element(By.XPATH, SELECTORS["close_chat"][0])
                    self.force_click(close)
                except: pass
                
                return 'sent'
            else:
                logger.error("❌ Gönder butonu aktif olmadı (Gri kaldı).")
                return 'error'

        except Exception as e:
            logger.error(f"Beklenmeyen Hata: {e}")
            return 'error'

    def close(self):
        if self.driver: self.driver.quit()