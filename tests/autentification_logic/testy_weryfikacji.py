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

def TestUserWalidation(driver):
    pass_all_registration = True
    created_test_user = False

    print("-------------------Testy rejestracji-------------------")

    #Prawidłowa rejestracja
    
    try:
        test_registration(driver, "testuser@example.co", "TestUser", "TestPassword123#", "TestPassword123#", True, 
        [Assersion(driver, "popup", "Register successed. You can log in."),
         Assersion(driver, "body", "Please log in"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])

        created_test_user = True
        print("✔ Test 1:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 1:")
        print(f"Sprawdzenie prawidłowej rejestracji:\n{e}")
    print("\n")

    #Podwójna rejestracja tego samego użytkownika
    try:
        test_registration(driver, "testuser@example.co", "TestUser", "TestPassword123#", "TestPassword123#", True, 
        [Assersion(driver, "popup", "Email already exists"),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 2:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 2:")
        print(f"Sprawdzenie podwójnej rejestracji:\n{e}")
    print("\n")

    #Sprawdzenie niezaakceptowanego regulaminu
    try:
        test_registration(driver, "testuser1@example.co", "TestUser1", "TestPassword123#", "TestPassword123#", False, 
        [Assersion(driver, "popup", "You have to accept the terms and conditions"),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 3:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 3:")
        print(f"Sprawdzenie braku akceptacji polityki prywatności:\n{e}")
    print("\n")

    #Pusty adres e-mail
    try:
        test_registration(driver, "", "TestUser2", "TestPassword123#", "TestPassword123#", True, 
        [Assersion(driver, "popup", "Please enter Your email."),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 4:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 4:")
        print(f"Sprawdzenie poprawności maila(pusty):\n{e}")
    print("\n")

    # Bledny e-mail
    try:
        test_registration(driver, "alan", "TestUser3", "TestPassword123#", "TestPassword123#", True, 
        [#Assersion(driver, "popup", " Wrong e-mail! "), #powoduje błędy po stronie Selenium
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/register")])
        print("✔ Test 5:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 5:")
        print(f"Sprawdzenie poprawności maila(zły format):\n{e}")
    print("\n")

    #Pusta nazwa użytkownika
    try:
        test_registration(driver, "testuser4@example.co", "", "TestPassword123#", "TestPassword123#", True, 
        [Assersion(driver, "popup", "Please enter a username."),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 6:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 6:")
        print(f"Brak nazwy urzytkownika:\n{e}")
    print("\n")

    #Puste hasło
    try:
        test_registration(driver, "testuser5@example.co", "TestUser5", "", "", True, 
        [Assersion(driver, "popup", "Please enter a password."),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 7:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 7:")
        print(f"Sprawdzenie poprawności hasła (puste hasło):\n{e}")
    print("\n")

    try:
        test_registration(driver, "testuser6@example.co", "TestUser6", "               ", "               ", True, 
        [Assersion(driver, "popup", "Password must not contain spaces."),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 8:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 8:")
        print(f"Sprawdzenie poprawności hasła (białe hasło):\n{e}")
    print("\n")

    #Niezgodne hasła
    try:
        test_registration(driver, "testuser7@example.co", "TestUser7", "TestPassword123#", "InneHaslo1#", True, 
        [Assersion(driver, "popup", "Passwords don't match"),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 9:")
    except AssertionError as e:
        pass_all_registration = False
        print(f"Błąd testu (Niezgodne hasła):\n{e}")
    print("\n")




    print("-------------------Testy logowania-------------------")
    pass_all_login = True
    try:
        test_login(driver, "testuserrrrrrr@example.co", "TestPassword123#", 
        [Assersion(driver, "popup", "Email doesn't exist in database!"),
         Assersion(driver, "body", "Please log in"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_login")]) 
        print("✔ Test 1:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 1:")
        print(f"Nieprawidłowy login:\n{e}")
    print("\n")

    try:
        test_login(driver, "testuser@example.co", "TestPassword123456#", 
        [Assersion(driver, "popup", "Wrong password!"),
         Assersion(driver, "body", "Please log in"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_login")]) 
        print("✔ Test 2:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 2:")
        print(f"Nieprawidłowe hasło:\n{e}")
    print("\n")

    try:
        test_login(driver, "", "TestPassword123456#", 
        [Assersion(driver, "popup", "Email doesn't exist in database!"),
         Assersion(driver, "body", "Please log in"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_login")])   
        print("✔ Test 3:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 3:")
        print(f"Pusty login:\n{e}")
    print("\n")

    try:
        test_login(driver, "testuser@example.co", "", 
        [Assersion(driver, "popup", "Wrong password!"),
         Assersion(driver, "body", "Please log in"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_login")]) 
        print("✔ Test 4:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 4:")
        print(f"puste hasło:\n{e}")
    print("\n")

    try:
        test_login(driver, "testuser@example.co", "TestPassword123#", 
        [Assersion(driver, "popup", "Login successed!"),
         Assersion(driver, "body", "Hello, TestUser!"),
         Assersion(driver, "url", "http://127.0.0.1:5000")])            
        print("✔ Test 5:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 5:")
        print(f"Prawidłowe logowanie:\n{e}")
    print("\n")

    if(pass_all_login):
        print("Wszystkie testy logowania przeszły pomyślnie!")