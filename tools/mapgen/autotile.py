"""Generic 8-neighbour autotiler for the Tiny Wonder terrain sets."""

SIDE_ROLE = {
    (0, 1, 0, 1): "NW", (0, 1, 1, 1): "N",  (0, 1, 1, 0): "NE",
    (1, 1, 0, 1): "W",                      (1, 1, 1, 0): "E",
    (1, 0, 0, 1): "SW", (1, 0, 1, 1): "S",  (1, 0, 1, 0): "SE",
    (0, 0, 1, 1): "hM", (0, 0, 0, 1): "hL", (0, 0, 1, 0): "hR",
    (1, 1, 0, 0): "vM", (0, 1, 0, 0): "vT", (1, 0, 0, 0): "vB",
    (0, 0, 0, 0): "dot",
}

def pick(cells, x, y, table):
    """Return the atlas coord for terrain cell (x, y) given the occupied set."""
    inn = lambda dx, dy: (x + dx, y + dy) in cells
    N, S, W, E = inn(0, -1), inn(0, 1), inn(-1, 0), inn(1, 0)
    if not (N and S and W and E):
        role = SIDE_ROLE[(int(N), int(S), int(W), int(E))]
        return table.get(role, table["C"])

    missing = []
    if not inn(-1, -1): missing.append("NW")
    if not inn(1, -1):  missing.append("NE")
    if not inn(-1, 1):  missing.append("SW")
    if not inn(1, 1):   missing.append("SE")
    if not missing:
        return table["C"]
    if len(missing) == 1:
        return table.get("i" + missing[0], table["C"])
    key = "+".join("i" + m for m in missing)
    if key in table:
        return table[key]
    # adjacent pair?
    for pair in ("iSW+iSE", "iNW+iSW", "iNW+iNE", "iNE+iSE"):
        want = set(pair.split("+"))
        if want <= {"i" + m for m in missing} and pair in table:
            return table[pair]
    return table.get("i" + missing[0], table["C"])
