import argparse
import json
import math
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

import numpy as np
import rasterio
from rasterio.windows import Window


def download(url, destination):
    if urlsplit(url).scheme not in ('http', 'https'):
        raise ValueError('Expected an HTTP(S) data URL')
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
        partial = Path(tmp) / 'download'
        with urlopen(url, timeout=60) as response, partial.open('wb') as out:
            if 'text/html' in response.headers.get('Content-Type', ''):
                raise ValueError('URL returned HTML; use the raster download link')
            shutil.copyfileobj(response, out, length=1024 * 1024)
        with rasterio.open(partial) as src:
            if not src.count or not src.crs:
                raise ValueError('Expected a georeferenced raster')
        if destination.exists():
            raise FileExistsError(destination)
        partial.rename(destination)
    return destination


def build(source, output, sector_size=512, height_unit=None,
          pixel_window=None, nodata=None, source_url=None):
    source, output = Path(source), Path(output)
    if output.exists():
        raise FileExistsError(output)
    if not isinstance(sector_size, int) or sector_size < 1:
        raise ValueError('sector_size must be a positive integer')
    if not height_unit or not height_unit.strip():
        raise ValueError('Specify height_unit from the product documentation')
    with rasterio.open(source) as src:
        if src.count != 1 or src.crs is None:
            raise ValueError('Use a single-band, georeferenced numerical DEM')
        if np.dtype(src.dtypes[0]).kind not in 'iuf':
            raise ValueError('DEM must contain real numbers')
        col, row, width, height = pixel_window or (0, 0, src.width, src.height)
        if (not all(isinstance(v, int) for v in (col, row, width, height))
                or min(col, row) < 0 or min(width, height) < 1
                or col + width > src.width or row + height > src.height):
            raise ValueError('Pixel window must be entirely inside the source')
        scale, offset = float(src.scales[0]), float(src.offsets[0])
        if not all(math.isfinite(v) for v in (scale, offset)) or scale == 0:
            raise ValueError('Invalid source scale or offset')
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output.parent) as temp:
            staging = Path(temp) / 'package'
            staging.mkdir()
            records = []
            for y in range(0, height, sector_size):
                for x in range(0, width, sector_size):
                    win = Window(col+x, row+y, min(sector_size, width-x),
                                 min(sector_size, height-y))
                    raw = src.read(1, window=win, masked=True)
                    valid = ~np.ma.getmaskarray(raw) & np.isfinite(raw.data)
                    if nodata is not None:
                        valid &= raw.data != nodata
                    z = raw.data.astype(np.float64) * scale + offset
                    valid &= np.isfinite(z)
                    z[~valid] = np.nan
                    sx, sy = x // sector_size, y // sector_size
                    name = f'sector_{sx}_{sy}.npz'
                    transform = list(src.window_transform(win))[:6]
                    np.savez_compressed(staging / name, height=z, valid=valid,
                                        obstacles=np.zeros(z.shape, dtype=bool),
                                        transform=np.array(transform))
                    records.append({'sector_x': sx, 'sector_y': sy, 'file': name,
                                    'source_col': col+x, 'source_row': row+y,
                                    'shape': list(z.shape), 'transform': transform,
                                    'valid_count': int(valid.sum())})
            manifest = {
                'format_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
                'source': str(source.resolve()), 'source_url': source_url,
                'source_files': src.files, 'crs_wkt': src.crs.to_wkt(),
                'source_transform': list(src.transform)[:6],
                'source_dtype': src.dtypes[0], 'source_nodata': str(src.nodata),
                'nodata_override_raw': str(nodata), 'scale_applied': scale,
                'offset_applied': offset, 'height_unit': height_unit,
                'source_band_unit': src.units[0], 'source_tags': src.tags(),
                'source_band_tags': src.tags(1),
                'pixel_window': [col, row, width, height], 'sector_size': sector_size,
                'resampled': False, 'sectors': records,
                'obstacle_semantics': 'false = not marked; NOT evidence of safety',
            }
            (staging / 'manifest.json').write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False),
                encoding='utf-8')
            if output.exists():
                raise FileExistsError(output)
            staging.rename(output)
    return output / 'manifest.json'


def sector_index(directory):
    directory = Path(directory)
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    return {(s['sector_x'], s['sector_y']): directory / s['file']
            for s in manifest['sectors']}


def load_sector(path):
    with np.load(path, allow_pickle=False) as sector:
        return {name: sector[name] for name in sector.files}


def pixel_center(sector, x, y):
    if not (0 <= y < sector['height'].shape[0] and 0 <= x < sector['height'].shape[1]):
        raise IndexError('Pixel outside sector')
    a, b, c, d, e, f = sector['transform']
    return (a*(x+0.5) + b*(y+0.5) + c, d*(x+0.5) + e*(y+0.5) + f)


def set_obstacle(path, x, y, blocked=True):
    path = Path(path)
    sector = load_sector(path)
    pixel_center(sector, x, y)  
    if not sector['valid'][y, x]:
        raise ValueError('No elevation data at this pixel')
    sector['obstacles'][y, x] = bool(blocked)
    with tempfile.TemporaryDirectory(dir=path.parent) as tmp:
        replacement = Path(tmp) / 'sector.npz'
        np.savez_compressed(replacement, **sector)
        os.replace(replacement, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    fetch = commands.add_parser('download', help='Download a self-contained DEM file')
    fetch.add_argument('url')
    fetch.add_argument('destination', type=Path)
    make = commands.add_parser('build', help='Split a local DEM into native-resolution sectors')
    make.add_argument('source', type=Path)
    make.add_argument('output', type=Path)
    make.add_argument('--sector-size', type=int, default=512)
    make.add_argument('--height-unit', required=True, help='Unit of calibrated elevations, e.g. m')
    make.add_argument('--pixel-window', type=int, nargs=4, metavar=('COL', 'ROW', 'WIDTH', 'HEIGHT'))
    make.add_argument('--nodata', type=float, help='Additional missing-data sentinel in RAW values')
    make.add_argument('--source-url', help='Optional provenance URL')
    args = vars(parser.parse_args())
    command = args.pop('command')
    try:
        print(download(**args) if command == 'download' else build(**args))
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
