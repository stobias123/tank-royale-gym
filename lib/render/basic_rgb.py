import numpy as np
import cv2 as cv
from tank_royal_manager.robocode_event_models import ScannedBotEvent, TickEventForBot
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
        cv.circle(img, (int(event.x), int(event.y)), BasicRGB.tank_bounding_radius, color, -1)

    def draw_scanned_bullet(self, img, event: BulletState):
        color = (0, 0, 255)
        cv.circle(img, (int(event.x), int(event.y)), BasicRGB.tank_bounding_radius, color, -1)

    def draw_tick(self, tick_event: TickEventForBot):
        img_shape = (self.map_height, self.map_width)
        img = np.zeros(img_shape, np.uint8)
        if tick_event is not None:
            for event in tick_event.events:
                if event['type'] == "ScannedBotEvent":
                    self.draw_scanned_bot(img, ScannedBotEvent(**event))
            for bullet in tick_event.bulletStates:
                self.draw_scanned_bullet(img, bullet)
        return img
