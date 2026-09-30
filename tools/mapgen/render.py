"""PIL preview of the generated map, mirroring how Godot will draw it."""
import os
from PIL import Image
from catalog import *
from layout import W, H, build_sets, build_ground, water_corner_fixes
from props import build_props, build_decor

T = 16

def load_atlases(project):
    ims = {}
    for sid, rel in ATLAS_FILES.items():
        p = os.path.join(project, rel)
        if sid == OBJECTS and not os.path.exists(p):
            src = Image.open(os.path.join(project, OBJECTS_SRC)).convert("RGBA")
            pad = Image.new("RGBA", (src.width, 192), (0, 0, 0, 0))
            pad.paste(src, (0, 0)); ims[sid] = pad; continue
        ims[sid] = Image.open(p).convert("RGBA")
    return ims


def render(project, out, show_blocked=False):
    atl = load_atlases(project)
    path, soil, water = build_sets()
    base, over = build_ground(path, soil, water)
    board, blocked = build_props(path, soil, water)
    decor = build_decor(path, soil, water, board)

    img = Image.new("RGBA", (W * T, H * T), (0, 0, 0, 255))

    def blit(src, ax, ay, w, h, cx, cy):
        reg = atl[src].crop((ax * T, ay * T, (ax + w) * T, (ay + h) * T))
        img.alpha_composite(reg, (cx * T, cy * T))

    for (x, y), (ax, ay) in base.items():
        blit(SPRING, ax, ay, 1, 1, x, y)
    for (x, y), (ax, ay) in over.items():
        blit(SPRING, ax, ay, 1, 1, x, y)
    for (x, y, (ax, ay)) in water_corner_fixes(water):
        blit(SPRING, ax, ay, 1, 1, x, y)
    for (x, y), (ax, ay) in decor.items():
        blit(SPRING, ax, ay, 1, 1, x, y)

    for p in sorted(board.items, key=lambda p: (p["sort_y"], p["x"])):
        if p["x"] + p["w"] <= 0 or p["y"] + p["h"] <= 0 or p["x"] >= W or p["y"] >= H:
            continue
        blit(p["src"], p["ax"], p["ay"], p["w"], p["h"], p["x"], p["y"])

    if show_blocked:
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(ov)
        for (x, y) in blocked:
            if 0 <= x < W and 0 <= y < H:
                d.rectangle([x*T, y*T, x*T+T-1, y*T+T-1], fill=(255, 0, 0, 70))
        img.alpha_composite(ov)

    img.convert("RGB").save(out)
    return img, board, blocked


if __name__ == "__main__":
    import sys
    project = PROJECT
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/preview.png"
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    blockmap = len(sys.argv) > 3 and sys.argv[3] == "blocked"
    img, board, blocked = render(project, out, show_blocked=blockmap)
    if scale != 1:
        img.resize((img.width * scale, img.height * scale), Image.NEAREST).convert("RGB").save(out)
    print(f"{out}  map {W}x{H} tiles = {W*T}x{H*T}px, {len(board.items)} props")
