#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Composite baseline habitat suitability using a weighted MCDA overlay.

All inputs must already be normalised to 0-1. The weights below are the
study-defined MCDA weights documented in the dissertation methodology; they
are not described here as statistically estimated or empirically fitted.
"""

import arcpy
from arcpy.sa import Raster

WEIGHTS = {
    'living_england': 0.35,
    'commuting_corridors': 0.35,
    'vhvv': 0.20,
    'aspect_slope': 0.10,
}


def compute_baseline_habitat(vhvv_path, commute_path, livinge_path,
                             aspect_slope_path, out_raster_path):
    """Create and save a species-specific baseline habitat raster (H_base).

    H_base = 0.20*VHVV + 0.35*Commute + 0.35*LivingE + 0.10*Aspect_Slope
    """
    if abs(sum(WEIGHTS.values()) - 1.0) > 1e-12:
        raise ValueError('MCDA weights must sum to 1.0.')

    arcpy.CheckOutExtension('Spatial')
    try:
        vhvv = Raster(vhvv_path)
        commute = Raster(commute_path)
        living_e = Raster(livinge_path)
        aspect_slope = Raster(aspect_slope_path)

        h_base = (
            WEIGHTS['vhvv'] * vhvv
            + WEIGHTS['commuting_corridors'] * commute
            + WEIGHTS['living_england'] * living_e
            + WEIGHTS['aspect_slope'] * aspect_slope
        )
        h_base.save(out_raster_path)
        return h_base
    finally:
        arcpy.CheckInExtension('Spatial')
