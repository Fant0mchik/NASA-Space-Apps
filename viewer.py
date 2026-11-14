import argparse
import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from rasterio.crs import CRS


def make_mesh(directory, step=32, max_vertices=1_000_000):
    directory = Path(directory)
    meta = json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    if meta.get('format_version') != 1:
        raise ValueError('Unsupported manifest version')
    if step < 1:
        raise ValueError('step must be >= 1')
    crs = CRS.from_wkt(meta['crs_wkt'])
    if not crs.is_projected or abs(crs.linear_units_factor[1] - 1) > 1e-9:
        raise ValueError('This viewer requires a projected DEM in metres; reproject the DEM first')
    if meta['height_unit'].strip().lower() not in ('m', 'meter', 'meters', 'metre', 'metres'):
        raise ValueError('Height values must be in metres')
    col, row, width, height = meta['pixel_window']
    if min(width, height) < 2:
        raise ValueError('At least 2 rows and columns are required')
    # One global sampling grid gives shared vertices across sector boundaries.
    xs = np.unique(np.r_[np.arange(0, width, step), width-1])
    ys = np.unique(np.r_[np.arange(0, height, step), height-1])
    if len(xs)*len(ys) > max_vertices:
        raise ValueError(f'Too many vertices; increase --step (limit {max_vertices:,})')
    z = np.full((len(ys), len(xs)), np.nan)
    cells = np.ones((len(ys)-1, len(xs)-1), dtype=bool)
    records = {(s['sector_x'], s['sector_y']): s for s in meta['sectors']}
    size = meta['sector_size']
    if size < 1:
        raise ValueError('Invalid sector_size')
    for y in range(0, height, size):
        for x in range(0, width, size):
            s = records.get((x//size, y//size))
            if s is None or (s['source_col'], s['source_row']) != (col+x, row+y):
                raise ValueError('Incomplete or inconsistent sector index')
            path = (directory/s['file']).resolve()
            if path.parent != directory.resolve():
                raise ValueError('Sector must be inside the package directory')
            with np.load(path, allow_pickle=False) as data:
                h = data['height']
                valid = data['valid'].astype(bool) & np.isfinite(h)
            expected = (min(size, height-y), min(size, width-x))
            if h.shape != expected or valid.shape != expected:
                raise ValueError(f'Unexpected shape: {path.name}')
            xi = np.flatnonzero((xs >= x) & (xs < x+h.shape[1]))
            yi = np.flatnonzero((ys >= y) & (ys < y+h.shape[0]))
            values = h[np.ix_(ys[yi]-y, xs[xi]-x)].copy()
            values[~valid[np.ix_(ys[yi]-y, xs[xi]-x)]] = np.nan
            z[np.ix_(yi, xi)] = values
            by, bx = np.nonzero(~valid)
            for side_x in ('left', 'right'):
                cx = np.clip(np.searchsorted(xs, bx+x, side=side_x)-1, 0, len(xs)-2)
                for side_y in ('left', 'right'):
                    cy = np.clip(np.searchsorted(ys, by+y, side=side_y)-1, 0, len(ys)-2)
                    cells[cy, cx] = False
    ids = np.arange(z.size).reshape(z.shape)
    a, b = ids[:-1, :-1], ids[:-1, 1:]
    c, d = ids[1:, :-1], ids[1:, 1:]
    cells &= np.isfinite(z[:-1, :-1]) & np.isfinite(z[:-1, 1:])
    cells &= np.isfinite(z[1:, :-1]) & np.isfinite(z[1:, 1:])
    triangles = np.concatenate((np.stack((a[cells], b[cells], c[cells]), axis=1),
                                np.stack((b[cells], d[cells], c[cells]), axis=1)))
    if not len(triangles):
        raise ValueError('No valid surface triangles; try a smaller --step or another area')
    xx, yy = np.meshgrid(xs+col+0.5, ys+row+0.5)
    ta, tb, tc, td, te, tf = meta['source_transform']
    if ta*te-tb*td == 0:
        raise ValueError('Degenerate source transform')
    if ta*te-tb*td < 0:
        triangles = triangles[:, [0, 2, 1]] 
    world_x, world_y = ta*xx+tb*yy+tc, td*xx+te*yy+tf
    used, inverse = np.unique(triangles, return_inverse=True)
    absolute_z = z.ravel()[used]
    origin = [float(world_x.ravel()[used].mean()), float(world_y.ravel()[used].mean()),
              float(absolute_z.min())]
    return {'x': world_x.ravel()[used]-origin[0], 'y': world_y.ravel()[used]-origin[1],
            'z': absolute_z-origin[2], 'absolute_z': absolute_z,
            'triangles': inverse.reshape(-1, 3), 'origin': origin, 'step': step}


def hillshade(mesh):
    """Compute fixed side lighting from triangle normals in metre coordinates."""
    points = np.column_stack((mesh['x'], mesh['y'], mesh['z']))
    first, second, third = mesh['triangles'].T
    normals = np.cross(points[second] - points[first], points[third] - points[first])
    normals /= np.linalg.norm(normals, axis=1, keepdims=True)
    light = np.array([-0.7, 0.7, 0.45])
    light /= np.linalg.norm(light)
    return np.clip(normals @ light, 0, 1)


def export_html(mesh, destination, title='Mars terrain', route=None):
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    triangles = mesh['triangles']
    coordinates = np.column_stack((
        mesh['x'] + mesh['origin'][0], mesh['y'] + mesh['origin'][1], mesh['absolute_z'],
    ))
    face_centers = coordinates[triangles].mean(axis=1)
    fig = go.Figure(go.Mesh3d(
        x=mesh['x'], y=mesh['y'], z=mesh['z'],
        i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2],
        intensity=hillshade(mesh), intensitymode='cell', cmin=0, cmax=1,
        colorscale=[[0, '#38241d'], [1, '#edbe97']],
        flatshading=True, showscale=False,
        customdata=face_centers,
        hovertemplate=('X (projected): %{customdata[0]:.1f} m<br>'
                       'Y (projected): %{customdata[1]:.1f} m<br>'
                       'Elevation: %{customdata[2]:.2f} m<extra></extra>'),
        lighting=dict(ambient=1, diffuse=0, specular=0)))
    if route is not None:
        world = route['coordinates']
        local = world - np.asarray(mesh['origin'])
        local[:, 2] += 30  # Lift the overlay above the rendered terrain to avoid z-fighting.
        fig.add_trace(go.Scatter3d(
            x=local[:, 0], y=local[:, 1], z=local[:, 2], mode='lines',
            line=dict(color='white', width=6, dash='dash'), name='Route',
            customdata=world,
            hovertemplate='X: %{customdata[0]:.1f} m<br>Y: %{customdata[1]:.1f} m<br>'
                          'Elevation: %{customdata[2]:.2f} m<extra>Route</extra>'))
        fig.add_trace(go.Scatter3d(
            x=local[[0, -1], 0], y=local[[0, -1], 1], z=local[[0, -1], 2],
            mode='markers+text', marker=dict(color='#00e676', size=7),
            text=['Start', 'Finish'], textposition='top center', name='Endpoints',
            customdata=world[[0, -1]],
            hovertemplate='X: %{customdata[0]:.1f} m<br>Y: %{customdata[1]:.1f} m<br>'
                          'Elevation: %{customdata[2]:.2f} m<extra>%{text}</extra>'))
        title += (f' · Route {route["length_m"]/1000:.1f} km'
                  f' · Slope limit {route["slope_limit_deg"]:g}° · DEM-based estimate')
    fig.update_layout(
        title=dict(text=f'{title}<br><sup>Step {mesh["step"]} px · {len(mesh["z"]):,} vertices · '
                        f'{len(triangles):,} triangles · Scale 1:1:1 · Drag to orbit, scroll to zoom</sup>'),
        paper_bgcolor='#161a1e', font=dict(color='#ece5dc'),
        margin=dict(l=0, r=0, t=70, b=0),
        scene=dict(aspectmode='data', dragmode='orbit', bgcolor='#161a1e',
                   xaxis=dict(title='Local X (m)', nticks=18), yaxis=dict(title='Local Y (m)', nticks=18),
                   zaxis=dict(title=f'Height above {mesh["origin"][2]:.1f} m'),
                   camera=dict(eye=dict(x=1.4, y=-1.4, z=1.1))))
    html = fig.to_html(include_plotlyjs=True, full_html=True,
                       config={'responsive': True, 'displaylogo': False, 'scrollZoom': True},
                       default_height='100vh')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8') as out:
        out.write(html)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Folder containing manifest.json and .npz files')
    parser.add_argument('--output', type=Path, default=Path('mars_map.html'))
    parser.add_argument('--step', type=int, default=32, help='Sample every N source pixels (default 32)')
    parser.add_argument('--start', nargs=2, type=float, metavar=('X', 'Y'), help='Route start in projected metres')
    parser.add_argument('--finish', nargs=2, type=float, metavar=('X', 'Y'), help='Route finish in projected metres')
    parser.add_argument('--max-slope', type=float, default=15, help='Routing slope limit in degrees (default 15)')
    args = parser.parse_args()
    if (args.start is None) != (args.finish is None):
        parser.error('--start and --finish must be provided together')
    try:
        mesh = make_mesh(args.directory, step=args.step)
        route = None
        if args.start is not None:
            from routing import plan_route
            route = plan_route(args.directory, args.step, args.start, args.finish, args.max_slope)
            print(f'Route: {route["length_m"]/1000:.2f} km; maximum source slope: '
                  f'{route["max_slope_deg"]:.2f} degrees; endpoints: {route["coordinates"][[0, -1]].tolist()}')
        print(export_html(mesh, args.output, route=route))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
