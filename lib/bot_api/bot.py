import threading
from time import sleep
from typing import List

from tank_royal_manager.manager.bot_manager import BotManager
from tank_royal_manager.manager.bot_manager import BaseBotMessageHandler
from tank_royal_manager.robocode_event_models import TickEventForBot, BotIntent, ScannedBotEvent


class Bot:
    def __init__(self, ws_addr: str = 'ws://localhost:7654', bot_name: str = 'baseBot'):
        self.botManager = BotManager(bot_name, ws_addr, DriveAndScanBot)
        self.botManager.start_thread()



class BotHandler:
    def __init__(self):
        pass


class DriveAndScanBot(BaseBotMessageHandler):
    def __init__(self, man: BotManager):
        super().__init__(man)
        self.bot_map = {}

    def handle_tick(self, tick: TickEventForBot):
        intent = BotIntent(targetSpeed=1, radarTurnRate=999)
        self.man.conn.send(intent.json())
        if len(tick.events) > 0:
            self.parse_events(tick.events)

    def parse_events(self, events: List[dict]):
        for event in events:
            if event['type'] == 'ScannedBotEvent':
                botEvent = ScannedBotEvent(**event)
                self.bot_map[botEvent.scannedBotId] = botEvent
