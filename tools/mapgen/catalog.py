"""Tile catalogue for the Tiny Wonder Farm assets (16x16 grid, col:row = x:y)."""

PROJECT = "/Users/ladislav/Documents/Documents - Ladislav’s MacBook Pro/farm-valley-prototype"

# ---- atlas source ids (must match the order written into the TileSet) ----
SPRING  = 0   # Assets/.../tilemaps/spring farm tilemap.png        9 x 20
OBJECTS = 1   # Assets/tilesets/farm_objects_atlas.png (padded)    9 x 12
PLANTS  = 2   # Assets/.../objects&items/plants free.png           5 x 6
ITEMS   = 3   # Assets/.../objects&items/items free.png            5 x 3

ATLAS_FILES = {
    SPRING:  "Assets/Tiny Wonder Farm Free/tilemaps/spring farm tilemap.png",
    OBJECTS: "Assets/tilesets/farm_objects_atlas.png",
    PLANTS:  "Assets/Tiny Wonder Farm Free/objects&items/plants free.png",
    ITEMS:   "Assets/Tiny Wonder Farm Free/objects&items/items free.png",
}
# source png used to build the padded objects atlas
OBJECTS_SRC = "Assets/Tiny Wonder Farm Free/objects&items/farm objects free.png"

# ---------------------------------------------------------------- ground ---
GRASS = (3, 1)                      # flat grass fill, RGB(165,197,67)

# Autotile role tables.  Roles are keyed by the 8-neighbour signature:
#   sides   N S W E   (1 = same terrain)
#   corners NW NE SW SE (only consulted when all four sides are 1)
PATH = {                            # light dirt path, rows 11-15
    "C":  (6, 12),
    "N":  (6, 11), "S": (6, 13), "W": (5, 12), "E": (7, 12),
    "NW": (5, 11), "NE": (7, 11), "SW": (5, 13), "SE": (7, 13),
    "iSE": (0, 14), "iSW": (1, 14), "iNE": (0, 15), "iNW": (1, 15),
    "iSW+iSE": (2, 12), "iNW+iSW": (3, 12), "iNW+iNE": (2, 13), "iNE+iSE": (3, 13),
    "hL": (0, 11), "hM": (1, 11), "hR": (2, 11), "dot": (3, 11),
    "vT": (4, 11), "vM": (4, 12), "vB": (4, 13),
}
SOIL = {                            # dark tilled earth, rows 14-18
    "C":  (6, 15),
    "N":  (6, 14), "S": (6, 16), "W": (5, 15), "E": (7, 15),
    "NW": (5, 14), "NE": (7, 14), "SW": (5, 16), "SE": (7, 16),
    "iSE": (2, 17), "iSW": (3, 17), "iNE": (2, 18), "iNW": (3, 18),
    "iSW+iSE": (4, 17), "iNW+iSW": (5, 17), "iNW+iNE": (4, 18), "iNE+iSE": (5, 18),
    "hL": (0, 16), "hM": (1, 16), "hR": (2, 16), "dot": (3, 16),
    "vT": (4, 14), "vM": (4, 15), "vB": (4, 16),
}
WATER = {                           # pond cut into grass, rows 7-9
    "C":  (3, 8),
    "N":  (3, 7), "S": (3, 9), "W": (2, 8), "E": (4, 8),
    "NW": (2, 7), "NE": (4, 7), "SW": (2, 9), "SE": (4, 9),
    # no inner-corner pieces exist for water -> the generator keeps ponds convex
    "vT": (3, 7), "vM": (3, 8), "vB": (3, 9),
    "hL": (2, 8), "hM": (3, 8), "hR": (4, 8), "dot": (3, 8),
}

# flat, non-colliding ground decals (transparent background)
PEBBLES     = [(0, 19), (1, 19)]
DIRT_PATCH  = [(2, 19), (3, 19), (4, 19), (5, 19), (6, 19), (7, 19)]
GRASS_TUFT  = [(0, 0), (1, 0), (0, 1), (0, 2), (4, 5)]   # 4:5 is a clover scatter
FLOWERS     = [(1, 1), (1, 2)]
WATER_ROCK  = [(8, 7)]              # rock in water (2-frame ripple animation)
REEDS       = [(8, 9)]              # reeds in water (2-frame ripple animation)

# --------------------------------------------------------------- foliage ---
# (col, row, w, h) blocks in the spring atlas.  All sit on transparent bg
# except SHRUB_ON_GRASS which has grass baked in.
BUSH_LIGHT   = (2, 0, 3, 3)   # pale-green round bush, dark outline
BUSH_YELLOW  = (5, 1, 4, 3)   # big yellow-green bush
BUSH_DARK    = (5, 4, 4, 3)   # big dark-green bush
BUSH_MED     = (2, 3, 2, 2)   # medium green bush
SHRUB_YELLOW = (2, 5, 2, 2)   # small yellow-green shrub
BUSH_ROCKBASE= (0, 5, 2, 2)   # bush growing out of a rocky ledge
SHRUB_GRASS  = (0, 3, 2, 2)   # dark shrub, OPAQUE grass background

BIG_BUSHES = [BUSH_YELLOW, BUSH_DARK]
MID_BUSHES = [BUSH_LIGHT, BUSH_MED, SHRUB_YELLOW]

# ---------------------------------------------------------------- objects --
TREE_A   = (3, 0, 3, 4)   # broad green tree
TREE_B   = (6, 0, 3, 4)   # rounder green tree
STUMP    = (6, 4, 3, 1)
BASKET   = (0, 4, 1, 1)
BARREL   = (0, 4, 1, 1)
CHEST    = (1, 4, 1, 1)
CHEST_OPEN = (1, 5, 1, 1)
FLOWER_W = (2, 4, 1, 1)
FLOWER_R = (3, 4, 1, 1)
BOULDER  = (2, 5, 1, 1)
LEAFY    = (3, 5, 1, 1)
STICK    = (0, 5, 1, 1)
HAYSTACK = (4, 4, 2, 2)
HOUSE    = (0, 6, 6, 6)
DOOR     = (6, 7, 2, 2)

# fence pieces (farm objects atlas)
F_TL = (0, 0)   # post left + rails, post continues down
F_TR = (2, 0)   # post right + rails, post continues down
F_BL = (0, 2)   # post left + rails, post capped
F_BR = (2, 2)   # post right + rails, post capped
F_H  = (1, 2)   # rails with a centred post
F_VL = (0, 1)   # bare post, left-aligned  (vertical run)
F_VR = (2, 1)   # bare post, right-aligned (vertical run)
F_POST_L = (1, 1)  # standalone capped post, left-aligned
F_END_L  = (1, 3)  # post left  + rails going right (open end)
F_END_R  = (0, 3)  # post right + rails coming from the left (open end)

# crops: plants atlas, column = growth stage, row = crop type
CROP_ROWS = {"squash": 0, "carrot": 1, "potato": 2, "berry": 3}
CROP_TALL = (3, 4, 1, 2)   # tall leafy crop, 1x2

# Grass-patch tiles (grass drawn on transparency, dark tufted rim).  The corner
# pieces are exactly the shape of a missing inner corner, so they are used to
# repair the concave corners of the pond, which the water set has no art for.
GRASS_PATCH_CORNER = {   # which diagonal is missing -> tile whose grass sits there
    "NW": (4, 2), "NE": (2, 2), "SW": (4, 0), "SE": (2, 0),
}

# grass islet that sits inside water (2 wide, 3 tall, cyan baked in)
ISLET = (0, 7, 2, 2)   # grass islet (cyan baked in)
SHORE_LEDGE = (0, 9, 2, 1)
