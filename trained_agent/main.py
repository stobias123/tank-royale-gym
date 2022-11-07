import os

import numpy as np
import torch
from PIL import Image

from tank_royal_gym.lib.bot_api.base_bot import BasicBot
from tank_royal_gym.lib.bot_api.bots import CustomBotManager
from tank_royal_gym.lib.render.basic_rgb import BasicRGB
from tank_royal_manager.robocode_event_models import TickEventForBot, BotIntent, ScannedBotEvent, BotState, MessageType, \
    GameEndedEventForBot
import logging
from stable_baselines3 import PPO
from torchvision import transforms as T


class AgentBot(BasicBot):
    def __init__(self, ws_address: str = 'ws://localhost:7654', bot_name: str = 'agentBot'):
        super().__init__(ws_address, bot_name)
        logging.info(f"[{bot_name}]  -- Init --")
        logging.info(f"[{bot_name}]  Connecting to {ws_address}")
        self.botManager = CustomBotManager(self.handle_tick, ws_address, bot_name)
        self.model = PPO.load("models/robocode-model")
        self.HEIGHT: int = 600
        self.WIDTH: int = 800
        self.renderer = BasicRGB(map_height=self.HEIGHT, map_width=self.WIDTH)
        self.tick: TickEventForBot = None

    def handle_tick(self, tick: TickEventForBot):
        self.find_bots(tick)
        frame = self._get_frame(tick)
        frame = self.preprocess(frame)
        action, ignore = self.model.predict(frame)
        intent = self.action_to_intent(action.max())
        if self.botManager.intent is None:
            self.botManager.conn.send(BotIntent().json)
            return
        self.botManager.conn.send(intent.json())

    def handle_game_event(self, event: GameEndedEventForBot):
        logging.info(f"[{self.bot_name}]  -- GameEnd Event -- \n \t {event}")

    def _get_frame(self, tick: TickEventForBot):
        #return self.renderer.draw_tick(tick_event=self.bot_agent.last_tick, bots=self.bot_agent.bots)
        return self.renderer.draw_tick(tick_event=tick, bots=self.bots)

    def run(self):
        self.botManager.start_thread()

    def preprocess(self, observation):
        ## Grayscale
        observation = np.transpose(observation, (2, 0, 1))
        observation = torch.tensor(observation.copy(), dtype=torch.float)
        grayscale = T.Grayscale()
        transforms = T.Compose(
            [T.Resize((240, 320)), T.Normalize(0, 255)]
        )
        observation = grayscale(observation)
        res = transforms(observation).squeeze(0)
        return res

if __name__ == '__main__':
    ## Get the WS_ADDRESS from the environment variable
    ws_address = os.environ.get('WS_ADDRESS')
    ws_port = os.environ.get('WS_PORT')
    bot_name = os.environ.get('BOT_NAME')
    bot = AgentBot(ws_address=f"ws://{ws_address}:{ws_port}", bot_name=bot_name)
    bot.run()