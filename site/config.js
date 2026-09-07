// Where each model's images and manifest live. The main repo serves GFS from
// its own Pages site (base ""); every other model comes from its own repo's
// Pages site. Add a line per model repo you create.
window.WX_MODELS = [
  { id: "gfs",   name: "GFS",   base: "" },
  { id: "ecmwf", name: "ECMWF", base: "https://brandonaog.github.io/wx-ecmwf/" },
];
// Optional single override for everything (e.g. an R2 bucket URL). Leave "".
window.WX_ASSETS = "";
