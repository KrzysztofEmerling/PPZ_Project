import shutil
import os

from autentification_logic.testy_weryfikacji import *

DB_instance_path = "instance/database.db"
DB_copy_path = "tests/database.db"

shutil.copy(DB_instance_path, DB_copy_path)

TestUserWalidation()

shutil.copy(DB_copy_path, DB_instance_path)
os.remove(DB_copy_path)