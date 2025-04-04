from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

from utils.Assersions import Assersion

options = Options()
options.headless = True
gecko_driver_path = GeckoDriverManager().install()
service = Service(gecko_driver_path)
driver = webdriver.Firefox(service=service, options=options)


def IntegrationTests():
    driver.get("http://127.0.0.1:5000")
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email_input_reg"))
    )