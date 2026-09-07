"""
Everything you'd want to tweak lives here: which regions get rendered, which
parameters, how many forecast hours, and how many runs to keep on the site.
"""

SITE_NAME = "WxModels"

# GFS 0.25° from NOAA NOMADS grib_filter (subset by variable/level/bbox so each
# download is a few MB instead of ~500 MB).
NOMADS_FILTER = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"
NOMADS_DIR = "/gfs.{ymd}/{hh}/atmos"
NOMADS_FILE = "gfs.t{hh}z.pgrb2.0p25.f{fhr:03d}"
NOMADS_IDX = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{ymd}/{hh}/atmos/gfs.t{hh}z.pgrb2.0p25.f000.idx"

MODEL = {
    "id": "gfs",
    "name": "GFS",
    "resolution": "0.25°",
    "cycles": [0, 6, 12, 18],
    # GFS f000..f120 lands ~3.5–4h after cycle time. We look this far back to
    # pick the newest cycle that's actually available.
    "min_age_hours": 3.5,
}

# Forecast hours to render. GFS is 3-hourly to 240 h, then 12-hourly to 384 h,
# so 6-hourly to 240 and 12-hourly beyond: 51 frames.
FORECAST_HOURS = list(range(0, 241, 6)) + list(range(252, 361, 12))

# How many runs to keep in site/images (older ones are pruned).
KEEP_RUNS = 2

# Regions: lon/lat bounding box (lon in -180..180). Padding is added on fetch
# so contours don't get clipped at the frame edge.
REGIONS = {
    "conus": {"name": "United States", "bbox": (-126, -66, 23, 50)},
    "natl":  {"name": "North Atlantic", "bbox": (-100, -10, 5, 45)},
    "epac":  {"name": "East Pacific",   "bbox": (-150, -85, 3, 35)},
    "namer": {"name": "North America",  "bbox": (-140, -50, 12, 62)},
    "gulf":  {"name": "Gulf & Florida",  "bbox": (-100, -74, 16, 33)},
    "carib": {"name": "Caribbean",       "bbox": (-92, -55, 7, 28)},
}

# Parameters. `fetch` lists grib_filter var/lev pairs; `plot` is the function
# name in plots.py. `group` drives the sidebar sections in the frontend.
PARAMS = {
    "z500_vort": {
        "name": "500 hPa height & vorticity",
        "group": "Upper air",
        "plot": "plot_z500_vort",
        "fetch": [("HGT", "500_mb"), ("ABSV", "500_mb")],
    },
    "mslp_precip": {
        "name": "MSLP & 6-hr precipitation",
        "group": "Surface",
        "plot": "plot_mslp_precip",
        "fetch": [("PRMSL", "mean_sea_level"), ("APCP", "surface"),
                  ("HGT", "1000_mb"), ("HGT", "500_mb")],
    },
    "t850_wind": {
        "name": "850 hPa temperature & wind",
        "group": "Upper air",
        "plot": "plot_t850_wind",
        "fetch": [("TMP", "850_mb"), ("UGRD", "850_mb"), ("VGRD", "850_mb"),
                  ("HGT", "850_mb")],
    },
    "t2m": {
        "name": "2 m temperature",
        "group": "Surface",
        "plot": "plot_t2m",
        "fetch": [("TMP", "2_m_above_ground"), ("PRMSL", "mean_sea_level")],
    },
    "wind10m": {
        "name": "10 m wind & MSLP",
        "group": "Surface",
        "plot": "plot_wind10m",
        "fetch": [("UGRD", "10_m_above_ground"), ("VGRD", "10_m_above_ground"),
                  ("PRMSL", "mean_sea_level")],
    },
    "pwat": {
        "name": "Precipitable water",
        "group": "Moisture",
        "plot": "plot_pwat",
        "fetch": [("PWAT", "entire_atmosphere_\\(considered_as_a_single_layer\\)"),
                  ("PRMSL", "mean_sea_level")],
    },
    "cape": {
        "name": "Surface CAPE",
        "group": "Severe",
        "plot": "plot_cape",
        "fetch": [("CAPE", "surface"), ("UGRD", "10_m_above_ground"),
                  ("VGRD", "10_m_above_ground")],
    },
}

# Output image size (inches × dpi)
FIG_SIZE = (12, 8)
DPI = 100
