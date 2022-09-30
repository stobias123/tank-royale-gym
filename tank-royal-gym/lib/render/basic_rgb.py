import numpy as np
import cv2 as cv
from tank_royal_manager.robocode_event_models import ScannedBotEvent, TickEventForBot, BotState
from tank_royal_manager.robocode_event_models import BulletState

basic_scanned_bot_event = ScannedBotEvent(
    scannedBotId=2,
    scannedByBotId=1,
    energy=2.8,
    x=473,
    y=241,
    direction=270,
    speed=1)


class BasicRGB:
    tank_bounding_radius = 18
    bullet_bounding_radius = 5

    def __init__(self, map_height, map_width):
        self.map_height = map_height
        self.map_width = map_width

    def draw_scanned_bot(self, img, event: ScannedBotEvent):
        color = (255, 0, 0)
        return cv.circle(img, (int(event.x), int(event.y)), BasicRGB.tank_bounding_radius, color, -1)

    def draw_self(self, img, event: BotState):
        color = (0, 255, 0)
        return cv.circle(img, (int(event.x), int(event.y)), BasicRGB.tank_bounding_radius, color, -1)

    def draw_scanned_bullet(self, img, event: BulletState):
        color = (0, 0, 255)
        return cv.circle(img, (int(event.x), int(event.y)), BasicRGB.tank_bounding_radius, color, -1)

    def draw_tick(self, tick_event: TickEventForBot, bots):
        img_shape = (self.map_height, self.map_width, 3)
        img = np.zeros(img_shape, np.uint8)
        if tick_event is not None:
            img = self.draw_self(img, tick_event.botState)
            if len(bots) > 0:
                for idx, bot in bots.items():
                    img = self.draw_scanned_bot(img, bot)
            if len(tick_event.bulletStates) > 0:
                for bullet in tick_event.bulletStates:
                    img = self.draw_scanned_bullet(img, bullet)
        return img
