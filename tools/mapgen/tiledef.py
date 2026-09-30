"""Per-tile metadata: multi-cell sizes, y-sort pivots, collision, terrains."""
from catalog import *

# ---------------------------------------------------------------- multi-cell
# (src, col, row) -> (w, h)
MULTI = {
    (SPRING, 0, 3): (2, 2),   # dark shrub on opaque grass
    (SPRING, 0, 5): (2, 2),   # grass plateau / mossy ledge
    (SPRING, 2, 3): (2, 2),   # medium green bush
    (SPRING, 2, 5): (2, 2),   # bright yellow-green shrub
    (SPRING, 5, 1): (4, 3),   # big pale bush
    (SPRING, 5, 4): (4, 3),   # big dark bush
    (SPRING, 0, 7): (2, 2),   # grass islet in water
    (OBJECTS, 3, 0): (3, 4),  # tree A
    (OBJECTS, 6, 0): (3, 4),  # tree B
    (OBJECTS, 6, 4): (3, 1),  # stump
    (OBJECTS, 4, 4): (2, 2),  # haystack
    (OBJECTS, 0, 6): (6, 6),  # house
    (OBJECTS, 6, 7): (2, 2),  # door closed
    (OBJECTS, 6, 9): (2, 2),  # door open
    (PLANTS, 2, 4): (1, 2),   # tall crop stages
    (PLANTS, 3, 4): (1, 2),
    (PLANTS, 4, 4): (1, 2),
}

# ---------------------------------------------------------------------------
# Godot draws an atlas tile centred on its ANCHOR CELL, so a 6x6 house placed at
# cell (32, 5) would straddle cells 29..34 / 2..7.  texture_origin shifts the art
# back so the block occupies [anchor .. anchor + (w-1, h-1)], which is what the
# map generator assumes.  The property is SUBTRACTED, hence the negative values.
def texture_origin(w, h):
    return (-8 * (w - 1), -8 * (h - 1))

# ------------------------------------------------- y-sort pivot and collision
# Both are expressed relative to the ANCHOR CELL centre, i.e. block-local pixel
# coordinates minus (8, 8).  texture_origin is a rendering-only offset and does
# not move collision, so the two use the same frame.
#
# BASE[tile] = y of the sprite's lowest pixel inside its block.
BASE = {
    (SPRING, 5, 1): 46, (SPRING, 5, 4): 45,
    (SPRING, 2, 3): 29, (SPRING, 2, 5): 30,
    (SPRING, 0, 5): 31, (SPRING, 0, 3): 31, (SPRING, 0, 7): 31,
    (OBJECTS, 3, 0): 59, (OBJECTS, 6, 0): 59,
    (OBJECTS, 4, 4): 31, (OBJECTS, 6, 4): 11,
    (OBJECTS, 0, 6): 91,
    (OBJECTS, 6, 7): 30, (OBJECTS, 6, 9): 30,   # +3 so a door beats its house
    (PLANTS, 2, 4): 25, (PLANTS, 3, 4): 25, (PLANTS, 4, 4): 25,
}
YSORT = {k: v - 8 for k, v in BASE.items()}
for _c in range(9):                      # every 1x1 prop sorts from its foot
    for _r in range(6):
        YSORT.setdefault((OBJECTS, _c, _r), 7)
for _c in range(5):
    for _r in range(6):
        YSORT.setdefault((PLANTS, _c, _r), 7)

# COLL values are BLOCK-LOCAL rects (x0, y0, x1, y1), origin at the block's
# top-left corner; emit.py converts them to the anchor-cell frame.
def rect(x0, y0, x1, y1):
    return (x0, y0, x1, y1)

CELL = [rect(0, 0, 16, 16)]
COLL = {}

# --- water: block the wet part of each shoreline tile
COLL[(SPRING, 3, 8)] = CELL                          # open water
COLL[(SPRING, 3, 7)] = [rect(0, 8, 16, 16)]          # top bank
COLL[(SPRING, 3, 9)] = [rect(0, 0, 16, 8)]           # bottom bank
COLL[(SPRING, 2, 8)] = [rect(8, 0, 16, 16)]          # left bank
COLL[(SPRING, 4, 8)] = [rect(0, 0, 8, 16)]           # right bank
COLL[(SPRING, 2, 7)] = [rect(8, 8, 16, 16)]
COLL[(SPRING, 4, 7)] = [rect(0, 8, 8, 16)]
COLL[(SPRING, 2, 9)] = [rect(8, 0, 16, 8)]
COLL[(SPRING, 4, 9)] = [rect(0, 0, 8, 8)]
for _t in ((8, 7), (8, 9)):                          # rock / reeds in the water
    COLL[(SPRING, _t[0], _t[1])] = CELL

# --- foliage (4x3 blocks are 64x48, 2x2 are 32x32)
COLL[(SPRING, 5, 1)] = [rect(4, 14, 60, 44)]         # big pale bush
COLL[(SPRING, 5, 4)] = [rect(4, 16, 50, 44)]         # big dark bush
COLL[(SPRING, 0, 5)] = [rect(4, 10, 28, 30)]         # mossy ledge

# --- fences: a post or rail blocks its whole cell
for _t in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1),
           (0, 2), (1, 2), (2, 2), (0, 3), (1, 3)):
    COLL[(OBJECTS, _t[0], _t[1])] = CELL

COLL[(OBJECTS, 3, 0)] = [rect(15, 48, 33, 60)]       # tree A trunk
COLL[(OBJECTS, 6, 0)] = [rect(15, 48, 33, 60)]       # tree B trunk
COLL[(OBJECTS, 6, 4)] = [rect(11, 2, 33, 12)]        # stump
COLL[(OBJECTS, 4, 4)] = [rect(1, 12, 31, 31)]        # haystack
COLL[(OBJECTS, 0, 6)] = [rect(8, 2, 88, 92)]         # cabin footprint
COLL[(OBJECTS, 6, 7)] = [rect(6, 3, 26, 27)]         # closed door
for _t in ((0, 4), (1, 4), (1, 5), (2, 5)):          # barrel, chests, boulder
    COLL[(OBJECTS, _t[0], _t[1])] = [rect(1, 2, 15, 15)]

# ------------------------------------------------------------------- terrains
# terrain indices inside terrain_set_0
T_GRASS, T_PATH, T_SOIL, T_WATER = 0, 1, 2, 3

ROLE_BITS = {          # N  S  W  E  NW NE SW SE
    "C":        (1, 1, 1, 1, 1, 1, 1, 1),
    "N":        (0, 1, 1, 1, 0, 0, 1, 1),
    "S":        (1, 0, 1, 1, 1, 1, 0, 0),
    "W":        (1, 1, 0, 1, 0, 1, 0, 1),
    "E":        (1, 1, 1, 0, 1, 0, 1, 0),
    "NW":       (0, 1, 0, 1, 0, 0, 0, 1),
    "NE":       (0, 1, 1, 0, 0, 0, 1, 0),
    "SW":       (1, 0, 0, 1, 0, 1, 0, 0),
    "SE":       (1, 0, 1, 0, 1, 0, 0, 0),
    "iNW":      (1, 1, 1, 1, 0, 1, 1, 1),
    "iNE":      (1, 1, 1, 1, 1, 0, 1, 1),
    "iSW":      (1, 1, 1, 1, 1, 1, 0, 1),
    "iSE":      (1, 1, 1, 1, 1, 1, 1, 0),
    "iSW+iSE":  (1, 1, 1, 1, 1, 1, 0, 0),
    "iNW+iSW":  (1, 1, 1, 1, 0, 1, 0, 1),
    "iNW+iNE":  (1, 1, 1, 1, 0, 0, 1, 1),
    "iNE+iSE":  (1, 1, 1, 1, 1, 0, 1, 0),
    "hL":       (0, 0, 0, 1, 0, 0, 0, 0),
    "hM":       (0, 0, 1, 1, 0, 0, 0, 0),
    "hR":       (0, 0, 1, 0, 0, 0, 0, 0),
    "vT":       (0, 1, 0, 0, 0, 0, 0, 0),
    "vM":       (1, 1, 0, 0, 0, 0, 0, 0),
    "vB":       (1, 0, 0, 0, 0, 0, 0, 0),
    "dot":      (0, 0, 0, 0, 0, 0, 0, 0),
}
BIT_NAMES = ["top_side", "bottom_side", "left_side", "right_side",
             "top_left_corner", "top_right_corner",
             "bottom_left_corner", "bottom_right_corner"]


def terrain_assignments():
    """(src, col, row) -> (terrain_index, {bit_name: terrain_index})"""
    out = {}
    out[(SPRING,) + GRASS] = (T_GRASS, {n: T_GRASS for n in BIT_NAMES})
    for table, tid in ((PATH, T_PATH), (SOIL, T_SOIL), (WATER, T_WATER)):
        seen = set()
        for role, coord in table.items():
            if role not in ROLE_BITS or coord in seen:
                continue
            seen.add(coord)
            bits = ROLE_BITS[role]
            out[(SPRING,) + coord] = (
                tid, {n: (tid if b else T_GRASS) for n, b in zip(BIT_NAMES, bits)})
    return out


# ------------------------------------------------------------------ animation
# The sheet ships second frames for the water edges and the water decor: the
# pairs differ only in their foam/ripple pixels.  Wiring them as 2-frame tile
# animations makes the pond move.  (src, col, row) -> (columns, separation, speed)
ANIM = {
    (SPRING, 8, 7): (1, (0, 0), 1.4),    # rock in water   -> 8:8
    (SPRING, 8, 9): (1, (0, 0), 1.4),    # reeds in water  -> 8:10
    (SPRING, 2, 7): (1, (0, 2), 1.4),    # pond top-left   -> 2:10
    (SPRING, 3, 7): (1, (0, 2), 1.4),    # pond top edge   -> 3:10
    (SPRING, 4, 7): (1, (0, 2), 1.4),    # pond top-right  -> 4:10
}
# cells consumed as animation frames must not be declared as tiles of their own
ANIM_FRAME_CELLS = {(SPRING, 8, 8), (SPRING, 8, 10),
                    (SPRING, 2, 10), (SPRING, 3, 10), (SPRING, 4, 10)}
