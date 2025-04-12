from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

from utils.Utils import *

def TestAdminPanel(driver):
    pass_all_tests = True
    test_registration(driver, "testuser1@example.ai", "TestUser_forADM1", "TestPassword123!", "TestPassword123!", True, [])
    test_registration(driver, "testuser2@example.ai", "TestUser_forADM2", "TestPassword123!", "TestPassword123!", True, [])
    test_registration(driver, "testuser3@example.ai", "TestUser_forADM3", "TestPassword123!", "TestPassword123!", True, [])
    test_login(driver, "testadmin@gmail.com", "admin123", [])

    print("-------------------Testy admina-------------------")

    try:
        panel_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Admin Panel")))
        panel_button.click()

        Assersion(driver, "url", "http://127.0.0.1:5000/admin_panel").assert_result()
        print("✔ Test 1: Admin panel opened successfully")

        body_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        ).text

        expected_usernames = ["testuser", "TestUser_forADM1", "TestUser_forADM2", "TestUser_forADM3"]
        for username in expected_usernames:
            assert username in body_text, f"{username} not found in admin panel"

        print("✔ Test 2: Usernames are visible in admin panel")

    except AssertionError as e:
        pass_all_tests = False
        print("✖ Test failed:")
        print(f"{e}")