from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

class Assersion:
    def __init__(self, driver, assersion_type, expected_message):
        self.driver = driver
        self.assersion_type = assersion_type
        self.expected_message = expected_message

    def assert_result(self):
        if self.assersion_type == "popup":
            return self._assert_alert()
        elif self.assersion_type == "body":
            return self._assert_text_in_body()
        elif self.assersion_type == "url":
            return self._assert_url()
        else:
            raise ValueError(f"Nieznany typ asercji: {self.assersion_type}")

    def _assert_alert(self):

        alerts = self.driver.find_elements(By.CLASS_NAME, "alert")
        if not alerts:
            raise AssertionError("❌ Nie znaleziono elementu z klasą 'alert' (flash).")

        
        for alert in alerts:
            if self.expected_message in alert.text:
                print("✅ Flash zawiera oczekiwany tekst.")
                return True
            else:
                print(f"\tUzyskane:{alert.text}")
        raise AssertionError(f"❌ Flash nie zawiera oczekiwanego tekstu: {self.expected_message}")

    def _assert_text_in_body(self):
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        #print(f"==============body_text=============\n{body_text}\n==============body_text=============")
        assert self.expected_message in body_text, f"❌ Tekst '{self.expected_message}' nie został znaleziony w treści strony."
        print("✅ Tekst został znaleziony w treści strony.")
        return True

    def _assert_url(self):
        current_url = self.driver.current_url
        assert self.expected_message in current_url, f"❌ Adres URL '{current_url}' nie jest zgodny z oczekiwanym '{self.expected_message}'."
        print("✅ Adres URL jest zgodny z oczekiwanym.")
        return True


def test_registration(driver, email, username, password, comfirm_password, accept_terms, Asseresions):
    driver.get("http://127.0.0.1:5000/register") 

    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email_input_reg")))
    username_input = driver.find_element(By.NAME, "username_input_reg")
    password_input = driver.find_element(By.NAME, "password_input_reg")
    password_confirm_input = driver.find_element(By.NAME, "confirm_password_input_reg")
    checkbox =  driver.find_element(By.ID, "flexCheckDefault")

    registration_button = driver.find_element(By.XPATH, "//button[text()='Sign up']")
    
    # Wpisanie danych
    email_input.clear()
    username_input.clear()
    password_input.clear()
    password_confirm_input.clear()

    email_input.send_keys(email)
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_confirm_input.send_keys(comfirm_password)
    if(accept_terms):
        checkbox.click()

    registration_button.click()

    
    # Oczekiwanie na nową stronę
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    for Asseresion in Asseresions:
        Asseresion.assert_result()

def test_login(driver, email, password, Asseresions):
    driver.get("http://127.0.0.1:5000/login") 

    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email_input_login")))
    password_input = driver.find_element(By.NAME, "password_input_login")

    login_button = driver.find_element(By.XPATH, "//button[text()='Log in']")
    
    # Wpisanie danych
    email_input.clear()
    password_input.clear()

    email_input.send_keys(email)
    password_input.send_keys(password)
    login_button.click()
    

    # Oczekiwanie na nową stronę
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    for Asseresion in Asseresions:
        Asseresion.assert_result()