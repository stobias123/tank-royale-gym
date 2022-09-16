# TODO

* [x] Handler api rework.
    * This will clean up how we're passing manager references around 
    * [x] Move message handlers to inherit from BotManager.
* [ ] Finish control flow for step.
  * [x] `_get_frame` - returns the frame to the `obs` object.
  * [x] `_get_reward` - returns the reward from the last `tick_event`
  * [x] `_is_done` - checks if it's done.
  * [x] `_action_to_intent` - translate chosen action space into `botIntent`
* [x] Create enemy bot.
  * We need a bot that will just fire directly at our RL bot.
* [x] Implement event handling for the following
  * [x] `GameEndedEventForObserver` - `ControllerManager`
  * [x] `GameEndedEventForBot` - `BotManager`
* [ ] Put together a DQN for the agentbot :D 
