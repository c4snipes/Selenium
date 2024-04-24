import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
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
    
class AuthenticationLoginTest(unittest.TestCase):
    def setUp(self):
        chrome_service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=chrome_service)
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8080/accounts/login')
        login_username = "testuser"
        login_password = "password123"
        self.driver.find_element(By.ID, "username").send_keys(login_username)
        self.driver.find_element(By.ID, "password").send_keys(login_password)
        self.driver.find_element(By.ID, "loginButton").click()

        # Ensure we are redirected to the encryption page
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "encryptPage")),
            message="Did not redirect to encryption page"
        )

    def test_save_encrypted_text(self):
        input_text = "password123"  # Input text to be encrypted

        try:
            # Wait until the input field is visible and clickable
            password_input = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "passwordTextE")),
                message="Password input box not found."
            )
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "passwordTextE")),
                message="Password input box is not clickable."
            )

            # Clear any pre-existing text and type in the input
            password_input.clear()
            password_input.send_keys(input_text)

            # Click the encrypt button
            encrypt_button = self.driver.find_element(By.ID, "encryptButton")
            encrypt_button.click()

            # Wait for the encrypted text to appear and verify it
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.find_element(By.ID, "encryptedText").get_attribute("value") != "",
                message="Encrypted text is empty or unchanged."
            )

            # Print encrypted value for verification during debugging
            encrypted_value = self.driver.find_element(By.ID, "encryptedText").get_attribute("value")
            print(f"Encrypted value: {encrypted_value}")

            # Proceed to save
            save_button = self.driver.find_element(By.CSS_SELECTOR, ".save-btn")
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(save_button),
                message="Save button is not clickable."
            )
            save_button.click()

            # Handle any potential alerts
            WebDriverWait(self.driver, 10).until(EC.alert_is_present())
            alert = Alert(self.driver)
            alert.accept()

        except Exception as e:
            print(f"An error occurred: {e}")
            
    def test_save_encrypted_text(self):
        input_text = "password123"
        try:
            password_input = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "passwordTextE")),
                message="Password input box not found."
            )
            password_input.clear()
            password_input.send_keys(input_text)

            encrypt_button = self.driver.find_element(By.ID, "encryptButton")
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(encrypt_button),
                message="Encrypt button is not clickable."
            )
            encrypt_button.click()

            encrypted_value = WebDriverWait(self.driver, 20).until(
                lambda driver: driver.find_element(By.ID, "encryptedText").get_attribute("value"),
                message="Encrypted text is empty or unchanged."
            )

            save_button = self.driver.find_element(By.CSS_SELECTOR, ".save-btn")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(save_button),
                message="Save button is not clickable."
            )
            self.driver.execute_script("arguments[0].click();", save_button)

            WebDriverWait(self.driver, 10).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()

        except Exception as e:
            print(f"An error occurred: {e}")
            
    def test_decrypt_encrypted_text(self):
        # Navigate to the decryption page
        self.driver.get('http://127.0.0.1:8080/decrypt')

        # Input the encrypted text to be decrypted
        encrypted_input = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.ID, "encryptedTextD")),
            message="Encrypted text input box not found."
        )
        encrypted_input.send_keys("Z09qais1aSpGR0hGR0gwMTJJSktGRQ==")  # Replace with your encrypted text

        # Click the decrypt button
        decrypt_button = self.driver.find_element(By.ID, "decryptButton")
        decrypt_button.click()

        # Wait for the decrypted text to appear
        decrypted_text_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "decryptedText")),
            message="Decrypted text element not present."
        )
        decrypted_text = decrypted_text_element.get_attribute("value")

        print(f"Decrypted value: {decrypted_text}")  # Output decrypted text for verification
        # You can add an assertion here if you know the expected decrypted text


    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()