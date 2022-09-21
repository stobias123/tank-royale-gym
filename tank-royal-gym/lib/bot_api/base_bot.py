import math
from typing import List

from gym.vector.utils import spaces
from tank_royal_manager.manager.bot_manager import BaseBotMessageHandler
from tank_royal_manager.robocode_event_models import BotIntent, ScannedBotEvent, TickEventForBot, BotState, MessageType

import lib.bot_api.constants as constants


class BasicBot:
    def __init__(self, ws_address: str = 'ws://localhost:7654', bot_name: str = 'baseBot'):
        self.botManager: BaseBotMessageHandler = None
        # self.botManager.start_thread()
        self.bots: {}
        self.bot_state: BotState = None
        self.last_tick: TickEventForBot = None
        self.last_frame = None
        self.action_space = spaces.Discrete(5)

    def action_to_intent(self, action: int):
        # W
        if action == 0:
            self.botManager.intent = BotIntent(targetSpeed=constants.MAX_FORWARD_SPEED)
        # A
        elif action == 1:
            self.botManager.intent = BotIntent(turnRate=constants.MAX_TURN_RATE)
        # S
        elif action == 2:
            self.botManager.intent = BotIntent(targetSpeed=-1 * constants.MAX_FORWARD_SPEED)
        # D
        elif action == 3:
            self.botManager.intent = BotIntent(turnRate=-1 * constants.MAX_TURN_RATE)
        # Space
        elif action == 4:
            self.botManager.intent = BotIntent(firepower=5)

    def normalize_relative_angle(self, angle: float):
        angle %= 360
        return angle if angle >= 0 else (angle + 360 if angle >= -180 else angle - 360)

    # calc_bearing Calculates the bearing (delta angle) between the input direction and the direction of this bot.

    def calc_bearing(self, direction: float):
        return self.normalize_relative_angle(direction - direction)

    # convert this kotlin function to python
    # default double directionTo(double x, double y) {
    #        return normalizeAbsoluteAngle(Math.toDegrees(Math.atan2(y - getY(), x - getX())));
    #    }
    def direction_to(self, x: float, y: float):
        return self.normalize_absolute_angle(
            math.degrees(math.atan2(y - self.botManager.bot_state.y, x - self.botManager.bot_state.x)))

    def normalize_absolute_angle(self, angle):
        return angle % 360 if angle >= 0 else angle + 360

    def bearing_to(self, x: float, y: float):
        return int(self.normalize_absolute_angle(self.direction_to(x, y) - self.botManager.bot_state.direction))


    ## find_bots iterates through the tick.events dictionary, and if the dictionary item is of type MessageType.ScannedBotEvent, it adds it to self.bots
    def find_bots(self, tick: TickEventForBot):
        self.bots = []
        for event in tick.events:
            if 'type' in event:
                if event['type'] == MessageType.ScannedBotEvent:
                    event = ScannedBotEvent(**event)
                    self.bots[event.scannedBotId] = event

    ## get_self_info gets the bot's state from the tick event and stores it in self.bot_stateo
    def get_self_info(self, tick: TickEventForBot):
        self.bot_state = tick.botState

    # def turnToFaceTarget(self, x, y):
    #     bearing = self.bearing_to(x, y)
    #     if bearing >= 0:
    #         turnDirection = 1
    #     else:
    #         turnDirection = -1
    #     turnLeft(bearing)