import os
from secret_key_generator import secret_key_generator

path = os.path.abspath("persistant")
if not os.path.exists(path):
    os.mkdir(path)

class Flask:
    host = "0.0.0.0"
    port = 2667
    secret_key = secret_key_generator.generate(file_name="persistant/secret_key.txt")
    debug = False


password = "beelogger_station_123"
