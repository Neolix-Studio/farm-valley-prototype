# Farm Valley map generator

These scripts built `Scenes/main.tscn`, `Scenes/player.tscn`, `Scripts/player.gd`
and `Assets/tilesets/farm_tileset.tres` from the Tiny Wonder Farm art.

    cd tools/mapgen
    python3 render.py preview.png 2   # PNG preview of the whole map, no Godot needed
    python3 emit.py                   # (re)write the Godot files

**Re-running `emit.py` overwrites those four files**, so once you start editing the
map in the Godot editor, stop using it — or tweak the generator instead and
regenerate. Everything it produces is ordinary Godot data; nothing depends on
these scripts at runtime.

| file | what it holds |
| --- | --- |
| `catalog.py` | which atlas tile is what (grass, path, soil, water, bushes, fences, house…) |
| `autotile.py` | 8-neighbour tile picker for the terrain sets |
| `layout.py` | the map: roads, yard, farm plot, pond |
| `props.py` | trees, bushes, fences, crops, scatter, collision map |
| `tiledef.py` | per-tile metadata: multi-cell sizes, y-sort pivots, collision, terrains |
| `render.py` | PIL preview that mirrors how Godot draws the scene |
| `emit.py` | writes the `.tres` / `.tscn` / `.gd` files |

Two things worth knowing if you edit the tileset by hand:

* Godot centres a multi-cell tile on its **anchor cell**, so every tile bigger than
  1x1 carries a `texture_origin` of `(-8*(w-1), -8*(h-1))` to make the art sit in the
  block you actually clicked.
* The water tiles have outer corners but **no inner (concave) corners**, so a pond
  with a concave corner shows a hard seam. The generator repairs those corners with
  the grass-patch corner tiles (see `water_corner_fixes` in `layout.py`).
