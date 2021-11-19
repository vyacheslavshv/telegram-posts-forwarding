import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("telegram")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('logs/log.log', maxBytes=200000, backupCount=10, encoding='utf-8')
formatter = logging.Formatter(fmt='%(asctime)s : %(levelname)s : %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

TOKEN_BOT = '2119379246:AAH65mUK8cjLj_ggscapWqGRiigpSdBjANQ'
# TOKEN_BOT = '1790953746:AAH57QwCGWgw3Ml3Mz2FXjktf5FKBsqcTSk' #Upwork Testing Bot

TG_API_ID = 1910144
TG_API_HASH = "275a53e95d045f6d980c222640f36add"

client_bot = None
client_user = None
client_user_db = None

banned_words = {
    "וויד", "ביקורת", "חממה", "פרסומת", "פרסום","בוטיק" ,"חשיש", "קנאביס", "ערוץ ביקורות", "מבצע", "פירסומת",
    "מחירון פירסום", "המדליף", "סאטיבה", "אינדיקה", "מתחזה", "קזינו", "הימורים", "http", "zop", ".com", "www",
    "פורסם"
}

OUR_LINK = "http://t.me/GlobalNewsRobot"
OUR_TAG = "@GlobalNewsRobot"
