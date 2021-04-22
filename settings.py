import os

COMMAND_PREFIX = '^'
TOKEN = ''
BOT_NAME = 'Ninjabot'
BOT_COLOUR = 0xFF6E00

MYSQL_HOST = 'localhost'
MYSQL_USER = 'ninjabot'
MYSQL_PASSWD = '<password>'
MYSQL_DATABASE = 'ninjabot'

ILLEGAL_DIR = 'Illegal'
EMOJI_DIR = 'Emojis'

LOGGER_FORMAT = '%(asctime)-15s %(message)s'
LOGGER_FILE = 'ninjabot.log'

ADMIN = []
BANNED_USERS = []
WHITELISTED_SERVERS = []

SWEAR_WORDS = []
SPECIAL_SWEAR_WORDS = []
UNBANNED_WORDS = []

# Valid types: message, react, none
SWEAR_DEFAULT_TYPE = 'message'
SWEAR_GUILD_CUSTOM_TYPE = {}
SWEAR_USER_CUSTOM_TYPE = {}

NAMES = {}

try:
    with open(os.path.join(os.path.dirname(__file__), 'local_settings.py')) as f:
        exec(f.read()) in globals()
except IOError:
    pass
