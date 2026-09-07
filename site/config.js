// Where each model's images and manifest live. The main repo serves GFS from
// its own Pages site (base ""); every other model comes from its own repo's
// Pages site. Add a line per model repo you create.
window.WX_MODELS = [
  { id: "gfs",   name: "GFS",   base: "" },
  { id: "ecmwf", name: "ECMWF", base: "https://brandonaog.github.io/wx-ecmwf/" },
  { id: "cmc",   name: "CMC",   base: "https://brandonaog.github.io/wx-cmc/" },
  { id: "icon",  name: "ICON",  base: "https://brandonaog.github.io/wx-icon/" },
];
// Ensembles (shown on ensembles.html as a dropdown). Same pattern: one repo each.
// Ensembles are grouped by data source: NOAA's in wx-gefs, ECMWF's in wx-ecens.
// Each model in a shared repo has its own manifest file.
window.WX_ENSEMBLES = [
  { id: "gefs",    name: "GEFS (31 members)",           base: "https://brandonaog.github.io/wx-gefs/",  manifest: "manifest-gefs.json" },
  { id: "aigefs",  name: "AI-GEFS (31 members)",        base: "https://brandonaog.github.io/wx-gefs/",  manifest: "manifest-aigefs.json" },
  { id: "ecens",   name: "ECMWF ENS (51 members)",      base: "https://brandonaog.github.io/wx-ecens/", manifest: "manifest-ecens.json" },
  { id: "aifsens", name: "ECMWF AIFS ENS (51 members)", base: "https://brandonaog.github.io/wx-ecens/", manifest: "manifest-aifsens.json" },
  { id: "geps",    name: "GEPS (21 members)",           base: "https://brandonaog.github.io/wx-geps/",  manifest: "manifest-geps.json" },
];
// Mesoscale (CONUS) models, all in the wx-meso repo.
window.WX_MESOSCALE = [
  { id: "hrrr",    name: "HRRR (3 km, hourly)",        base: "https://brandonaog.github.io/wx-meso/", manifest: "manifest-hrrr.json" },
  { id: "namnest", name: "NAM 3 km nest",              base: "https://brandonaog.github.io/wx-meso/", manifest: "manifest-namnest.json" },
  { id: "nam",     name: "NAM 12 km",                  base: "https://brandonaog.github.io/wx-meso/", manifest: "manifest-nam.json" },
  { id: "nbm",     name: "National Blend (NBM)",       base: "https://brandonaog.github.io/wx-meso/", manifest: "manifest-nbm.json" },
];
// Optional single override for everything (e.g. an R2 bucket URL). Leave "".
window.WX_ASSETS = "";
