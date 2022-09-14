# TODO

* [x] Handler api rework.
    * This will clean up how we're passing manager references around 
    * [x] Move message handlers to inherit from BotManager.
* [ ] Finish control flow for step.
  * [x] `_get_frame` - returns the frame to the `obs` object.
  * [x] `_get_reward` - returns the reward from the last `tick_event`
  * [ ] `_is_done` - checks if it's done.
  * [ ] `_action_to_intent` - translate chosen action space into `botIntent`
* [ ] Create enemy bot.
  * We need a bot that will just fire directly at our RL bot.