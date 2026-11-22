# Horseshoe bat habitat and solar-PV connectivity code

Code accompanying a master's dissertation comparing landscape connectivity for greater horseshoe bat (*Rhinolophus ferrumequinum*, GH) and lesser horseshoe bat (*Rhinolophus hipposideros*, LH) under baseline and solar-PV disturbance scenarios.

## Repository contents

1. `01_living_england_scoring.py` — species-specific Living England scoring functions for greater horseshoe bat (`calc_ghb`) and lesser horseshoe bat (`calc_lhb`) on a 0-10 scale. Both use the two highest-probability Living England classes, the +2 designated-site modifier and the Ancient Woodland override. The LH function additionally applies documented woodland/scrub adjacency rules.
2. `02_baseline_habitat_mcda.py` — combines normalised environmental layers into baseline habitat suitability, `H_base` (0-1).
3. `03_solar_decay_and_resistance.py` — generates species-specific solar-pressure decay, effective habitat quality and resistance (1-100).

## Processing sequence

`Living England scoring -> normalisation to 0-1 -> baseline MCDA -> solar pressure -> effective habitat -> resistance surface -> connectivity analysis`

The final connectivity analysis (for example, GIS/Linkage Mapper processing and network metrics) is not implemented in these three Python files unless separately supplied in the repository. Do not treat these scripts as a complete replacement for the dissertation Methods.

## Core equations

Baseline habitat suitability:

`H_base = 0.20(VHVV) + 0.35(Commute) + 0.35(LivingE) + 0.10(Aspect_Slope)`

Solar-adjusted effective habitat:

`H_effective = max(0, H_base - P_solar * W_zone)`

Resistance transformation:

`R = 1 + 99(1 - H_effective)^2`

The implementation clamps `H_effective` to 0-1 before resistance conversion.

## Solar-pressure distances

| Species | Code | Full-pressure core | Linear decay reaches zero |
|---|---|---:|---:|
| Greater horseshoe bat | GH | 30 m | 250 m |
| Lesser horseshoe bat | LH | 30 m | 250 m |

Both species therefore use the same PV pressure-decay distances: full pressure to 30 m, followed by linear decay to zero at 250 m.

These are study parameters and should be interpreted using the dissertation's literature review and methodology rather than as universal species thresholds.

## Requirements

- Python 3 as provided with ArcGIS Pro
- ArcPy
- ArcGIS Spatial Analyst extension

ArcPy is distributed with ArcGIS Pro and is not installed from PyPI, so no conventional `requirements.txt` is provided.

## Inputs and assumptions

- MCDA raster inputs must be normalised to the continuous range 0-1 before Script 02.
- `dist_raster_path` is a distance raster in metres from the solar-array footprint.
- `zone_weight_path` in Script 03 may be a raster path or a scalar and is expected on a 0-1 scale.
- Living England class labels must match the strings used in Script 01.
- In ArcGIS Pro Calculate Field, use `calc_ghb(...)` for *R. ferrumequinum* and `calc_lhb(...)` for *R. hipposideros*.
- No raw spatial datasets are redistributed here. Users should obtain source data from the original providers and reproduce preprocessing as described in the dissertation.

## Living England scoring scope

Script 01 now includes both species-specific scoring functions. `calc_ghb` reproduces the greater horseshoe bat class values given in the dissertation methodology, while `calc_lhb` reproduces the lesser horseshoe bat values and its woodland/scrub adjacency adjustments. The methodology mentions additional GH transition adjustments but does not state a numerical multiplier; the repository therefore does not invent those undocumented adjustments. Add them only if the exact rule used in the analysis can be recovered.

## Reproducibility

Run scripts in numerical order where they form part of the relevant species workflow. Dataset preparation, clipping, projection, raster alignment/cell size, normalisation, core-area definition and downstream connectivity/network analysis must follow the dissertation methodology.

## Citation

If this repository accompanies the dissertation, add the final dissertation citation and repository DOI (for example, a Zenodo DOI) here after archiving.
