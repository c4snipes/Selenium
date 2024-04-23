import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import random

def generate_valid_username():
    """Generate a valid-length username, between 5 and 10 characters."""
    prefix = 'usr'
    number_length = random.randint(2, 7)
    numeric_suffix = random.randint(10**(number_length-1), 10**number_length-1)
    return prefix + str(numeric_suffix)

def generate_too_short_username():
    """Generate a username that is too short."""
    return 'usr'[:random.randint(1, 4)]  # Results in a username length of 1 to 3 characters

def generate_too_long_username():
    """Generate a username that is too long."""
    prefix = 'usr'
    number_length = random.randint(8, 10)
    numeric_suffix = random.randint(10**(number_length-1), 10**number_length-1)
    return prefix + str(numeric_suffix)
class RegistrationTest(unittest.TestCase):
    def setUp(self):
        """Sets up the test environment before each test."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.driver.get('http://127.0.0.1:8080/accounts/register')

    def perform_registration(self, username, expected_error=None):
        """Perform registration and check for expected errors."""
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "username")))
        username_field = self.driver.find_element(By.ID, "username")
        password_field = self.driver.find_element(By.ID, "password")
        token_field = self.driver.find_element(By.ID, "token")
        
        username_field.send_keys(username)
        password_field.send_keys("Test1234!")
        token_field.send_keys("1234567890")
        
        # Scroll to the button and click using JavaScript if necessary
        submit_button = self.driver.find_element(By.ID, "register_button")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        self.driver.execute_script("arguments[0].click();", submit_button)

        if expected_error:
            error_message = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger")),
                message="Expected error message not found."
            )
            self.assertIn(expected_error, error_message.text)
        else:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-success")),
                message="Registration success message not found."
            )

    def test_valid_username_registration(self):
        """Tests valid username registration."""
        self.perform_registration(generate_valid_username())

    def test_too_short_username_registration(self):
        """Tests registration with a too short username."""
        self.perform_registration(generate_too_short_username(), expected_error="Username must be between 5 and 10 characters long.")

    def test_too_long_username_registration(self):
        """Tests registration with a too long username."""
        self.perform_registration(generate_too_long_username(), expected_error="Username must be between 5 and 10 characters long.")
    def perform_registration_with_password(self, password, expected_error=None):
        """Perform registration and check for specific password related errors."""
        username = generate_valid_username()
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "token").send_keys("validToken1234567890")

        submit_button = self.driver.find_element(By.ID, "register_button")
        self.driver.execute_script("arguments[0].click();", submit_button)

        if expected_error:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger")),
                message="Expected error message not found."
            )
            error_message = self.driver.find_element(By.CSS_SELECTOR, ".alert-danger").text
            self.assertIn(expected_error, error_message)
        else:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-success")),
                message="Registration success message not found."
            )

    def perform_registration_with_passkey(self, passkey, expected_error=None):
        """Perform registration and check for specific passkey related errors."""
        username = generate_valid_username()
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys("Password123!")
        self.driver.find_element(By.ID, "token").send_keys(passkey)

        submit_button = self.driver.find_element(By.ID, "register_button")
        self.driver.execute_script("arguments[0].click();", submit_button)

        if expected_error:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger")),
                message="Expected error message not found."
            )
            error_message = self.driver.find_element(By.CSS_SELECTOR, ".alert-danger").text
            self.assertIn(expected_error, error_message)
        else:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-success")),
                message="Registration success message not found."
            )

    def test_password_too_short(self):
        """Test with a password that is too short."""
        self.perform_registration_with_password("123", expected_error="Password must be between 8 and 20 characters long.")

    def test_password_too_long(self):
        """Test with a password that is too long."""
        self.perform_registration_with_password("123456789012345678901234567890", expected_error="Password must be between 8 and 20 characters long.")

    def test_passkey_too_short(self):
        """Test with a passkey that is too short."""
        self.perform_registration_with_passkey("12346", expected_error="Passkey must be between 10 and 30 characters long.")

    def test_passkey_too_long(self):
        """Test with a passkey that is too long."""
        self.perform_registration_with_passkey("1234567890123456789012345678901234567890", expected_error="Passkey must be between 10 and 30 characters long.")

    def perform_multi_error_registration(self, username, password, passkey, expected_errors):
        """Perform registration with multiple fields to trigger various validation errors."""
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "token").clear()
        self.driver.find_element(By.ID, "token").send_keys(passkey)

        submit_button = self.driver.find_element(By.ID, "register_button")
        # Use JavaScript to click to avoid ElementClickInterceptedException
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Collect all visible error messages
        WebDriverWait(self.driver, 20).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".alert-danger")))
        error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger")
        found_errors = [element.text for element in error_elements]

        # Assert each expected error is displayed
        for expected_error in expected_errors:
            with self.subTest(error=expected_error):
                self.assertIn(expected_error, found_errors, f"Expected error '{expected_error}' not found in {found_errors}")

    def test_multiple_errors(self):
        """Test form submission with multiple simultaneous validation errors."""
        self.perform_multi_error_registration(
            username=generate_too_short_username(),  # Too short
            password="123",  # Too short
            passkey="123456789",  # Too short
            expected_errors=[
                "Username must be between 5 and 10 characters long.",
                "Password must be between 8 and 20 characters long.",
                "Passkey must be between 10 and 30 characters long."
            ]
        )
    def tearDown(self):
        """Tears down the test environment after tests."""
        self.driver.quit()
    
class LoginTest(unittest.TestCase):
    def setUp(self):
        """Sets up the test environment before each test."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.driver.get("http://127.0.0.1:8080/accounts/login")  # Update this URL to your application's login page

    def test_login(self):
        """Perform login using provided credentials."""
        username = self.driver.find_element(By.ID, "username").send_keys("testuser")
        password = self.driver.find_element(By.ID, "password").send_keys("password123")
        login_button = self.driver.find_element(By.ID, "loginButton")  # Updated to match the ID in your HTML
        
        # Use JavaScript to click to avoid ElementClickInterceptedException
        self.driver.execute_script("arguments[0].click();", login_button)

    def tearDown(self):
        """Tears down the test environment after tests."""
        self.driver.quit()
        
class EncryptionTest(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()), options=chrome_options)
        self.driver.get('http://127.0.0.1:8080/accounts/login')  # Update URL as necessary

        # Login to the application
        username = "testuser"
        password = "password123"
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "loginButton").click()

        # Wait for the login success alert to confirm login
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")),
            message="Login failed or login success message not found."
        )


    def test_save_encrypted_text(self):
        """Test the functionality of saving encrypted text."""
        # Enter some text to be encrypted
        input_text = "Test Encryption Text"
        self.driver.find_element(By.ID, "passwordTextE").send_keys(input_text)

        # Click the save button
        self.driver.find_element(By.CSS_SELECTOR, ".save-btn").click()

        # Verify that the encrypted text was saved correctly
        saved_text = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#encryptedText")),
            message="Encrypted text not found."
        )
        self.assertEqual(saved_text.get_attribute('value'), input_text, "Encrypted text did not match input.")

    def tearDown(self):
        """Closes the browser window after the tests are completed."""
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()