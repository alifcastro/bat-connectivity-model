#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solar disturbance decay and resistance-surface generation.

Creates a species-specific solar pressure surface, subtracts weighted pressure
from baseline habitat quality, and transforms effective habitat quality to
resistance on a 1-100 scale. Distances are in metres.
"""

import arcpy
from arcpy.sa import Raster, Con, Square

DECAY = {
    'GH': {'core_m': 30.0, 'outer_m': 250.0},
    'LH': {'core_m': 30.0, 'outer_m': 250.0},
}


def model_solar_impact_and_resistance(dist_raster_path, h_base_path,
                                      zone_weight_path, out_pressure_path,
                                      out_heff_path, out_resistance_path,
                                      species='GH'):
    """Generate P_solar, H_effective and resistance rasters.

    Equations
    ---------
    Pressure is 1 inside the species-specific core, decreases linearly to 0
    at the outer distance, and is 0 beyond it.

    H_effective = max(0, H_base - P_solar * W_zone)
    R = 1 + 99 * (1 - H_effective)^2

    H_base and W_zone are therefore expected on a 0-1 scale. The resulting
    resistance is 1 (highest habitat quality / lowest resistance) to 100
    (zero effective habitat quality / highest modelled resistance).
    """
    species = str(species).upper()
    if species not in DECAY:
        raise ValueError("species must be 'GH' or 'LH'.")

    arcpy.CheckOutExtension('Spatial')
    try:
        dist = Raster(dist_raster_path)
        h_base = Raster(h_base_path)
        zone_weight = (Raster(zone_weight_path)
                       if isinstance(zone_weight_path, str)
                       else float(zone_weight_path))

        core = DECAY[species]['core_m']
        outer = DECAY[species]['outer_m']
        span = outer - core
        p_solar = Con(
            dist <= core,
            1.0,
            Con(dist >= outer, 0.0, 1.0 - ((dist - core) / span)),
        )
        p_solar.save(out_pressure_path)

        # Clamp explicitly to 0-1 to keep the subsequent resistance in range.
        h_effective_raw = h_base - (p_solar * zone_weight)
        h_effective = Con(
            h_effective_raw < 0.0,
            0.0,
            Con(h_effective_raw > 1.0, 1.0, h_effective_raw),
        )
        h_effective.save(out_heff_path)

        r_surface = 1.0 + (99.0 * Square(1.0 - h_effective))
        r_surface.save(out_resistance_path)
        return r_surface
    finally:
        arcpy.CheckInExtension('Spatial')
