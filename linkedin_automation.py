"""
LinkedIn semi-automation module for MÜDEK Alumni Survey System.
Handles browser automation with human-in-the-loop for final actions.

IMPORTANT: This module is designed for semi-automation only.
The final SEND action is always left to manual user confirmation.
"""

import time
import random
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None

import config
from logger_utils import setup_logger

logger = setup_logger(__name__)


class LinkedInAutomation:
    """
    Semi-automated LinkedIn messaging system with human-in-the-loop design.
    
    This class handles:
    - Browser initialization with existing session support
    - Profile navigation
    - Message box population
    
    It does NOT:
    - Send messages automatically (requires manual confirmation)
    - Handle login (expects existing session)
    """
    
    def __init__(self, profile_path: Optional[str] = None):
        """
        Initialize the LinkedIn automation handler.
        
        Args:
            profile_path: Path to Chrome user data directory for session persistence
        """
        self.profile_path = profile_path or config.CHROME_PROFILE_PATH
        self.driver = None
        self.wait = None
        self.actions = None
        self._setup_browser()
    
    def _setup_browser(self):
        """Configures and initializes the Chrome browser."""
        options = Options()
        
        # Use existing Chrome profile if specified
        if self.profile_path:
            options.add_argument(f"user-data-dir={self.profile_path}")
            if config.CHROME_PROFILE_NAME:
                options.add_argument(f"profile-directory={config.CHROME_PROFILE_NAME}")
            logger.info(f"Using Chrome profile: {self.profile_path}")
        
        # Window size
        options.add_argument(f"window-size={config.BROWSER_WIDTH},{config.BROWSER_HEIGHT}")
        
        # Disable automation detection flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Additional options for stability
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # Headless mode (not recommended for LinkedIn)
        if config.HEADLESS_MODE:
            options.add_argument("--headless=new")
            logger.warning("Headless mode enabled - may trigger LinkedIn detection")
        
        try:
            if ChromeDriverManager:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            self.wait = WebDriverWait(self.driver, config.ELEMENT_WAIT_TIMEOUT)
            self.actions = ActionChains(self.driver)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
            
            logger.info("Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Adds a random delay to simulate human behavior."""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def _human_type(self, element, text: str, delay_range: Tuple[float, float] = (0.02, 0.08)):
        """
        Types text with human-like delays between keystrokes.
        
        Args:
            element: WebElement to type into
            text: Text to type
            delay_range: Min and max delay between keystrokes
        """
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
    
    def check_login_status(self) -> bool:
        """
        Checks if the user is logged into LinkedIn.
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            self._random_delay(2, 4)
            
            # Check for feed elements that only appear when logged in
            feed_indicators = [
                "//div[contains(@class, 'feed-shared-update')]",
                "//div[@data-test-id='nav-menu']",
                "//input[contains(@class, 'search-global')]"
            ]
            
            for indicator in feed_indicators:
                try:
                    self.driver.find_element(By.XPATH, indicator)
                    logger.info("LinkedIn login verified")
                    return True
                except NoSuchElementException:
                    continue
            
            logger.warning("LinkedIn login not detected")
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    def navigate_to_profile(self, linkedin_url: str) -> bool:
        """
        Navigates to a LinkedIn profile page.
        
        Args:
            linkedin_url: Full LinkedIn profile URL
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Navigating to profile: {linkedin_url}")
            self.driver.get(linkedin_url)
            self._random_delay(config.MEDIUM_DELAY, config.MEDIUM_DELAY + 2)
            
            # Verify we're on a profile page
            profile_indicators = [
                "//section[contains(@class, 'profile')]",
                "//div[contains(@class, 'pv-top-card')]",
                "//h1[contains(@class, 'text-heading-xlarge')]"
            ]
            
            for indicator in profile_indicators:
                try:
                    self.wait.until(EC.presence_of_element_located((By.XPATH, indicator)))
                    logger.debug("Profile page loaded successfully")
                    return True
                except TimeoutException:
                    continue
            
            logger.warning("Could not verify profile page loaded")
            return False
            
        except TimeoutException:
            logger.error(f"Timeout loading profile: {linkedin_url}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to profile: {e}")
            return False
    
    def open_message_dialog(self) -> bool:
        """
        Opens the messaging dialog for the current profile.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Multiple possible selectors for the Message button
            message_button_selectors = [
                "//button[contains(@aria-label, 'Message')]",
                "//button[contains(text(), 'Message')]",
                "//button[contains(text(), 'Mesaj')]",  # Turkish
                "//a[contains(@href, '/messaging/')]",
                "//button[contains(@class, 'message-anywhere-button')]"
            ]
            
            message_button = None
            for selector in message_button_selectors:
                try:
                    message_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not message_button:
                logger.warning("Message button not found - may need to connect first")
                return False
            
            # Scroll button into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                message_button
            )
            self._random_delay(config.SHORT_DELAY, config.SHORT_DELAY + 1)
            
            # Click the button
            try:
                message_button.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", message_button)
            
            self._random_delay(config.SHORT_DELAY, config.MEDIUM_DELAY)
            logger.debug("Message dialog opened")
            return True
            
        except Exception as e:
            logger.error(f"Error opening message dialog: {e}")
            return False
    
    def fill_message(self, message: str, use_human_typing: bool = True) -> bool:
        """
        Fills the message input with the provided text.
        
        Args:
            message: Message text to fill
            use_human_typing: If True, types with human-like delays
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the message input area
            message_box_selectors = [
                "//div[@role='textbox' and contains(@aria-label, 'message')]",
                "//div[@role='textbox' and contains(@aria-label, 'Write a message')]",
                "//div[@role='textbox' and contains(@aria-label, 'Mesaj yaz')]",  # Turkish
                "//div[contains(@class, 'msg-form__contenteditable')]",
                "//div[@contenteditable='true' and contains(@class, 'msg')]"
            ]
            
            message_box = None
            for selector in message_box_selectors:
                try:
                    message_box = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not message_box:
                logger.warning("Message box not found")
                return False
            
            # Click to focus
            message_box.click()
            self._random_delay(0.3, 0.7)
            
            # Clear any existing content
            message_box.send_keys(Keys.CONTROL + "a")
            message_box.send_keys(Keys.DELETE)
            self._random_delay(0.2, 0.5)
            
            # Type the message
            if use_human_typing:
                # For long messages, use faster typing
                delay_range = (0.01, 0.03) if len(message) > 200 else (0.02, 0.06)
                self._human_type(message_box, message, delay_range)
            else:
                message_box.send_keys(message)
            
            logger.info("Message filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error filling message: {e}")
            return False
    
    def prepare_message(self, linkedin_url: str, message: str) -> bool:
        """
        Complete workflow to prepare a message (navigate, open dialog, fill).
        Does NOT send - leaves that for manual action.
        
        Args:
            linkedin_url: LinkedIn profile URL
            message: Message text
            
        Returns:
            True if message is ready to send, False otherwise
        """
        # Step 1: Navigate to profile
        if not self.navigate_to_profile(linkedin_url):
            return False
        
        # Step 2: Open message dialog
        if not self.open_message_dialog():
            return False
        
        # Step 3: Fill the message
        if not self.fill_message(message):
            return False
        
        return True
    
    def wait_for_user_confirmation(self) -> str:
        """
        Pauses execution and waits for user to confirm action.
        
        Returns:
            User's response ('s' for sent, 'k' for skipped, 'q' for quit)
        """
        print("\n" + "="*60)
        print("✅ MESSAGE READY - AWAITING MANUAL ACTION")
        print("="*60)
        print("\nOptions:")
        print("  [S] - Message SENT (press after clicking Send)")
        print("  [K] - SKIP this profile")
        print("  [Q] - QUIT campaign")
        print("="*60)
        
        while True:
            response = input("\nYour action [S/K/Q]: ").strip().lower()
            if response in ['s', 'k', 'q']:
                return response
            print("Invalid option. Please enter S, K, or Q.")
    
    def close(self):
        """Closes the browser and cleans up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")


class LinkedInConnectionChecker:
    """
    Utility class to check connection status before messaging.
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
    
    def is_first_degree_connection(self) -> bool:
        """
        Checks if the current profile is a 1st-degree connection.
        
        Returns:
            True if 1st-degree connection, False otherwise
        """
        try:
            degree_selectors = [
                "//span[contains(@class, 'distance-badge') and contains(text(), '1st')]",
                "//span[contains(text(), '1st degree connection')]",
                "//span[contains(text(), '1. derece bağlantı')]"  # Turkish
            ]
            
            for selector in degree_selectors:
                try:
                    self.driver.find_element(By.XPATH, selector)
                    return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception:
            return False


# =============================================================================
# STANDALONE TESTING
# =============================================================================

if __name__ == "__main__":
    print("Testing LinkedIn Automation Module...")
    print("-" * 50)
    print("\n⚠️  This will open a browser window.")
    print("Make sure you're logged into LinkedIn in Chrome.\n")
    
    input("Press ENTER to continue...")
    
    try:
        automation = LinkedInAutomation()
        
        if automation.check_login_status():
            print("\n✅ Login verified!")
            
            test_url = input("\nEnter a LinkedIn profile URL to test: ").strip()
            if test_url:
                test_message = "This is a test message. [DELETE THIS]"
                
                if automation.prepare_message(test_url, test_message):
                    print("\n✅ Message prepared successfully!")
                    automation.wait_for_user_confirmation()
                else:
                    print("\n❌ Failed to prepare message")
        else:
            print("\n❌ Please log into LinkedIn first")
        
        automation.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
