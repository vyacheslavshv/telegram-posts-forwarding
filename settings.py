import logging
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser

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

banned_words = {
    "וויד", "ביקורת", "חממה", "פרסומת", "פרסום","בוטיק" ,"חשיש", "קנאביס", "ערוץ ביקורות", "מבצע", "פירסומת",
    "מחירון פירסום", "המדליף", "סאטיבה", "אינדיקה", "מתחזה", "קזינו", "הימורים", "zop", "פורסם"
}

OUR_LINK = "http://t.me/BestNewsIsraelBot"
OUR_TAG = "@BestNewsIsraelBot"

TRANSFERS_PER_PAGE = 10
