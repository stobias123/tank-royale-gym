def normalizeRelativeangle(angle: float):
    mod_angle = angle % 360
    if angle % 360 >= 0:
        if angle < 180