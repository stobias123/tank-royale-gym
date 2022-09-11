import rel
import threading
from time import sleep
from tank_royal_manager import BotManager

class Bot:
    def __init__(self, bot_name: str = 'baseBot'):
        self.connection_manager = BotManager(bot_name)

