import os

from secret_key_generator import secret_key_generator


path = os.path.abspath("persistant")
if not os.path.exists(path):
    os.mkdir(path)

class Flask:
    secret_key = secret_key_generator.generate(file_name="persistant/secret_key.txt")


password = os.environ.get("DEFAULT_PASS")

if password == "":
    password = "beelogger_station"
