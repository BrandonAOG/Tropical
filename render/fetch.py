"""
Download GFS subsets from NOAA NOMADS and load them into plain numpy arrays.

The grib_filter CGI lets us request only the variables/levels/bbox we need, so
each forecast hour is a few MB. GRIB decoding uses cfgrib (needs the eccodes
system library: `apt install libeccodes-dev` or `conda install eccodes`).
"""
from __future__ import annotations

import datetime as dt
import logging
import time
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import requests

from config import (MODEL, NOMADS_DIR, NOMADS_FILE, NOMADS_FILTER, NOMADS_IDX,
                    PARAMS)

log = logging.getLogger("fetch")

# cfgrib short names for each (VAR, LEVEL) pair we ask NOMADS for.
CFGRIB_NAMES = {
    ("HGT", "500_mb"): "gh",
    ("HGT", "850_mb"): "gh",
    ("HGT", "1000_mb"): "gh",
    ("ABSV", "500_mb"): "absv",
    ("PRMSL", "mean_sea_level"): "prmsl",
    ("APCP", "surface"): "tp",
    ("TMP", "850_mb"): "t",
    ("TMP", "2_m_above_ground"): "t2m",
    ("UGRD", "850_mb"): "u",
    ("VGRD", "850_mb"): "v",
    ("UGRD", "10_m_above_ground"): "u10",
    ("VGRD", "10_m_above_ground"): "v10",
    ("PWAT", "entire_atmosphere_\\(considered_as_a_single_layer\\)"): "pwat",
    ("CAPE", "surface"): "cape",
}


def latest_available_run(now: dt.datetime | None = None,
                         session: requests.Session | None = None) -> dt.datetime:
    """Newest GFS cycle whose f000 index file exists on NOMADS."""
    now = now or dt.datetime.now(dt.timezone.utc)
    session = session or requests.Session()
    candidate = now - dt.timedelta(hours=MODEL["min_age_hours"])
    candidate = candidate.replace(minute=0, second=0, microsecond=0)
    candidate = candidate.replace(hour=(candidate.hour // 6) * 6)
    for _ in range(8):  # look back up to 2 days
        url = NOMADS_IDX.format(ymd=candidate.strftime("%Y%m%d"),
                                hh=candidate.strftime("%H"))
        try:
            r = session.head(url, timeout=20)
            if r.status_code == 200:
                return candidate
        except requests.RequestException as e:
            log.warning("HEAD %s failed: %s", url, e)
        candidate -= dt.timedelta(hours=6)
    raise RuntimeError("No GFS run found on NOMADS in the last 48 h")


def all_fetch_pairs(param_ids: list[str]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for pid in param_ids:
        pairs.update(PARAMS[pid]["fetch"])
    return pairs


def build_filter_url(run: dt.datetime, fhr: int, pairs: set[tuple[str, str]],
                     bbox: tuple[float, float, float, float]) -> str:
    """grib_filter URL for one forecast hour, all variables, one bounding box."""
    lon0, lon1, lat0, lat1 = bbox
    # grib_filter wants 0..360 longitudes
    left = lon0 % 360
    right = lon1 % 360
    q = {
        "dir": NOMADS_DIR.format(ymd=run.strftime("%Y%m%d"), hh=run.strftime("%H")),
        "file": NOMADS_FILE.format(hh=run.strftime("%H"), fhr=fhr),
        "subregion": "",
        "leftlon": f"{left:g}",
        "rightlon": f"{right:g}",
        "toplat": f"{lat1:g}",
        "bottomlat": f"{lat0:g}",
    }
    for var, lev in pairs:
        q[f"var_{var}"] = "on"
        q[f"lev_{lev}"] = "on"
    return NOMADS_FILTER + "?" + urlencode(q, safe="\\()")


def download(url: str, dest: Path, session: requests.Session, retries: int = 4) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > 1000:
                dest.write_bytes(r.content)
                return dest
            log.warning("GET %s -> %s (%d bytes)", url[:80], r.status_code, len(r.content))
        except requests.RequestException as e:
            log.warning("GET failed (%s): %s", attempt, e)
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Failed to download {url}")


class Fields(dict):
    """A dict of name -> 2D numpy array, plus shared lon/lat 1-D coordinates."""
    lon: np.ndarray
    lat: np.ndarray


def load_grib(path: Path) -> Fields:
    """Read every message in a GRIB2 file into a Fields dict keyed by cfgrib
    short name (with the level appended when the same name occurs at several
    levels, e.g. gh500 / gh850 / gh1000)."""
    import cfgrib  # imported lazily so --synthetic mode works without eccodes

    out = Fields()
    datasets = cfgrib.open_datasets(str(path), backend_kwargs={"indexpath": ""})
    lon = lat = None
    for ds in datasets:
        if lon is None:
            lon = ds["longitude"].values
            lat = ds["latitude"].values
        for name, da in ds.data_vars.items():
            arr = da.values
            # cfgrib may stack multiple levels in one variable
            if "isobaricInhPa" in da.dims:
                for i, lev in enumerate(da["isobaricInhPa"].values):
                    out[f"{name}{int(lev)}"] = np.asarray(arr[i], dtype=float)
            else:
                lev = da.coords.get("isobaricInhPa")
                key = f"{name}{int(lev.values)}" if lev is not None and lev.ndim == 0 else name
                out[key] = np.asarray(arr, dtype=float)
    if lon is None:
        raise RuntimeError(f"No data in {path}")
    lon = np.where(lon > 180, lon - 360, lon)
    order = np.argsort(lon)
    lon = lon[order]
    for k in list(out):
        out[k] = out[k][:, order]
    out.lon, out.lat = lon, lat
    return out


def synthetic_fields(fhr: int, bbox, n=(120, 200)) -> Fields:
    """Fake but physically plausible-looking fields for testing the plots
    without network access to NOMADS."""
    lon0, lon1, lat0, lat1 = bbox
    lat = np.linspace(lat1, lat0, n[0])
    lon = np.linspace(lon0, lon1, n[1])
    LON, LAT = np.meshgrid(lon, lat)
    t = fhr / 24.0
    wave = np.sin(np.radians(LON * 3 + t * 40)) * np.cos(np.radians((LAT - 35) * 4))
    out = Fields()
    out.lon, out.lat = lon, lat
    out["gh500"] = 5700 - 12 * (LAT - 25) + 120 * wave
    out["gh850"] = 1500 - 4 * (LAT - 25) + 40 * wave
    out["gh1000"] = 100 + 20 * wave
    out["absv"] = (2e-5 + 1.5e-4 * np.clip(wave, 0, 1) ** 2 * np.sin(np.radians(LON * 6))**2)
    out["prmsl"] = 101300 - 1200 * wave + 200 * np.cos(np.radians(LAT * 5))
    out["tp"] = 15 * np.clip(-wave, 0, 1) ** 3 * (np.random.default_rng(fhr).random(LON.shape) * 0.5 + 0.5)
    out["t850"] = 293 - 0.5 * (LAT - 10) + 5 * wave
    out["u850"] = 10 * wave + 5
    out["v850"] = 8 * np.cos(np.radians(LON * 3 + t * 40))
    out["t2m"] = 303 - 0.7 * (LAT - 10) + 4 * wave
    out["u10"] = 6 * wave + 3
    out["v10"] = 5 * np.cos(np.radians(LON * 3 + t * 40))
    out["pwat"] = 45 - 0.8 * (LAT - 10) + 12 * -wave
    out["cape"] = 3000 * np.clip(-wave, 0, 1) ** 2 * np.clip((40 - LAT) / 30, 0, 1)
    return out
