"""
LinkedIn Automation Engine for MÜDEK Alumni Survey.
"""
import time
import random
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
import config
from logger_utils import setup_logger

logger = setup_logger(__name__)

# --- DİNAMİK SEÇİCİLER (LinkedIn UI değişikliklerine karşı) ---
SELECTORS = {
    "message_button": [
        "//button[contains(@aria-label, 'Message')]",
        "//button//span[text()='Message']/..",
        "//button//span[text()='Mesaj']/..",
        "//button[contains(@class, 'message-anywhere-button')]",
        "//div[contains(@class, 'pv-top-card')]//button[contains(., 'Message')]"
    ],
    "connect_button": [
        "//button[contains(@aria-label, 'Connect')]",
        "//button//span[text()='Connect']/..",
        "//button//span[text()='Bağlan']/..",
        "//button[contains(@aria-label, 'Invite')]"
    ],
    "message_textbox": [
        "div.msg-form__contenteditable[role='textbox']",
        "div[role='textbox'][contenteditable='true']",
        "div.msg-form__msg-content-container div[role='textbox']"
    ],
    "global_nav": [
        "//nav[@id='global-nav']",
        "//header[contains(@class, 'global-nav')]"
    ]
}


class LinkedInAutomation:
    def __init__(self):
        self.profile_path = config.CHROME_PROFILE_PATH
        self.driver = None
        self.wait = None
        self._setup_browser()
    
    def _setup_browser(self):
        """Tarayıcıyı bot tespitine karşı korumalı şekilde başlatır."""
        options = Options()
        
        if self.profile_path:
            options.add_argument(f"user-data-dir={self.profile_path}")
            if config.CHROME_PROFILE_NAME:
                options.add_argument(f"profile-directory={config.CHROME_PROFILE_NAME}")
        
        # Bot tespiti önleme ayarları
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument(f"--window-size={config.BROWSER_WIDTH},{config.BROWSER_HEIGHT}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        if config.HEADLESS_MODE:
            options.add_argument("--headless=new")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                """
            })
            self.wait = WebDriverWait(self.driver, config.ELEMENT_WAIT_TIMEOUT)
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """İnsan benzeri rastgele bekleme."""
        time.sleep(random.uniform(min_sec, max_sec))

    def _find_element_by_selectors(self, selectors: list, by_type: str = "xpath") -> Optional:
        """Birden fazla seçici deneyerek element bulur."""
        for selector in selectors:
            try:
                if by_type == "xpath":
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    logger.debug(f"Found element with selector: {selector[:50]}...")
                    return elements[0]
            except Exception:
                continue
        return None

    def check_login_status(self) -> bool:
        """LinkedIn oturum durumunu kontrol eder."""
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            self._random_delay(2, 4)
            
            # Global nav kontrolü
            nav = self._find_element_by_selectors(SELECTORS["global_nav"])
            if nav:
                logger.info("LinkedIn session verified via global-nav")
                return True
            
            # URL kontrolü (login sayfasına yönlendirildiyse)
            current_url = self.driver.current_url
            if "login" in current_url or "checkpoint" in current_url:
                logger.warning("Redirected to login page")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Login check failed: {e}")
            return False

    def prepare_message(self, linkedin_url: str, message: str) -> str:
        """
        Profili açar ve mesaj kutusunu hazırlar.
        
        Returns:
            'ready': Mesaj yazıldı, gönderime hazır
            'connection_needed': 1. derece bağlantı değil
            'error': Beklenmeyen hata
        """
        try:
            logger.info(f"Navigating to: {linkedin_url}")
            self.driver.get(linkedin_url)
            self._random_delay(3, 5)
            
            # Sayfa yüklenme kontrolü
            try:
                self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//main[contains(@class, 'scaffold-layout__main')]")
                ))
            except TimeoutException:
                logger.warning("Page load timeout, continuing anyway...")

            # 1. MESAJ BUTONUNU ARA
            message_btn = self._find_element_by_selectors(SELECTORS["message_button"])
            
            if not message_btn:
                # Mesaj butonu yoksa bağlantı durumunu kontrol et
                connect_btn = self._find_element_by_selectors(SELECTORS["connect_button"])
                if connect_btn:
                    logger.warning("Connection required - not 1st degree connection")
                    return 'connection_needed'
                
                # "More" menüsünde olabilir
                try:
                    more_btn = self.driver.find_element(
                        By.XPATH, "//button[contains(@aria-label, 'More actions')]"
                    )
                    more_btn.click()
                    self._random_delay(1, 2)
                    message_btn = self._find_element_by_selectors(SELECTORS["message_button"])
                except:
                    pass
                
                if not message_btn:
                    logger.error("Message button not found anywhere")
                    return 'error'

            # 2. BUTONA TIKLA
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", message_btn)
                self._random_delay(0.5, 1)
                message_btn.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", message_btn)
            
            self._random_delay(2, 3)

            # 3. MESAJ KUTUSUNA YAZ
            text_box = None
            for selector in SELECTORS["message_textbox"]:
                try:
                    text_box = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if text_box:
                        break
                except:
                    continue
            
            if not text_box:
                logger.error("Message textbox not found")
                return 'error'
            
            # Mevcut içeriği temizle
            text_box.click()
            self._random_delay(0.3, 0.5)
            
            # İnsan benzeri yazma simülasyonu
            for char in message:
                text_box.send_keys(char)
                time.sleep(random.uniform(0.02, 0.08))
            
            logger.info("Message prepared successfully")
            return 'ready'

        except StaleElementReferenceException:
            logger.error("Element became stale - page may have reloaded")
            return 'error'
        except Exception as e:
            logger.error(f"Error preparing message: {e}")
            return 'error'

    def wait_for_user_confirmation(self) -> str:
        """Kullanıcıdan manuel onay bekler."""
        print("\n" + "=" * 55)
        print("✅ MESAJ HAZIR - LÜTFEN MANUEL KONTROL EDİN")
        print("-" * 55)
        print("  [S] -> Gönderdim (Sent)")
        print("  [K] -> Pas Geç (Skip)")
        print("  [E] -> Düzenle & Gönder (Edit)")
        print("  [Q] -> Çıkış (Quit)")
        print("=" * 55)
        
        while True:
            choice = input("Seçiminiz [S/K/E/Q]: ").strip().lower()
            if choice in ['s', 'k', 'e', 'q']:
                if choice == 'e':
                    input("Düzenleme yaptıktan sonra Enter'a basın...")
                    return 's'  # Düzenleme sonrası gönderildi say
                return choice
            print("⚠️ Geçersiz seçim. Lütfen S, K, E veya Q girin.")

    def close(self):
        """Tarayıcıyı güvenli şekilde kapatır."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
