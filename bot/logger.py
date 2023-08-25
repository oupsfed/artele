import logging
from sys import stdout

# logging.basicConfig(
#     level=logging.ERROR,
#     filename='main.log',
#     filemode='w',
#     format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
#     encoding='utf-8'
# )
logging.basicConfig(
    level=logging.DEBUG,
    stream=stdout,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    encoding='utf-8'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stdout)
log_format = '%(asctime)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fmt=log_format)
handler.setFormatter(formatter)

logger.addHandler(handler)