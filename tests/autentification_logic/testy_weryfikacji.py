from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager


# Konfiguracja Selenium
options = Options()
options.headless = True
gecko_driver_path = GeckoDriverManager().install()
service = Service(gecko_driver_path)
driver = webdriver.Firefox(service=service, options=options)

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

        print("uzyskane:")
        for alert in alerts:
            print(f"\t{alert.text}")
            if self.expected_message in alert.text:
                print("✅ Flash zawiera oczekiwany tekst.")
                return True
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

def test_registration(email, username, password, comfirm_password, accept_terms, Asseresions):
    driver.get("http://127.0.0.1:5000/register") 

    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email_input_reg"))
    )
    username_input = driver.find_element(By.NAME, "username_input_reg")
    password_input = driver.find_element(By.NAME, "password_input_reg")
    password_confirm_input = driver.find_element(By.NAME, "confirm_password_input_reg")
    checkbox =  driver.find_element(By.NAME, "terms_conditions_input_reg")

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

def test_login(email, password, Asseresions):
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
    for Asseresion in Asseresions:
        Asseresion.assert_result()

def TestUserWalidation():
    pass_all_registration = True
    created_test_user = False

    print("-------------------Testy rejestracji-------------------")

    #Prawidłowa rejestracja
    
    try:
        test_registration("testuser@example.co", "TestUser", "TestPassword123", "TestPassword123", True, 
        [Assersion(driver, "popup", " Registration successed! "),
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
        test_registration("testuser@example.co", "TestUser", "TestPassword123", "TestPassword123", True, 
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
        test_registration("testuser1@example.co", "TestUser1", "TestPassword123", "TestPassword123", False, 
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
        test_registration("", "TestUser2", "TestPassword123", "TestPassword123", True, 
        [Assersion(driver, "popup", " Wrong e-mail! "),
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
        test_registration("alan", "TestUser3", "TestPassword123", "TestPassword123", True, 
        [Assersion(driver, "popup", " Wrong e-mail! "),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 5:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 5:")
        print(f"Sprawdzenie poprawności maila(zły format):\n{e}")
    print("\n")

    #Pusta nazwa użytkownika
    try:
        test_registration("testuser4@example.co", "", "TestPassword123", "TestPassword123", True, 
        [Assersion(driver, "popup", " Wrong username "),
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
        test_registration("testuser5@example.co", "TestUser5", "", "", True, 
        [Assersion(driver, "popup", " Wrong passwoard! "),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 7:")
    except AssertionError as e:
        pass_all_registration = False
        print("✖ Test 7:")
        print(f"Sprawdzenie poprawności hasła (puste hasło):\n{e}")
    print("\n")

    try:
        test_registration("testuser6@example.co", "TestUser6", "               ", "               ", True, 
        [Assersion(driver, "popup", " Wrong passwoard! "),
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
        test_registration("testuser7@example.co", "TestUser7", "TestPassword123", "InneHaslo", True, 
        [Assersion(driver, "popup", "Passwords don't match"),
         Assersion(driver, "body", "Create an account"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_register")])
        print("✔ Test 9:")
    except AssertionError as e:
        pass_all_registration = False
        print(f"Błąd testu (Niezgodne hasła):\n{e}")

    if pass_all_registration:
        print("✖ Test 9:")
        print(f"Sprawdzenie rejestracji w przypadku rozbierznych haseł:\n {e}")
    print("\n")




    print("-------------------Testy logowania-------------------")
    pass_all_login = True
    try:
        test_login("testuserrrrrrr@example.co", "TestPassword123", 
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
        test_login("testuser@example.co", "TestPassword123456", 
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
        test_login("", "TestPassword123456", 
        [Assersion(driver, "popup", "Wrong password!"),
         Assersion(driver, "body", "Please log in"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_login")])   
        print("✔ Test 3:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 3:")
        print(f"Pusty login:\n{e}")
    print("\n")

    try:
        test_login("testuser@example.co", "", 
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
        test_login("testuser@example.co", "TestPassword123", 
        [Assersion(driver, "popup", "Login successed!"),
         Assersion(driver, "body", "Hello, TestUser!"),
         Assersion(driver, "url", "http://127.0.0.1:5000/handle_login")])            
        print("✔ Test 5:")
    except AssertionError as e:
        pass_all_login = False
        print("✖ Test 5:")
        print(f"Prawidłowe logowanie:\n{e}")
    print("\n")

    if(pass_all_login):
        print("Wszystkie testy logowania przeszły pomyślnie!")
    driver.quit()
