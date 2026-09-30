"""Write the Godot 4.7 TileSet, scenes, script and project settings."""
import base64, os, struct
from PIL import Image
import numpy as np

from catalog import *
from layout import W, H, build_sets, build_ground, water_corner_fixes
from props import build_props, build_decor
from tiledef import (MULTI, YSORT, COLL, texture_origin, terrain_assignments, BIT_NAMES,
                     T_GRASS, T_PATH, T_SOIL, T_WATER, ANIM, ANIM_FRAME_CELLS)

T = 16
PROJ = PROJECT

ATLAS_GRID = {SPRING: (9, 20), OBJECTS: (9, 12), PLANTS: (5, 6), ITEMS: (5, 3)}
RES_PATH = {
    SPRING:  "res://Assets/Tiny Wonder Farm Free/tilemaps/spring farm tilemap.png",
    OBJECTS: "res://Assets/tilesets/farm_objects_atlas.png",
    PLANTS:  "res://Assets/Tiny Wonder Farm Free/objects&items/plants free.png",
    ITEMS:   "res://Assets/Tiny Wonder Farm Free/objects&items/items free.png",
}
ATLAS_ID = {SPRING: "1_spring", OBJECTS: "2_objects", PLANTS: "3_plants", ITEMS: "4_items"}


# --------------------------------------------------------------------- assets
def make_padded_objects_atlas():
    dst = os.path.join(PROJ, "Assets/tilesets/farm_objects_atlas.png")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    src = Image.open(os.path.join(PROJ, OBJECTS_SRC)).convert("RGBA")
    out = Image.new("RGBA", (src.width, 192), (0, 0, 0, 0))
    out.paste(src, (0, 0))
    out.save(dst)
    return dst


def atlas_images():
    ims = {}
    for sid in ATLAS_GRID:
        p = os.path.join(PROJ, RES_PATH[sid].replace("res://", ""))
        ims[sid] = Image.open(p).convert("RGBA")
    return ims


def declared_tiles(ims):
    """(src) -> ordered list of (col, row, w, h) for every tile we declare."""
    out = {}
    for sid, (cols, rows) in ATLAS_GRID.items():
        covered = set()
        multi = []
        for (s, c, r), (w, h) in MULTI.items():
            if s != sid:
                continue
            multi.append((c, r, w, h))
            for dy in range(h):
                for dx in range(w):
                    covered.add((c + dx, r + dy))
        a = np.array(ims[sid])
        singles = []
        for r in range(rows):
            for c in range(cols):
                if (c, r) in covered or (sid, c, r) in ANIM_FRAME_CELLS:
                    continue
                cell = a[r * T:(r + 1) * T, c * T:(c + 1) * T]
                if cell.shape[0] < T or cell.shape[1] < T:
                    continue
                if (cell[:, :, 3] > 8).sum() == 0:
                    continue
                singles.append((c, r, 1, 1))
        out[sid] = sorted(multi + singles, key=lambda t: (t[1], t[0]))
    return out


# -------------------------------------------------------------------- TileSet
def emit_tileset(tiles):
    terr = terrain_assignments()
    L = []
    L.append('[gd_resource type="TileSet" format=3]')
    L.append("")
    for sid in sorted(ATLAS_GRID):
        L.append(f'[ext_resource type="Texture2D" path="{RES_PATH[sid]}" id="{ATLAS_ID[sid]}"]')
    L.append("")
    for sid in sorted(ATLAS_GRID):
        L.append(f'[sub_resource type="TileSetAtlasSource" id="Atlas_{sid}"]')
        L.append(f'texture = ExtResource("{ATLAS_ID[sid]}")')
        L.append("texture_region_size = Vector2i(16, 16)")
        for (c, r, w, h) in tiles[sid]:
            if (w, h) != (1, 1):
                L.append(f"{c}:{r}/size_in_atlas = Vector2i({w}, {h})")
            if (sid, c, r) in ANIM:
                cols, sep, speed = ANIM[(sid, c, r)]
                L.append(f"{c}:{r}/animation_columns = {cols}")
                L.append(f"{c}:{r}/animation_separation = Vector2i({sep[0]}, {sep[1]})")
                L.append(f"{c}:{r}/animation_speed = {speed}")
                L.append(f"{c}:{r}/animation_frame_0/duration = 1.0")
                L.append(f"{c}:{r}/animation_frame_1/duration = 1.0")
            L.append(f"{c}:{r}/0 = 0")
            if (w, h) != (1, 1):
                ox, oy = texture_origin(w, h)
                L.append(f"{c}:{r}/0/texture_origin = Vector2i({ox}, {oy})")
            ys = YSORT.get((sid, c, r), 0)
            if ys:
                L.append(f"{c}:{r}/0/y_sort_origin = {ys}")
            for i, (bx0, by0, bx1, by1) in enumerate(COLL.get((sid, c, r), [])):
                x0, y0, x1, y1 = bx0 - 8, by0 - 8, bx1 - 8, by1 - 8
                pts = f"{x0}, {y0}, {x1}, {y0}, {x1}, {y1}, {x0}, {y1}"
                L.append(f"{c}:{r}/0/physics_layer_0/polygon_{i}/points = PackedVector2Array({pts})")
            if (sid, c, r) in terr:
                tid, bits = terr[(sid, c, r)]
                L.append(f"{c}:{r}/0/terrain_set = 0")
                L.append(f"{c}:{r}/0/terrain = {tid}")
                for name in BIT_NAMES:
                    L.append(f"{c}:{r}/0/terrains_peering_bit/{name} = {bits[name]}")
        L.append("")
    L.append("[resource]")
    L.append("physics_layer_0/collision_layer = 2")
    L.append("physics_layer_0/collision_mask = 1")
    L.append("terrain_set_0/mode = 0")
    for i, (name, col) in enumerate([("Grass", "0.45, 0.72, 0.26, 1"),
                                     ("Dirt Path", "0.96, 0.71, 0.4, 1"),
                                     ("Tilled Soil", "0.84, 0.53, 0.31, 1"),
                                     ("Water", "0.51, 0.92, 0.81, 1")]):
        L.append(f'terrain_set_0/terrain_{i}/name = "{name}"')
        L.append(f"terrain_set_0/terrain_{i}/color = Color({col})")
    for sid in sorted(ATLAS_GRID):
        L.append(f'sources/{sid} = SubResource("Atlas_{sid}")')
    return "\n".join(L) + "\n"


# --------------------------------------------------------------- tile_map_data
def encode_layer(cells):
    """cells: iterable of (x, y, source_id, atlas_x, atlas_y, alternative)"""
    buf = struct.pack("<H", 0)
    for (x, y, sid, ax, ay, alt) in cells:
        buf += struct.pack("<hhHHHH", x, y, sid, ax, ay, alt)
    return base64.b64encode(buf).decode("ascii")


# ----------------------------------------------------------------- main scene
def emit_main(base, over, fixes, decor, board):
    layers = {}
    layers["Ground"] = [(x, y, SPRING, a, b, 0) for (x, y), (a, b) in base.items()]
    layers["GroundTop"] = [(x, y, SPRING, a, b, 0) for (x, y), (a, b) in over.items()]
    layers["Shoreline"] = [(x, y, SPRING, a, b, 0) for (x, y, (a, b)) in fixes]
    layers["Decor"] = [(x, y, SPRING, a, b, 0) for (x, y), (a, b) in decor.items()]
    for i in range(4):
        layers[f"Props{i}"] = []
    for p in board.items:
        layers[f"Props{p['layer']}"].append(
            (p["x"], p["y"], p["src"], p["ax"], p["ay"], 0))

    L = []
    L.append('[gd_scene format=4 uid="uid://i8tvan2ybu25"]')
    L.append("")
    L.append('[ext_resource type="TileSet" path="res://Assets/tilesets/farm_tileset.tres" id="1_tileset"]')
    L.append('[ext_resource type="PackedScene" path="res://Scenes/player.tscn" id="2_player"]')
    L.append("")
    L.append('[sub_resource type="RectangleShape2D" id="Wall_H"]')
    L.append(f"size = Vector2({W * T}, {BORDER_PX})")
    L.append("")
    L.append('[sub_resource type="RectangleShape2D" id="Wall_V"]')
    L.append(f"size = Vector2({BORDER_PX}, {H * T})")
    L.append("")
    L.append('[node name="World" type="Node2D"]')
    L.append("y_sort_enabled = true")
    L.append("")
    for name, cells in layers.items():
        z = {"Ground": -2, "GroundTop": -2, "Shoreline": -1, "Decor": -1}.get(name)
        L.append(f'[node name="{name}" type="TileMapLayer" parent="."]')
        if z is not None:
            L.append(f"z_index = {z}")
        else:
            L.append("y_sort_enabled = true")
        L.append(f'tile_map_data = PackedByteArray("{encode_layer(cells)}")')
        L.append('tile_set = ExtResource("1_tileset")')
        # GroundTop carries the water tiles, whose polygons keep the player dry
        if name in ("Ground", "Shoreline", "Decor"):
            L.append("collision_enabled = false")
        L.append("")

    # invisible fence around the playable area, in case the forest has a gap
    L.append('[node name="Bounds" type="StaticBody2D" parent="."]')
    L.append("collision_layer = 2")
    L.append("collision_mask = 0")
    L.append("")
    px0, py0 = BORDER_PX, BORDER_PX
    px1, py1 = W * T - BORDER_PX, H * T - BORDER_PX
    for nm, shape, pos in [
            ("Top", "Wall_H", (W * T / 2, py0 - BORDER_PX / 2)),
            ("Bottom", "Wall_H", (W * T / 2, py1 + BORDER_PX / 2)),
            ("Left", "Wall_V", (px0 - BORDER_PX / 2, H * T / 2)),
            ("Right", "Wall_V", (px1 + BORDER_PX / 2, H * T / 2))]:
        L.append(f'[node name="{nm}" type="CollisionShape2D" parent="Bounds"]')
        L.append(f"position = Vector2({pos[0]:g}, {pos[1]:g})")
        L.append(f'shape = SubResource("{shape}")')
        L.append("")

    L.append('[node name="Player" parent="." instance=ExtResource("2_player")]')
    L.append(f"position = Vector2({PLAYER_START[0]}, {PLAYER_START[1]})")
    L.append("")
    return "\n".join(L)


BORDER_PX = 3 * T
PLAYER_START = (552, 186)


# --------------------------------------------------------------- player scene
def emit_player():
    frames = []      # (id, x, y)
    anims = []
    CH = "res://Assets/Tiny Wonder Farm Free/characters/main character/walk and idle.png"

    def strip(name, row, cols, speed, ):
        ids = []
        for c in cols:
            fid = f"F{row}_{c}"
            frames.append((fid, c * 24, row * 24))
            ids.append(fid)
        anims.append((name, ids, speed))

    strip("idle_left", 0, [0, 1], 3.0)
    strip("idle_right", 0, [2, 3], 3.0)
    strip("walk_left", 1, list(range(8)), 12.0)
    strip("walk_right", 2, list(range(8)), 12.0)

    L = []
    L.append('[gd_scene format=3 uid="uid://ejfipyhqesjv"]')
    L.append("")
    L.append('[ext_resource type="Script" path="res://Scripts/player.gd" id="1_script"]')
    L.append(f'[ext_resource type="Texture2D" path="{CH}" id="2_sheet"]')
    L.append("")
    for fid, x, y in frames:
        L.append(f'[sub_resource type="AtlasTexture" id="{fid}"]')
        L.append('atlas = ExtResource("2_sheet")')
        L.append(f"region = Rect2({x}, {y}, 24, 24)")
        L.append("")
    L.append('[sub_resource type="SpriteFrames" id="PlayerFrames"]')
    parts = []
    for (name, ids, speed) in anims:
        fr = ", ".join('{\n"duration": 1.0,\n"texture": SubResource("%s")\n}' % i for i in ids)
        parts.append('{\n"frames": [%s],\n"loop": true,\n"name": &"%s",\n"speed": %.1f\n}'
                     % (fr, name, speed))
    L.append("animations = [" + ", ".join(parts) + "]")
    L.append("")
    L.append('[sub_resource type="RectangleShape2D" id="PlayerBody"]')
    L.append("size = Vector2(12, 6)")
    L.append("")
    L.append('[node name="Player" type="CharacterBody2D"]')
    L.append("y_sort_enabled = true")
    L.append("collision_layer = 1")
    L.append("collision_mask = 2")
    L.append('script = ExtResource("1_script")')
    L.append("")
    L.append('[node name="Sprite" type="AnimatedSprite2D" parent="."]')
    L.append("position = Vector2(0, -10)")
    L.append('sprite_frames = SubResource("PlayerFrames")')
    L.append('animation = &"idle_right"')
    L.append('autoplay = "idle_right"')
    L.append("")
    L.append('[node name="CollisionShape2D" type="CollisionShape2D" parent="."]')
    L.append("position = Vector2(0, -2)")
    L.append('shape = SubResource("PlayerBody")')
    L.append("")
    L.append('[node name="Camera2D" type="Camera2D" parent="."]')
    L.append("limit_left = 0")
    L.append("limit_top = 0")
    L.append(f"limit_right = {W * T}")
    L.append(f"limit_bottom = {H * T}")
    L.append("limit_smoothed = true")
    L.append("position_smoothing_enabled = true")
    L.append("position_smoothing_speed = 6.0")
    L.append("")
    return "\n".join(L)


PLAYER_GD = '''extends CharacterBody2D

## Top-down farm hand.  The Tiny Wonder sheet only has left/right facings,
## so vertical movement keeps whichever side the player last faced.

@export var speed: float = 78.0

@onready var _sprite: AnimatedSprite2D = $Sprite

var _facing: String = "right"


func _physics_process(_delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = direction * speed
	move_and_slide()

	if direction.x > 0.1:
		_facing = "right"
	elif direction.x < -0.1:
		_facing = "left"

	var wanted := ("walk_" if direction != Vector2.ZERO else "idle_") + _facing
	if _sprite.animation != wanted:
		_sprite.play(wanted)
'''


def write(path, text):
    full = os.path.join(PROJ, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)
    return full


if __name__ == "__main__":
    make_padded_objects_atlas()
    ims = atlas_images()
    tiles = declared_tiles(ims)
    for sid in sorted(tiles):
        print(f"source {sid}: {len(tiles[sid])} tiles "
              f"({sum(1 for t in tiles[sid] if t[2:] != (1,1))} multi-cell)")

    path, soil, water = build_sets()
    base, over = build_ground(path, soil, water)
    board, blocked = build_props(path, soil, water)
    decor = build_decor(path, soil, water, board)

    print(write("Assets/tilesets/farm_tileset.tres", emit_tileset(tiles)))
    print(write("Scenes/main.tscn", emit_main(base, over, water_corner_fixes(water), decor, board)))
    print(write("Scenes/player.tscn", emit_player()))
    print(write("Scripts/player.gd", PLAYER_GD))
