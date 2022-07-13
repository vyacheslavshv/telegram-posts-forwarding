import logging
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
from utils import LimitedSizeDict

logger = logging.getLogger("telegram")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('logs/log.log', maxBytes=200000, backupCount=10, encoding='utf-8')
formatter = logging.Formatter(fmt='%(asctime)s : %(levelname)s : %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

config = ConfigParser()
config.read('config.ini')
config.sections()
TOKEN_BOT = config['BOT']['Token']

TG_API_ID = 1910144
TG_API_HASH = "275a53e95d045f6d980c222640f36add"

client_bot = None
client_user = None
client_user_db = None
user_flood_wait = None
stopped_channels = dict()

# OUR_OUTRO = "הצטרפו אלינו לערוץ"
OUR_LINK = "👉🏼 t.me/BestNewsIsraelBot 👈🏼"
OUR_TAG = "🔥 @BestNewsIsraelBot 🔥 "
OUR_OUTRO = "\n\nהצטרפו אלינו לערוץ" + "\n" + OUR_LINK + "\n" + OUR_TAG



TRANSFERS_PER_PAGE = 10
STOP_WORDS_PER_PAGE = 20

TORTOISE_ORM = {
     "connections": {"default": 'sqlite://db_files/db.sqlite3'},
     "apps": {
         "models": {
             "models": ["tables", "aerich.models"],
             "default_connection": "default",
         },
     },
 }

problematic_channel = -1001534901673
event_messages = LimitedSizeDict(size_limit=500)
