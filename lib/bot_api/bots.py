import logging
import math
from typing import List

from gym import spaces
from tank_royal_manager.manager.bot_manager import BaseBotMessageHandler
from tank_royal_manager.robocode_event_models import TickEventForBot, BotIntent, ScannedBotEvent, BotState, MessageType

from lib.bot_api import constants
from lib.bot_api.base_bot import BasicBot


class CustomBotManager(BaseBotMessageHandler):
    def __init__(self, tickHandler, ws_address: str = 'ws://localhost:7654', bot_name: str = 'fireBot'):
        super().__init__(bot_name, ws_addr=ws_address)
        self.intent: BotIntent = BotIntent()
        self.BOT_FUNC_MAP[MessageType.TickEventForBot] = tickHandler


class FireBot(BasicBot):
    def __init__(self, ws_address: str = 'ws://localhost:7654', bot_name: str = 'fireBot'):
        super().__init__(ws_address, bot_name)
        self.botManager = CustomBotManager(self.handle_tick, ws_address, bot_name)
        self.botManager.start_thread()
        self.bots = []

    def handle_tick(self, tick: TickEventForBot):
        self.botManager.intent = BotIntent()
        self.find_bots(tick)
        self.get_self_info(tick)
        self.botManager.intent.firepower = 1
        if len(self.bots) > 0:
            bearing = self.bearing_to(self.bots[0].x, self.bots[0].y)
            self.botManager.intent.turnRate = bearing / 10
            self.botManager.intent.firepower = 3
            logging.info(f"Firing at bearing: {bearing}")
        else:
            self.botManager.intent.turnRate=1
        self.botManager.conn.send(self.botManager.intent.json())

    def find_bots(self, tick: TickEventForBot):
        self.bots = []
        for event in tick.events:
            if event['type'] == 'ScannedBotEvent':
                self.bots.append(ScannedBotEvent(**event))

    def get_self_info(self, tick: TickEventForBot):
        self.botManager.bot_state = tick.botState


class ScanAndFireBot(BaseBotMessageHandler):
    def __init__(self, ws_address: str = 'ws://localhost:7654', bot_name: str = 'fireBot'):
        super().__init__(bot_name, ws_addr=ws_address)
        self.phase = 'Scan'
        self.intent: BotIntent = None

    def handle_tick(self, tick: TickEventForBot):
        self.find_bots(tick)
        self.get_self_info(tick)

        self.conn.send(BotIntent(radarTurnRate=1).json())

    def get_self_info(self, tick: TickEventForBot):
        self.bot_state = tick.botState

    def find_bots(self, tick: TickEventForBot):
        self.bots = []
        for event in tick.events:
            if event['type'] == 'ScannedBotEvent':
                self.bots.append(ScannedBotEvent(**event))


class DriveAndScanBot(BasicBot):
    def __init__(self, ws_address: str = 'ws://localhost:7654', bot_name: str = 'drive_and_scan'):
        super().__init__(ws_address, bot_name)
        self.botManager = CustomBotManager(self.handle_tick, ws_address, bot_name)
        self.botManager.start_thread()
        self.bots = []

    def handle_tick(self, tick: TickEventForBot):
        self.last_tick = tick
        if self.botManager.intent is None:
            self.botManager.conn.send(BotIntent().json)
            return
        self.botManager.conn.send(self.botManager.intent.json())
