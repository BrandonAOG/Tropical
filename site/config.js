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
window.WX_ENSEMBLES = [
  { id: "gefs",  name: "GEFS (31 members)",       base: "https://brandonaog.github.io/wx-gefs/" },
  // { id: "ecens", name: "ECMWF ENS (51 members)", base: "https://brandonaog.github.io/wx-ecens/" },
];
// Optional single override for everything (e.g. an R2 bucket URL). Leave "".
window.WX_ASSETS = "";
