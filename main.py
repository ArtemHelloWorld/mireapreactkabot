import logging
from bot import run_bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='main.log',
    filemode='a'
)


if __name__ == '__main__':
    run_bot()
