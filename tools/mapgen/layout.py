"""Hand-authored layout for the Farm Valley hub."""
import math, random
from catalog import *
from autotile import pick

W, H = 48, 34
BORDER = 3                       # forest thickness
SEED = 20260920

ROAD_X0, ROAD_X1 = 22, 24        # vertical main road (inclusive)
ROAD_Y0, ROAD_Y1 = 16, 18        # horizontal main road (inclusive)

YARD = (29, 4, 39, 13)           # house yard dirt pad, inclusive
HOUSE_CELL = (32, 5)             # top-left cell of the 6x6 house block
SPUR_X0, SPUR_X1 = 34, 35        # yard -> road

PLOT = (6, 20, 17, 28)           # fenced farm plot
PLOT_GATE = (11, 12)
SOIL_RECT = (8, 22, 15, 26)

POND_CX, POND_CY, POND_RX, POND_RY = 10.5, 8.0, 6.0, 3.4
ISLET_CELL = (12, 7)


def build_sets():
    path, soil, water = set(), set(), set()

    for y in range(2, H - 2):
        for x in range(ROAD_X0, ROAD_X1 + 1):
            path.add((x, y))
    for x in range(2, W - 2):
        for y in range(ROAD_Y0, ROAD_Y1 + 1):
            path.add((x, y))

    # house yard: rectangle with the four corners knocked off
    x0, y0, x1, y1 = YARD
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x in (x0, x1)) and (y in (y0, y1)):
                continue
            path.add((x, y))
    for y in range(y1 + 1, ROAD_Y0):
        for x in range(SPUR_X0, SPUR_X1 + 1):
            path.add((x, y))

    # short path from the road down to the farm plot gate
    for y in range(ROAD_Y1 + 1, PLOT[1] + 1):
        for x in range(PLOT_GATE[0], PLOT_GATE[1] + 1):
            path.add((x, y))

    sx0, sy0, sx1, sy1 = SOIL_RECT
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            soil.add((x, y))

    # pond: an ellipse with a couple of hand-placed bulges.  Its concave corners
    # are repaired later with grass-patch corner tiles (see water_corner_fixes).
    for y in range(H):
        for x in range(W):
            dx = (x + 0.5 - POND_CX) / POND_RX
            dy = (y + 0.5 - POND_CY) / POND_RY
            if dx * dx + dy * dy <= 1.0:
                water.add((x, y))
    for (bx, by) in ((4, 8), (5, 8), (16, 8), (16, 9)):
        water.add((bx, by))
    for _ in range(3):
        thin = {c for c in water
                if sum(((c[0] + dx, c[1] + dy) in water)
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) <= 1}
        if not thin:
            break
        water -= thin

    path -= water
    return path, soil, water


def water_corner_fixes(water):
    """Concave corners of the pond, as [(x, y, atlas_coord), ...] drawn on top."""
    fixes = []
    for (x, y) in sorted(water):
        inn = lambda dx, dy: (x + dx, y + dy) in water
        if not (inn(0, -1) and inn(0, 1) and inn(-1, 0) and inn(1, 0)):
            continue
        for name, (dx, dy) in (("NW", (-1, -1)), ("NE", (1, -1)),
                               ("SW", (-1, 1)), ("SE", (1, 1))):
            if not inn(dx, dy):
                fixes.append((x, y, GRASS_PATCH_CORNER[name]))
    return fixes


def build_ground(path, soil, water):
    base = {}
    for y in range(H):
        for x in range(W):
            base[(x, y)] = GRASS
    over = {}
    for (x, y) in sorted(path):
        over[(x, y)] = pick(path, x, y, PATH)
    for (x, y) in sorted(soil):
        over[(x, y)] = pick(soil, x, y, SOIL)
    for (x, y) in sorted(water):
        over[(x, y)] = pick(water, x, y, WATER)
    return base, over
