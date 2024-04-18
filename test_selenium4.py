import random
import string
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

def generate_username(prefix, min_length=5, max_length=9):
    """Generate a random username with the given prefix, having a length between min_length and max_length."""
    if min_length < len(prefix):
        raise ValueError("Minimum length must be greater than the length of the prefix.")
    if max_length <= len(prefix):
        raise ValueError("Maximum length must be greater than the prefix length for additional characters.")

    # Generate a string of random characters within specified length bounds
    random_part_length = random.randint(min_length - len(prefix), max_length - len(prefix))
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random_part_length))
    return prefix + random_part


class RegistrationTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        chrome_service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=chrome_service)
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8080/accounts/register')

    def safe_click(self, by, identifier):
        """Attempt to click on an element using JavaScript if standard click fails."""
        attempts = 0
        while attempts < 3:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((by, identifier))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                self.driver.execute_script("arguments[0].click();", element)
                return
            except Exception as e:
                print(f"Attempt {attempts+1}: {e}")
                time.sleep(2)
                if "intercepted" in str(e):
                    attempts += 1
                    continue
                raise
        raise Exception(f"Failed to click on the element identified by {identifier} after several attempts.")
    def check_for_alert(self, alert_class, expected_text):
        """Check for an alert with the given class and text."""
        try:
            alert = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, alert_class))
            )
            return expected_text in alert.text
        except TimeoutException:
            return False
    def test_valid_registration(self):
        """Ensure that valid registration is processed correctly with dynamically generated usernames."""
        try:
            username = generate_username("usr", 5, 9)
            print(f"Trying to register with username: {username}")
            
            self.driver.find_element(By.ID, "username").clear()
            self.driver.find_element(By.ID, "username").send_keys(username)
            self.driver.find_element(By.ID, "password").send_keys("validPass123!")
            self.driver.find_element(By.ID, "token").send_keys("token1234567890")
            self.safe_click(By.ID, "register_button")
            
            # General alert check
            alert = WebDriverWait(self.driver, 25).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert"))
            )
            self.assertIn("successful", alert.text.lower())  # Checking for 'successful' in any alert

        except Exception as e:
            self.driver.save_screenshot("test_valid_registration_failure.png")
            raise AssertionError(f"Test failed: {e}")
        
        

    def tearDown(self):
        """Tear down the test environment after each test."""
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
