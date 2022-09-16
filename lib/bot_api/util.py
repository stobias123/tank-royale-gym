def normalize_relative_angle(angle: float):
    mod_angle = angle % 360
    if mod_angle >= 0:
        return mod_angle if mod_angle < 180 else (mod_angle - 360)
    else:
        return mod_angle if mod_angle >= -180 else (mod_angle + 360)

# calc_bearing Calculates the bearing (delta angle) between the input direction and the direction of this bot.

def calc_bearing(direction: float):
    return normalize_relative_angle(direction - direction)

# convert this kotlin function to python
# default double directionTo(double x, double y) {
#        return normalizeAbsoluteAngle(Math.toDegrees(Math.atan2(y - getY(), x - getX())));
#    }
def direction_to(x: float, y: float):
    return normalize_absolute_angle(math.atan2(y - self.bot_state.y, x - self.bot_state.x))