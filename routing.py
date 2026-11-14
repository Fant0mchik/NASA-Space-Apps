import heapq
import json
import math
from pathlib import Path

import numpy as np


def astar(blocked, penalty, start, finish, dx, dy):
    if blocked[start] or blocked[finish]:
        raise ValueError('An endpoint is inside hazardous or missing terrain')
    costs = {start: 0.0}
    parents = {}
    queue = [(0.0, 0.0, start)]
    while queue:
        _, cost, current = heapq.heappop(queue)
        if cost != costs[current]:
            continue
        if current == finish:
            path = [current]
            while current in parents:
                current = parents[current]
                path.append(current)
            return path[::-1]
        row, col = current
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nr, nc = row + dr, col + dc
            if not (0 <= nr < blocked.shape[0] and 0 <= nc < blocked.shape[1]):
                continue
            if blocked[nr, nc] or blocked[row, nc] or blocked[nr, col]:
                continue
            neighbor = (nr, nc)
            distance = math.hypot(dx[col] - dx[nc], dy[row] - dy[nr])
            candidate = cost + distance * (1 + (penalty[current] + penalty[neighbor]) / 2)
            if candidate < costs.get(neighbor, math.inf):
                costs[neighbor] = candidate
                parents[neighbor] = current
                estimate = math.hypot(dx[nc] - dx[finish[1]], dy[nr] - dy[finish[0]])
                heapq.heappush(queue, (candidate + estimate, candidate, neighbor))
    raise ValueError('No route satisfies the terrain limits')


def plan_route(directory, step, start, finish, max_slope=15):
    directory = Path(directory)
    meta = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    col, row, width, height = meta['pixel_window']
    a, b, c, d, e, f = meta['source_transform']
    if b or d or a <= 0 or e >= 0:
        raise ValueError('Routing requires a north-up projected DEM')
    if step < 1 or not 0 < max_slope < 90:
        raise ValueError('Invalid routing step or slope limit')
    dem = np.full((height, width), np.nan, dtype=np.float32)
    for sector in meta['sectors']:
        path = (directory / sector['file']).resolve()
        if path.parent != directory.resolve():
            raise ValueError('Sector must be inside the package directory')
        with np.load(path, allow_pickle=False) as data:
            values = np.where(data['valid'].astype(bool), data['height'], np.nan)
        sy, sx = sector['source_row'] - row, sector['source_col'] - col
        dem[sy:sy + values.shape[0], sx:sx + values.shape[1]] = values
    xs = np.unique(np.r_[np.arange(0, width, step), width - 1])
    ys = np.unique(np.r_[np.arange(0, height, step), height - 1])
    surface = dem[np.ix_(ys, xs)].astype(float)
    slope = np.zeros((len(ys) - 1, len(xs) - 1))
    relief = np.zeros_like(slope)
    for iy, (top, bottom) in enumerate(zip(ys[:-1], ys[1:])):
        lo, hi = max(0, top - 1), min(height, bottom + 2)
        strip = dem[lo:hi]
        gy, gx = np.gradient(strip, abs(e), a)
        grade = np.hypot(gx, gy)[top-lo:bottom-lo+1]
        grade = np.nan_to_num(grade, nan=np.inf, posinf=np.inf)
        for ix, (left, right) in enumerate(zip(xs[:-1], xs[1:])):
            block = dem[top:bottom+1, left:right+1]
            slope[iy, ix] = np.max(grade[:, left:right+1])
            relief[iy, ix] = np.ptp(block) if np.isfinite(block).all() else np.inf
    center_z = (surface[:-1, :-1] + surface[1:, :-1] +
                surface[:-1, 1:] + surface[1:, 1:]) / 4
    blocked = ~np.isfinite(center_z) | (slope > math.tan(math.radians(max_slope)))
    radius = max(1, round(2000 / (step * min(a, abs(e)))))
    padded = np.pad(center_z, radius, mode='edge')
    total = np.zeros_like(center_z)
    count = np.zeros_like(center_z)
    for oy in range(2 * radius + 1):
        for ox in range(2 * radius + 1):
            nearby = padded[oy:oy+center_z.shape[0], ox:ox+center_z.shape[1]]
            valid = np.isfinite(nearby)
            total += np.where(valid, nearby, 0)
            count += valid
    mean = np.divide(total, count, out=center_z.copy(), where=count > 0)
    depression = np.maximum(0, mean - center_z)
    penalty = 8 * slope + relief / 50 + depression / 30
    dx = c + a * (col + (xs[:-1] + xs[1:]) / 2 + .5)
    dy = f + e * (row + (ys[:-1] + ys[1:]) / 2 + .5)

    def locate(point):
        if len(point) != 2 or not np.isfinite(point).all():
            raise ValueError('Route endpoints must be finite projected X/Y coordinates')
        px, py = (point[0] - c) / a - col - .5, (point[1] - f) / e - row - .5
        if not (xs[0] <= px <= xs[-1] and ys[0] <= py <= ys[-1]):
            raise ValueError('Route endpoint is outside the DEM')
        return (min(len(ys)-2, int(np.searchsorted(ys, py, side='right')-1)),
                min(len(xs)-2, int(np.searchsorted(xs, px, side='right')-1)))

    path = astar(blocked, penalty, locate(start), locate(finish), dx, dy)
    waypoints = np.array([start, *[(dx[x], dy[y]) for y, x in path], finish])
    samples = [waypoints[0]]
    for p, q in zip(waypoints[:-1], waypoints[1:]):
        n = max(1, math.ceil(np.linalg.norm(q-p) / (min(a, abs(e)) * step / 4)))
        samples.extend(p + (q-p) * t / n for t in range(1, n+1))
    xy = np.asarray(samples)
    px, py = (xy[:, 0]-c)/a-col-.5, (xy[:, 1]-f)/e-row-.5
    ix = np.clip(np.searchsorted(xs, px, side='right')-1, 0, len(xs)-2)
    iy = np.clip(np.searchsorted(ys, py, side='right')-1, 0, len(ys)-2)
    u, v = (px-xs[ix])/(xs[ix+1]-xs[ix]), (py-ys[iy])/(ys[iy+1]-ys[iy])
    za, zb, zc, zd = surface[iy, ix], surface[iy, ix+1], surface[iy+1, ix], surface[iy+1, ix+1]
    z = np.where(u+v <= 1, za+(zb-za)*u+(zc-za)*v,
                 zd+(zc-zd)*(1-u)+(zb-zd)*(1-v))
    xyz = np.column_stack((xy, z))
    length = np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum()
    peak = math.degrees(math.atan(max(slope[p] for p in path)))
    return {'coordinates': xyz, 'length_m': float(length), 'max_slope_deg': peak,
            'slope_limit_deg': max_slope, 'step_m': step * max(a, abs(e))}
