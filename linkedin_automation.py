"""
LinkedIn Automation - AGGRESSIVE CLEANUP & NAME MATCHING
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import config
from logger_utils import setup_logger

logger = setup_logger(__name__)

# --- SELECTORLAR ---
SELECTORS = {
    "profile_name_h1": [
        "//h1[contains(@class, 'text-heading-xlarge')]",
        "//div[contains(@class, 'ph5')]//h1",
        "//h1"
    ],
    "primary_message_button": [
        "//main//button[contains(@class, 'message-anywhere-button')]",
        "//span[text()='Mesaj gönder']",
        "//span[text()='Mesaj']",
        "//button[contains(., 'Mesaj')]"
    ],
    "popup_close_buttons": [
        "//button[@aria-label='Dismiss']",
        "//button[@aria-label='Kapat']",
        "//button[contains(@class, 'artdeco-modal__dismiss')]",
        "//button[@aria-label='Close']",
        "//svg[@data-test-icon='close-medium']/ancestor::button"
    ],
    # Sohbet Kapatma (Çoklu Seçenek)
    "chat_close_buttons": [
        # Standart kapatma butonu
        "//button[contains(@class, 'msg-overlay-bubble-header__control--close-btn')]",
        # İkon üzerinden bulma
        "//svg[@data-test-icon='close-small']/ancestor::button",
        # Header içindeki son buton
        "//header[contains(@class, 'msg-overlay-bubble-header')]//button[last()]"
    ],
    "message_textbox": [
        "div.msg-form__contenteditable[role='textbox']",
        "div[role='textbox']"
    ],
    "send_button": [
        "//button[@type='submit']",
        "//button[contains(@class, 'msg-form__send-button')]"
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
        self.wait = WebDriverWait(self.driver, 8)

    def check_login_status(self):
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            return "login" not in self.driver.current_url
        except: return False

    def safe_click(self, element):
        """Elemente tıklamayı garantiye alır."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
        except:
            try:
                self.driver.execute_script("arguments[0].click();", element)
            except: pass

    def nuke_all_chats(self):
        """
        Ekranda ne kadar sohbet penceresi varsa hepsini kapatır.
        Bunu 'While' döngüsü ile hiç buton kalmayana kadar yapar.
        """
        logger.info("🧹 Temizlik başlıyor: Tüm sohbetler kapatılıyor...")
        max_attempts = 5 # Sonsuz döngüye girmesin
        for _ in range(max_attempts):
            found_any = False
            for xpath in SELECTORS["chat_close_buttons"]:
                try:
                    buttons = self.driver.find_elements(By.XPATH, xpath)
                    for btn in buttons:
                        if btn.is_displayed():
                            self.safe_click(btn)
                            found_any = True
                            time.sleep(0.3) # Animasyon bekle
                except: pass
            
            if not found_any:
                break # Hiç buton kalmadıysa döngüyü kır
        
        time.sleep(1) # Emin olmak için bekle

    def handle_popups(self):
        try:
            for xpath in SELECTORS["popup_close_buttons"]:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    if el.is_displayed():
                        self.safe_click(el)
                        time.sleep(0.5)
        except: pass

    def get_first_name(self):
        """Profildeki H1 başlığından ilk ismi alır."""
        try:
            for xpath in SELECTORS["profile_name_h1"]:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    full_name = elements[0].text.strip()
                    return full_name.split()[0] # "Yasin"
            return None
        except: return None

    def send_message_fast(self, url, message):
        try:
            # ADIM 0: ÖNCEKİ PİSLİKLERİ TEMİZLE
            self.nuke_all_chats()

            logger.info(f"Profil açılıyor: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # ADIM 0.5: SAYFA YÜKLENİNCE TEKRAR TEMİZLE (Otomatik açılan varsa)
            self.handle_popups()
            self.nuke_all_chats()

            # Profil ismini al (Doğrulama için)
            target_name = self.get_first_name()
            logger.info(f"Hedef Kişi: {target_name}")

            # ADIM 1: MESAJ BUTONUNA TIKLA
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
                logger.info("✅ Profildeki Mesaj butonuna tıklanıyor...")
                self.safe_click(msg_btn)
                time.sleep(3) # Pencerenin açılmasını bekle
            else:
                logger.error("❌ Mesaj butonu bulunamadı.")
                return 'error'

            # ADIM 2: DOĞRU KUTUYU BUL (İSİM EŞLEŞTİRME)
            # Sadece başlığında hedefin ismi geçen kutuyu arıyoruz
            textbox = None
            try:
                if target_name:
                    # Başlığında isim geçen pencerenin içindeki textbox
                    target_xpath = f"//div[contains(@class, 'msg-overlay-conversation-bubble') and .//h2[contains(., '{target_name}')]]//div[@role='textbox']"
                    textbox = self.driver.find_element(By.XPATH, target_xpath)
                    logger.info(f"🎯 {target_name} için doğru kutu bulundu.")
                else:
                    # İsim alamazsak aktif elementi dene
                    textbox = self.driver.switch_to.active_element
            except:
                # Bulamazsa genel arama yap ve sonuncuyu (en yeniyi) al
                try:
                    all_boxes = self.driver.find_elements(By.CSS_SELECTOR, "div[role='textbox']")
                    visible_boxes = [b for b in all_boxes if b.is_displayed()]
                    if visible_boxes:
                        textbox = visible_boxes[0] # LinkedIn yeni pencereyi genelde ilk sıraya (sola) koyar
                        logger.warning("⚠️ İsimle bulunamadı, ilk sıradaki kutu seçildi.")
                except: pass

            if not textbox:
                logger.error("❌ Sohbet kutusu bulunamadı/açılmadı.")
                return 'error'

            # Kutuya tıkla
            self.safe_click(textbox)
            time.sleep(0.5)

            # ADIM 3: YAZ VE TETİKLE
            logger.info("Mesaj yazılıyor...")
            textbox.clear()
            textbox.send_keys(message)
            time.sleep(0.5)
            # Tetikleyici (Trigger)
            textbox.send_keys(" ") 
            textbox.send_keys(Keys.BACKSPACE)
            time.sleep(1)

            # ADIM 4: GÖNDER (FORM İÇİ BUTON)
            # Textbox'ın bağlı olduğu formu bul, onun butonuna bas
            try:
                parent_form = textbox.find_element(By.XPATH, "./ancestor::form")
                send_btn = parent_form.find_element(By.XPATH, ".//button[@type='submit']")
                
                if send_btn and send_btn.is_enabled():
                    logger.info("📤 Gönderiliyor...")
                    self.safe_click(send_btn)
                    time.sleep(2)
                    
                    # İŞLEM BİTİNCE KAPAT (Temizlik)
                    self.nuke_all_chats()
                    return 'sent'
                else:
                    logger.error("❌ Gönder butonu aktif değil.")
                    return 'error'
            except:
                logger.error("❌ Form butonu bulunamadı.")
                return 'error'

        except Exception as e:
            logger.error(f"Hata: {e}")
            return 'error'

    def close(self):
        if self.driver: self.driver.quit()