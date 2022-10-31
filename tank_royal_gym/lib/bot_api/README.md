```mermaid
sequenceDiagram
    participant E as Environment
    participant A as Bot
    participant S as Server

E ->> A: Start Agent
A ->> S: Join Game
E ->>  S: Start Game
S ->>  A: Game Started Event
S ->>  E: Game Started Event
E ->>  S: Step
S ->>  A: TickEvent
A ->> A: Predict
A ->> S: BotIntent

```