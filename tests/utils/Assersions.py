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
        assert self.expected_message in body_text, f"❌ Tekst '{self.expected_message}' nie został znaleziony w treści strony."
        print("✅ Tekst został znaleziony w treści strony.")
        return True

    def _assert_url(self):
        current_url = self.driver.current_url
        assert self.expected_message in current_url, f"❌ Adres URL '{current_url}' nie jest zgodny z oczekiwanym '{self.expected_message}'."
        print("✅ Adres URL jest zgodny z oczekiwanym.")
        return True