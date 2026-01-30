from dataclasses import dataclass

@dataclass(frozen=True)
class MapData:
    grid: list[list[int]]
    castle: tuple[int, int]
    spawns: dict[str, tuple[int, int]]

def gen_plus_map(w: int, h: int, arm: int) -> MapData:
    if w < 7 or h < 7:
        raise ValueError("w и h должны быть >= 7")
    if arm < 1:
        raise ValueError("arm должен быть >= 1")

    cx = w // 2
    cy = h // 2

    grid = [[1 for _ in range(w)] for __ in range(h)]

    x0 = max(0, cx - arm)
    x1 = min(w - 1, cx + arm)
    y0 = max(0, cy - arm)
    y1 = min(h - 1, cy + arm)

    for y in range(h):
        for x in range(w):
            in_vert = x0 <= x <= x1
            in_horz = y0 <= y <= y1
            if in_vert or in_horz:
                grid[y][x] = 0

    castle = (cx, cy)
    grid[cy][cx] = 0

    spawns = {
        "top": (cx, h - 1),
        "bottom": (cx, 0),
        "left": (0, cy),
        "right": (w - 1, cy),
    }

    for k, (sx, sy) in spawns.items():
        grid[sy][sx] = 0

    return MapData(grid=grid, castle=castle, spawns=spawns)
