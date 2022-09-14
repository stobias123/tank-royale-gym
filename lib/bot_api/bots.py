from typing import List

from gym import spaces
from tank_royal_manager.manager.bot_manager import BaseBotMessageHandler
from tank_royal_manager.robocode_event_models import TickEventForBot, BotIntent, ScannedBotEvent

from lib.bot_api import constants


class BotHandler:
    def __init__(self):
        pass


class BasicBot:
    def __init__(self, ws_address: str = 'ws://localhost:7654', bot_name: str = 'baseBot'):
        self.botManager = DriveAndScanBot('drive_and_scan', ws_address)
        self.botManager.start_thread()
        self.last_tick = None
        self.last_frame = None
        self.botManager.queued_intent = None
        self.action_space = spaces.Discrete(5)

    def action_to_intent(self, action: int):
        # W
        if action == 0:
            self.botManager.queued_intent = BotIntent(targetSpeed=constants.MAX_FORWARD_SPEED)
        # A
        elif action == 1:
            self.botManager.queued_intent = BotIntent(turnRate=constants.MAX_TURN_RATE)
        # S
        elif action == 2:
            self.botManager.queued_intent = BotIntent(targetSpeed=-1 * constants.MAX_FORWARD_SPEED)
        # D
        elif action == 3:
            self.botManager.queued_intent = BotIntent(turnRate=-1 * constants.MAX_TURN_RATE)
        # Space
        elif action == 4:
            self.botManager.queued_intent = BotIntent(firepower=5)


class FireBot:
    def __init__(self, ws_address: str = 'ws://localhost:7654', bot_name: str = 'fireBot'):
        self.botManager = ScanAndFireBot(bot_name, ws_address)
        self.botManager.start_thread()


class ScanAndFireBot(BaseBotMessageHandler):
    def __init__(self, ws_address: str = 'ws://localhost:7654', bot_name: str = 'fireBot'):
        super().__init__(bot_name,ws_addr=ws_address)
        self.phase = 'Scan'

    def handle_tick(self, tick: TickEventForBot):
        bots = tick.events
        self.conn.send(BotIntent(radarTurnRate= 1).json())

    def find_bots(self, tick: TickEventForBot):
        bots = []
        for event in tick.events:
            if event['type'] == 'ScannedBotEvent':
                bots.append(ScannedBotEvent(**event))



class DriveAndScanBot(BaseBotMessageHandler):
    def handle_tick(self, tick: TickEventForBot):
        self.last_tick = tick
        if self.queued_intent is None:
            self.conn.send(BotIntent().json)
            return
        self.conn.send(self.queued_intent.json())
