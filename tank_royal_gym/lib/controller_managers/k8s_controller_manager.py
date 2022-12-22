from tank_royal_manager.manager import BaseControllerManager
from tank_royal_manager.robocode_event_models import game_setup, StartGame

K8S_GAME = game_setup.GameSetup(
    arenaHeight=600,
    arenaWidth=800,
    defaultTurnsPerSecond=30,
    gameType="classic",
    gunCoolingRate=0.1,
    isArenaHeightLocked=True,
    isArenaWidthLocked=True,
    isGunCoolingRateLocked=True,
    isMaxInactivityTurnsLocked=True,
    isMaxNumberOfParticipantsLocked=True,
    isMinNumberOfParticipantsLocked=True,
    isNumberOfRoundsLocked=True,
    isReadyTimeoutLocked=False,
    isTurnTimeoutLocked=False,
    maxInactivityTurns=450,
    maxNumberOfParticipants=20,
    minNumberOfParticipants=2,
    numberOfRounds=1,
    readyTimeout=1000000,
    turnTimeout=500000
)

class K8sControllerManager(BaseControllerManager):
    def __init__(self, ws_address: str):
        super().__init__(ws_address)

    def start(self):
        self.game_over = False
        packet = StartGame(
            gameSetup=K8S_GAME,
            botAddresses=self.bot_list
        )
        self.conn.send(packet.json())