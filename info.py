import re
from os import environ

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
API_ID = environ.get('23171051')
API_HASH = environ.get('10331d5d712364f57ffdd23417f4513c')
BOT_TOKEN = environ.get('7398590079:AAH1Yai7B7AoOMsEB8HrQ9kkSiQYHs6aGAY')

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', "990262535").split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS',).split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('-1002001105061')
auth_grp = environ.get('AUTH_GROUP', "")
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
SUPPORT_CHANNEL = environ.get('CHANNEL_USERNAME')
SUPPORT_GROUP = environ.get('GROUP_USERNAME')
INDEX_USER = [int(environ.get('INDEX_USER', '6987799874'))]
INDEX_USER.extend(ADMINS)

# MongoDB information
DATABASE_URI = environ.get('mongodb+srv://Your:Your@cluster0.yrzwe0j.mongodb.net/?retryWrites=true&w=majority')
DATABASE_NAME = environ.get('DATABASE_NAME', "Your")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'wolve')

# Others
LOG_CHANNEL = int(environ.get('-1002145560187'))
FORCESUB_CHANNEL = int(environ.get('-1002001105061'))
SLOW_MODE_DELAY = int(environ.get('SLOW_MODE_DELAY', 60))
WAIT_TIME = int(environ.get('AUTO_DELETE_WAIT_TIME', 1800))
FORWARD_CHANNEL = int(environ.get('FORWARD_CHANNEL', ""))

# other
ACCESS_KEY = environ.get("LICENSE_ACCESS_KEY")
BIN_CHANNEL = environ.get("BIN_CHANNEL")
URL = environ.get("STREAM_URL")
SHORTNER_SITE = environ.get("OnePageLink.in")
SHORTNER_API = environ.get("da8ddb823eb0ac5d36a3ab19e9012bf4b8652200")
