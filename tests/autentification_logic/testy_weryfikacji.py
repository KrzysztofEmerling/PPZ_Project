from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager


# Konfiguracja Selenium
options = Options()
# options.headless = True  # Odkomentuj, jeśli chcesz tryb headless
gecko_driver_path = GeckoDriverManager().install()
service = Service(gecko_driver_path)
driver = webdriver.Firefox(service=service, options=options)

def test_registration(email, username, password, comfirm_password, expected_message):
    driver.get("http://127.0.0.1:5000/register") 

    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email_input_reg"))
    )
    username_input = driver.find_element(By.NAME, "username_input_reg")
    password_input = driver.find_element(By.NAME, "password_input_reg")
    password_confirm_input = driver.find_element(By.NAME, "confirm_password_input_reg")

    login_button = driver.find_element(By.XPATH, "//button[text()='Sign up']")
    
    # Wpisanie danych
    email_input.clear()
    username_input.clear()
    password_input.clear()
    password_confirm_input.clear()

    email_input.send_keys(email)
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_confirm_input.send_keys(comfirm_password)

    login_button.click()

    
    # Oczekiwanie na nową stronę
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert expected_message in body_text, f"Niepoprawny komunikat: {body_text}"

def test_login(email, password, expected_message):
    driver.get("http://127.0.0.1:5000/login") 

    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email_input_login"))
    )
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
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert expected_message in body_text, f"Niepoprawny komunikat: {body_text}"


def TestUserWalidation():
    pass_all_registration = True
    created_test_user = False

    print("-------------------Testy rejestracji-------------------")

    #Prawidłowa rejestracja
    try:
        test_registration("testuser@example.com", "testuser", "TestPassword123", "TestPassword123", "Zarejestrowano pomyślnie")
        created_test_user = True
        print("✔ Test 1:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 1:")
        print(f"Błąd testu (Prawidłowa rejestracja): {e}, brak komunikatu o pomyślnym utworzeniu konta")
    print("\n")

    #Podwójna rejestracja tego samego użytkownika
    try:
        test_registration("testuser@example.com", "testuser", "TestPassword123", "TestPassword123", "Email already exists")
        print("✔ Test 2:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 2:")
        print(f"Błąd testu (Podwójna rejestracja): {e}")
    print("\n")

    #Pusty adres e-mail
    try:
        test_registration("", "testuser2", "TestPassword123", "TestPassword123", "Adres e-mail nie może być pusty")
        print("✔ Test 3:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 3:")
        print(f"Błąd testu (Pusty adres e-mail): {e}, brak komunikatu o błędnie wprowadzonym mailu")
    print("\n")

    # Bledny e-mail
    try:
        test_registration("alan", "testuser3", "TestPassword123", "TestPassword123", "Blendny adres email")
        print("✔ Test 4:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 4:")
        print(f"Błąd testu (Błędny adres e-mail): {e}")
    print("\n")

    #Pusta nazwa użytkownika
    try:
        test_registration("testuser4@example.com", "", "TestPassword123", "TestPassword123", "Nazwa użytkownika nie może być pusta")
        print("✔ Test 5:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 5:")
        print(f"Błąd testu (Pusta nazwa użytkownika): {e}")
    print("\n")

    #Puste hasło
    try:
        test_registration("testuser5@example.com", "testuser5", "", "", "Hasło nie może być puste")
        print("✔ Test 6:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 6:")
        print(f"Błąd testu (Puste hasło): {e}")
    print("\n")

    try:
        test_registration("testuser6@example.com", "testuser6", "               ", "               ", "Hasło nie może zawierać białych znaków")
        print("✔ Test 7:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 7:")
        print(f"Błąd testu (\"Białe\" hasło): {e}")
    print("\n")

    #Niezgodne hasła
    try:
        test_registration("testuser7@example.com", "testuser7", "TestPassword123", "InneHaslo", "Passwords don't match")
        print("✔ Test 8:")
    except AssertionError as e:
        pass_all_registration = False
        print(f"Błąd testu (Niezgodne hasła): {e}")

    if pass_all_registration:
        print("Wszystkie testy rejestracji przeszły pomyślnie!")
    print("\n")

    print("-------------------Testy logowania-------------------")
    pass_all_login = True
    try:
        test_login("testuserrrrrrr@example.com", "TestPassword123", "User doesn't exist in database")   # Nieprawidłowy login
        print("✔ Test 1:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 1:")
        print(f"Błąd testu (Nieprawidłowy login): {e}")
    print("\n")

    try:
        test_login("testuser@example.com", "TestPassword123456", "User doesn't exist in database")   #Nieprawidłowe hasło
        print("✔ Test 2:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 2:")
        print(f"Błąd testu (Nieprawidłowe hasło): {e}")
    print("\n")

    try:
        test_login("", "TestPassword123456", "User doesn't exist in database")                   #Login nie może być pusty
        print("✔ Test 3:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 3:")
        print(f"Błąd testu (Pusty login): {e}")
    print("\n")

    try:
        test_login("testuser@example.com", "", "User doesn't exist in database")             #Hasło nie może być puste
        print("✔ Test 4:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 4:")
        print(f"Błąd testu (puste hasło): {e}")
    print("\n")

    try:
        test_login("testuser@example.com", "TestPassword123", "Zalogowano pomyślnie")              #Prawidłowe logowanie
        print("✔ Test 5:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 5:")
        print(f"Błąd testu (Prawidłowe logowanie): {e}")
    print("\n")

    if(pass_all_login):
        print("Wszystkie testy logowania przeszły pomyślnie!")
    driver.quit()
