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

def IntegrationTests(driver):
    

    print("Testy funkcjonalnośi strony")
    print("\nHiperłącza bez logowania:")
    links_text = ["My profile", "My games", "Ranking", "Statistics"]
    

    for i in range(2):
        driver.get("http://127.0.0.1:5000")
        link_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, links_text[i])))

        try:
            link_button.click()
            Assersion(driver, "popup", "You are not logged in").assert_result()
            Assersion(driver, "body", "Please log in").assert_result()
            Assersion(driver, "url", "http://127.0.0.1:5000/login").assert_result()
            print(f"✔ Test {i}.0:")

            return_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Sudoku-Sweeper")))
            try:    
                return_button.click()
                Assersion(driver, "body", "Sudoku is a logic-based puzzle game where the goal is to fill a 9x9 grid with numbers from 1 to 9.").assert_result()
                Assersion(driver, "url", "http://127.0.0.1:5000").assert_result()
                print(f"✔ Test {i}.1:")
            except AssertionError as e:
                pass_all_login = False
                print(f"✖ Test {i}.1:")
                print(f"Prawidłowe hiperłącze:\n{e}")

        except AssertionError as e:
            pass_all_login = False
            print(f"✖ Test {i}.0:")
            print(f"Prawidłowe hiperłącze:\n{e}")
        print("\n")

    print("\nHiperłącza po zalogowaniu logowania:")
    test_registration(driver, "alan.ma@kota.co", "Przemek", "Makota12#", "Makota12#", True, [])
    test_login(driver, "alan.ma@kota.co", "Makota12#", [])

    addresses = ["http://127.0.0.1:5000/user_panel", "http://127.0.0.1:5000/my_games","http://127.0.0.1:5000/ranking", "http://127.0.0.1:5000/statistics"]
    text_on_subpages = [
        "Username:",
        "My games",
        "Ranking",
        "Statistics"]

    for i in range(4):
        driver.get("http://127.0.0.1:5000")
        link_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, links_text[i])))

        try:
            link_button.click()
            Assersion(driver, "url", addresses[i]).assert_result()
            Assersion(driver, "body",text_on_subpages[i]).assert_result()
            print(f"✔ Test {2 + i}.0:")

            return_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Sudoku-Sweeper")))
            try:    
                return_button.click()
                Assersion(driver, "url", "http://127.0.0.1:5000").assert_result()
                Assersion(driver, "body", "Sudoku is a logic-based puzzle game where the goal is to fill a 9x9 grid with numbers from 1 to 9.").assert_result()
                print(f"✔ Test {2 + i}.1:")
            except AssertionError as e:
                pass_all_login = False
                print(f"✖ Test {2 + i}.1:")
                print(f"Prawidłowe hiperłącze:\n{e}")

        except AssertionError as e:
            pass_all_login = False
            print(f"✖ Test {2 + i}.0:")
            print(f"Prawidłowe hiperłącze:\n{e}")
        print("\n")


    print("\nTesty tworzenia nowej gry:")
    #wyszukanie przycisków z wyborem trudności gry:
    buttons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".btn-lg")))

    for i in range(len(buttons)):
        # Ponowne pobranie listy przycisków przed kliknięciem
        buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".btn-lg")))
        
        try:
            buttons[i].click()
            Assersion(driver, "body", "Time:").assert_result()
            
            return_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Sudoku-Sweeper")))
            return_button.click()

            print(f"✔ Test {8 + i}:")
        except AssertionError as e:
            print(f"✖ Test {8 + i}:")
            print(f"Przycisk nie przenosi na stronę gry:\n{e}")
    print("\n")
    