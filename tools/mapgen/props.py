"""Prop placement for the Farm Valley hub."""
import random
from catalog import *
from layout import *


def P(src, block, x, y, solid=False):
    ax, ay, w, h = block
    return dict(src=src, ax=ax, ay=ay, w=w, h=h, x=x, y=y,
                sort_y=(y + h) * 16, solid=solid)


class Board:
    def __init__(self, n_layers=4):
        self.layers = [dict() for _ in range(n_layers)]
        self.items = []

    def free(self, layer, x, y, w, h):
        L = self.layers[layer]
        return all((x + dx, y + dy) not in L
                   for dy in range(h) for dx in range(w))

    def put(self, layer, p):
        L = self.layers[layer]
        for dy in range(p["h"]):
            for dx in range(p["w"]):
                L[(p["x"] + dx, p["y"] + dy)] = p
        p["layer"] = layer
        self.items.append(p)
        return p

    def try_put(self, layer, p):
        return self.put(layer, p) if self.free(layer, p["x"], p["y"], p["w"], p["h"]) else None

    def try_any(self, layers, p):
        for l in layers:
            if self.free(l, p["x"], p["y"], p["w"], p["h"]):
                return self.put(l, p)
        return None


def build_props(path, soil, water):
    rng = random.Random(SEED)
    b = Board(4)
    blocked = set()
    reserved = set(path) | set(soil) | set(water)   # nothing decorative may land here

    def block(x, y, w=1, h=1):
        for dy in range(h):
            for dx in range(w):
                blocked.add((x + dx, y + dy))

    def reserve(x, y, w=1, h=1):
        for dy in range(h):
            for dx in range(w):
                reserved.add((x + dx, y + dy))

    # keep the built areas clear before anything is sown
    reserve(PLOT[0] - 1, PLOT[1] - 1, PLOT[2] - PLOT[0] + 3, PLOT[3] - PLOT[1] + 3)
    reserve(HOUSE_CELL[0], HOUSE_CELL[1], 6, 6)

    # ------------------------------------------------------------- forest ---
    def forest_blob():
        r = rng.random()
        if r < 0.40:  return SPRING, BUSH_DARK
        if r < 0.70:  return SPRING, BUSH_YELLOW
        if r < 0.88:  return OBJECTS, (TREE_A if rng.random() < 0.5 else TREE_B)
        return SPRING, BUSH_MED

    def sow(x, y):
        src, blk = forest_blob()
        if any((x + dx, y + dy) in reserved
               for dx in range(blk[2]) for dy in range(blk[3])):
            return None
        return b.try_any((0, 1, 2), P(src, blk, x, y, solid=True))

    x = -4
    while x < W + 3:
        for y in (-2, 0, 2):
            sow(x + rng.randint(-1, 1), y + rng.randint(0, 1))
        for y in (H - 5, H - 3, H - 1):
            sow(x + rng.randint(-1, 1), y + rng.randint(-1, 0))
        x += rng.randint(2, 3)
    y = -4
    while y < H + 3:
        for x0 in (-3, -1, 1):
            sow(x0 + rng.randint(0, 1), y + rng.randint(-1, 1))
        for x0 in (W - 5, W - 3, W - 1):
            sow(x0 + rng.randint(-1, 0), y + rng.randint(-1, 1))
        y += rng.randint(2, 3)

    for yy in range(-3, H + 3):
        for xx in range(-3, W + 3):
            if xx < BORDER or xx >= W - BORDER or yy < BORDER or yy >= H - BORDER:
                block(xx, yy)
                reserved.add((xx, yy))

    # -------------------------------------------------------------- house ---
    hx, hy = HOUSE_CELL
    b.put(3, P(OBJECTS, HOUSE, hx, hy, solid=True))
    block(hx + 1, hy + 1, 4, 5)
    reserve(hx, hy, 6, 6)
    b.put(2, P(OBJECTS, DOOR, hx + 2, hy + 4))

    def spot(x, y, src, blk, solid=False, layers=(3, 2, 1)):
        w, h = blk[2], blk[3]
        if any((x + dx, y + dy) in reserved for dx in range(w) for dy in range(h)):
            return None
        p = b.try_any(layers, P(src, blk, x, y, solid=solid))
        if p:
            reserve(x, y, w, h)
            if solid:
                block(x + max(0, w // 2 - (1 if w > 2 else 0)), y + h - 1,
                      1 if w < 3 else 1, 1)
        return p

    # dirt yard is walkable, so only reserve it for scatter purposes
    for (x, y, src, blk, solid) in [
            (39, 5, OBJECTS, HAYSTACK, True), (30, 10, OBJECTS, CHEST, True),
            (39, 11, OBJECTS, BOULDER, True), (30, 5, OBJECTS, BOULDER, True),
            (31, 12, OBJECTS, FLOWER_R, False), (32, 12, OBJECTS, FLOWER_W, False),
            (37, 12, OBJECTS, FLOWER_W, False), (38, 12, OBJECTS, FLOWER_R, False),
            (30, 6, OBJECTS, STUMP, True), (33, 12, OBJECTS, CHEST_OPEN, True),
            (36, 12, OBJECTS, LEAFY, False), (39, 8, OBJECTS, BOULDER, True)]:
        p = b.try_any((3, 2), P(src, blk, x, y, solid=solid))
        if p:
            reserve(x, y, blk[2], blk[3])
            if solid:
                block(x, y, blk[2], blk[3])

    for (x, y, src, blk, solid) in [(27, 7, OBJECTS, TREE_B, True),
                                    (42, 7, OBJECTS, TREE_A, True),
                                    (27, 11, SPRING, BUSH_MED, False),
                                    (41, 13, SPRING, BUSH_MED, False),
                                    (26, 4, SPRING, BUSH_YELLOW, False)]:
        spot(x, y, src, blk, solid)

    # ---------------------------------------------------------- farm plot ---
    px0, py0, px1, py1 = PLOT
    g0, g1 = PLOT_GATE
    fence = []
    for x in range(px0, px1 + 1):
        if g0 <= x <= g1:
            continue
        top = F_TL if x == px0 else (F_TR if x == px1 else F_H)
        if x == g0 - 1: top = F_END_R
        if x == g1 + 1: top = F_END_L
        fence.append((x, py0, top))
        fence.append((x, py1, F_BL if x == px0 else (F_BR if x == px1 else F_H)))
    for y in range(py0 + 1, py1):
        fence.append((px0, y, F_VL))
        fence.append((px1, y, F_VR))
    for (x, y, t) in fence:
        b.try_put(3, P(OBJECTS, (t[0], t[1], 1, 1), x, y, solid=True))
        block(x, y)

    kinds = [CROP_ROWS["squash"], CROP_ROWS["carrot"], CROP_ROWS["potato"],
             CROP_ROWS["berry"], CROP_ROWS["carrot"]]
    sx0, sy0, sx1, sy1 = SOIL_RECT
    for i, y in enumerate(range(sy0, sy1 + 1)):
        kind = kinds[i % len(kinds)]
        stage = [4, 3, 4, 2, 4][i % 5]
        for x in range(sx0, sx1 + 1):
            if rng.random() < 0.08:
                continue
            b.try_put(2, P(PLANTS, (stage, kind, 1, 1), x, y))

    b.try_put(3, P(OBJECTS, BARREL, 16, 21, solid=True));  block(16, 21)
    b.try_put(3, P(OBJECTS, CHEST_OPEN, 7, 21, solid=True)); block(7, 21)
    b.try_put(3, P(OBJECTS, STICK, 8, 27))

    # ----------------------------------------------------------- orchard ----
    for (ox, oy) in [(27, 21), (30, 20), (33, 22), (37, 21), (41, 20),
                     (28, 25), (32, 26), (36, 25), (40, 24),
                     (30, 29), (34, 29), (38, 28), (42, 27), (26, 28)]:
        jx, jy = rng.randint(-1, 1), rng.randint(-1, 1)
        blk = TREE_A if rng.random() < 0.5 else TREE_B
        spot(ox + jx, oy + jy, OBJECTS, blk, solid=True, layers=(3, 2, 1))
    spot(34, 23, OBJECTS, HAYSTACK, solid=True)
    spot(28, 23, OBJECTS, STUMP, solid=True)

    # ------------------------------------------------- gate posts on roads ---
    def stub(cells, y, horizontal=True):
        for (gx, t) in cells:
            if b.try_put(3, P(OBJECTS, (t[0], t[1], 1, 1), gx, y, solid=True)):
                block(gx, y); reserve(gx, y)

    for gy in (5, H - 6):
        stub([(ROAD_X0 - 2, F_END_L), (ROAD_X0 - 1, F_END_R),
              (ROAD_X1 + 1, F_END_L), (ROAD_X1 + 2, F_END_R)], gy)
    for gx in (5, 42):
        for gy in (ROAD_Y0 - 1, ROAD_Y1 + 1):
            if b.try_put(3, P(OBJECTS, (F_POST_L[0], F_POST_L[1], 1, 1), gx, gy, solid=True)):
                block(gx, gy)

    # ------------------------------------------------------- open meadow ----
    clusters = [(18, 4), (18, 12), (6, 13), (16, 7), (26, 15), (12, 14),
                (4, 19), (19, 21), (18, 27), (7, 31), (15, 31), (25, 31),
                (44, 17), (43, 25), (4, 6), (44, 31), (20, 15), (8, 16),
                (26, 10), (20, 9), (44, 9), (14, 18), (5, 22), (4, 31),
                (9, 13), (14, 11), (20, 24), (20, 27), (28, 16), (33, 16),
                (39, 16), (28, 4), (44, 21), (4, 10), (13, 19), (22, 12),
                (26, 22), (12, 31), (23, 32), (19, 24), (19, 28), (16, 22),
                (16, 26), (8, 14), (12, 12), (16, 15), (21, 13), (27, 13),
                (33, 15), (39, 14), (44, 5), (44, 13), (44, 27), (4, 13),
                (4, 25), (9, 31), (18, 31), (28, 31), (36, 31), (43, 31)]
    def sprinkle(cx, cy, tries, choices, spread=2):
        for _ in range(tries):
            x, y = cx + rng.randint(-spread, spread), cy + rng.randint(-spread, spread)
            src, blk, solid = rng.choice(choices)
            if spot(x, y, src, blk, solid=solid):
                return True
        return False

    BIG   = [(SPRING, BUSH_DARK, False), (SPRING, BUSH_YELLOW, False)]
    SMALL = [(SPRING, BUSH_MED, False), (SPRING, SHRUB_YELLOW, False)]
    TREES = [(OBJECTS, TREE_A, True), (OBJECTS, TREE_B, True)]

    for (cx, cy) in clusters:
        if rng.random() < 0.55:
            sprinkle(cx, cy, 5, BIG)
        if rng.random() < 0.40:
            sprinkle(cx, cy, 6, TREES)
        for _ in range(rng.randint(2, 4)):
            sprinkle(cx, cy, 6, SMALL, spread=3)

    for (x, y, blk) in [(19, 4, TREE_B), (5, 12, TREE_A), (20, 30, TREE_B),
                        (4, 27, TREE_A), (25, 26, TREE_A), (19, 8, TREE_A),
                        (44, 12, TREE_B), (44, 4, TREE_A), (4, 15, TREE_B),
                        (8, 13, TREE_A), (13, 13, TREE_B), (18, 13, TREE_A),
                        (4, 20, TREE_B), (19, 17, TREE_A)]:
        spot(x, y, OBJECTS, blk, solid=True)

    # wildflower meadows to break up the open grass
    for (mx, my) in [(7, 15), (15, 15), (27, 6), (28, 19), (20, 12), (43, 18)]:
        for _ in range(rng.randint(4, 7)):
            fx, fy = mx + rng.randint(-2, 2), my + rng.randint(-1, 2)
            spot(fx, fy, OBJECTS, FLOWER_W if rng.random() < 0.5 else FLOWER_R)
        sprinkle(mx, my, 4, SMALL, spread=3)

    for (x, y, blk) in [(4, 7, TREE_B), (16, 5, TREE_A), (7, 12, TREE_B),
                        (14, 12, TREE_A), (4, 4, TREE_A)]:
        spot(x, y, OBJECTS, blk, solid=True)
    spot(6, 4, OBJECTS, STUMP, solid=True)
    # break up the pond's rectangular silhouette with foliage on its corners
    for (x, y, src, blk, solid) in [(4, 3, OBJECTS, TREE_A, True),
                                    (17, 4, OBJECTS, TREE_B, True),
                                    (4, 11, SPRING, BUSH_DARK, False),
                                    (16, 11, SPRING, BUSH_YELLOW, False),
                                    (7, 3, OBJECTS, STUMP, True),
                                    (17, 7, SPRING, BUSH_ROCKBASE, False),
                                    (18, 10, OBJECTS, BOULDER, True),
                                    (17, 12, OBJECTS, BOULDER, True),
                                    (3, 13, SPRING, BUSH_MED, False),
                                    (13, 13, SPRING, BUSH_MED, False)]:
        spot(x, y, src, blk, solid=solid)

    # grass islet inside the pond
    ix, iy = ISLET_CELL
    if all((ix + dx, iy + dy) in water for dx in range(2) for dy in range(2)):
        b.try_put(2, P(SPRING, ISLET, ix, iy))
        block(ix, iy, 2, 2)

    for c in water:
        blocked.add(c)
    return b, blocked


def build_decor(path, soil, water, board):
    rng = random.Random(SEED + 7)
    decor = {}
    taken = set()
    for p in board.items:
        if p["src"] == SPRING and (p["ax"], p["ay"]) == ISLET[:2]:
            for dy in range(ISLET[3]):
                for dx in range(ISLET[2]):
                    taken.add((p["x"] + dx, p["y"] + dy))

    def ok(x, y):
        return (BORDER <= x < W - BORDER and BORDER <= y < H - BORDER
                and (x, y) not in decor and (x, y) not in taken)

    for _ in range(2600):
        x, y = rng.randrange(W), rng.randrange(H)
        if not ok(x, y) or (x, y) in water or (x, y) in soil or (x, y) in path:
            continue
        r = rng.random()
        if r < 0.52:   decor[(x, y)] = rng.choice(GRASS_TUFT)
        elif r < 0.80: decor[(x, y)] = rng.choice(FLOWERS)
        elif r < 0.92: decor[(x, y)] = rng.choice(PEBBLES)
        else:          decor[(x, y)] = rng.choice(DIRT_PATCH)

    for _ in range(150):
        x, y = rng.randrange(W), rng.randrange(H)
        if (x, y) in path and ok(x, y) and rng.random() < 0.45:
            decor[(x, y)] = rng.choice(PEBBLES)

    # reeds only where the tile below is also water, so they stay in the pond
    for c in sorted(water):
        x, y = c
        if c in taken or (x, y + 1) not in water:
            continue
        shore = any((x + dx, y + dy) not in water
                    for dx, dy in ((1, 0), (-1, 0), (0, -1)))
        if shore and rng.random() < 0.35:
            decor[c] = rng.choice(REEDS)
        elif not shore and rng.random() < 0.08:
            decor[c] = rng.choice(WATER_ROCK)
    return decor
