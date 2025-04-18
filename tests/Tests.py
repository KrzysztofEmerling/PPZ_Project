import shutil
import os

from autentification_logic.testy_weryfikacji import *

from integrations.integration_tests import *

from admin.admin_tests import * 


DB_instance_path = "instance/database.db"
DB_copy_path = "tests/database.db"

# Konfiguracja Selenium
options = Options()
options.headless = True
gecko_driver_path = GeckoDriverManager().install()
service = Service(gecko_driver_path)
shutil.copy(DB_instance_path, DB_copy_path)

driver = webdriver.Firefox(service=service, options=options)
TestUserWalidation(driver)
driver.quit()

driver = webdriver.Firefox(service=service, options=options)
IntegrationTests(driver)
driver.quit()

driver = webdriver.Firefox(service=service, options=options)
TestAdminPanel(driver)
driver.quit()

shutil.copy(DB_copy_path, DB_instance_path)
os.remove(DB_copy_path)