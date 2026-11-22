#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Species-specific Living England habitat suitability scoring (0-10).

Designed for use as Python functions in the ArcGIS Pro Calculate Field tool.
Both functions combine the two highest-probability Living England classes by
probability-weighted averaging, then apply the dissertation's designated-site
modifier and Ancient Woodland override.

The greater horseshoe bat (GH) scores reproduce the values in the dissertation
methodology table. The lesser horseshoe bat (LH) scores reproduce its separate
methodology table and retain the documented woodland/scrub adjacency rules.
"""


def _flag(value):
    """Return True only when a value is numerically equal to 1."""
    try:
        return float(value) == 1.0
    except (TypeError, ValueError):
        return False


def _probability(value):
    """Return a non-negative numeric prediction weight."""
    try:
        return max(0.0, float(value)) if value is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _weighted_score(a_pred, a_prob, b_pred, b_prob, scores):
    """Probability-weight two class scores and return names/probabilities."""
    a_name = '' if a_pred is None else str(a_pred)
    b_name = '' if b_pred is None else str(b_pred)
    p_a = _probability(a_prob)
    p_b = _probability(b_prob)
    s_a = scores.get(a_name, 0.0)
    s_b = scores.get(b_name, 0.0)
    total = p_a + p_b
    base = ((s_a * p_a) + (s_b * p_b)) / total if total > 0 else s_a
    return base, a_name, b_name, p_a, p_b


def _apply_conservation_rules(base, a_name, b_name, p_a, p_b,
                              is_desig, is_ancient_wood, targets):
    """Apply the Ancient Woodland override and designated-site modifier."""
    if _flag(is_ancient_wood) and ('Woodland' in a_name or 'Woodland' in b_name):
        return 10.0

    eligible = ((a_name in targets and p_a > 0) or
                (b_name in targets and p_b > 0))
    if _flag(is_desig) and eligible:
        base += 2.0
    return min(max(base, 0.0), 10.0)


def calc_ghb(a_pred, a_prob, b_pred, b_prob, is_desig,
             is_ancient_wood=0):
    """Return greater horseshoe bat habitat suitability on a 0-10 scale.

    ArcGIS Field Calculator expression::

        calc_ghb(!A_pred!, !A_prob!, !B_pred!, !B_prob!,
                 !is_designated!, !is_ancient_wood!)

    Scores follow the greater horseshoe bat Living England table in the
    dissertation methodology. The narrative mentions additional transition
    adjustments but gives no numerical multiplier; those undocumented
    adjustments are not invented here.
    """
    scores = {
        'Broadleaved, Mixed and Yew Woodland': 10.0,
        'Scrub': 8.0,
        'Fen, Marsh and Swamp': 7.0,
        'Water': 3.0,
        'Bog': 7.0,
        'Acid, Calcareous, Neutral Grassland': 8.0,
        'Improved Grassland': 5.0,
        'Coniferous Woodland': 3.0,
        'Dwarf Shrub Heath': 3.0,
        'Built-up Areas and Gardens': 2.0,
        'Bracken': 2.0,
        'Arable and Horticultural': 0.0,
        'Bare Ground': 0.0,
        'Bare Sand': 0.0,
        'Coastal Saltmarsh': 0.0,
        'Coastal Sand Dunes': 0.0,
        'Unclassified': 0.0,
    }
    base, a_name, b_name, p_a, p_b = _weighted_score(
        a_pred, a_prob, b_pred, b_prob, scores)
    targets = {
        'Broadleaved, Mixed and Yew Woodland',
        'Scrub',
        'Fen, Marsh and Swamp',
        'Bog',
        'Acid, Calcareous, Neutral Grassland',
        'Improved Grassland',
    }
    return _apply_conservation_rules(
        base, a_name, b_name, p_a, p_b, is_desig,
        is_ancient_wood, targets)


def calc_lhb(a_pred, a_prob, b_pred, b_prob, is_desig,
             is_near_wood_scrub, is_ancient_wood=0):
    """Return lesser horseshoe bat habitat suitability on a 0-10 scale.

    ArcGIS Field Calculator expression::

        calc_lhb(!A_pred!, !A_prob!, !B_pred!, !B_prob!,
                 !is_designated!, !is_near_wood_scrub!, !is_ancient_wood!)
    """
    near_wood = _flag(is_near_wood_scrub)
    scores = {
        'Broadleaved, Mixed and Yew Woodland': 10.0,
        'Scrub': 10.0,
        'Fen, Marsh and Swamp': 5.0,
        'Water': 8.0 if near_wood else 3.0,
        'Bog': 0.0,
        'Acid, Calcareous, Neutral Grassland': 4.0,
        'Improved Grassland': 1.0,
        'Coniferous Woodland': 6.0 if near_wood else 4.0,
        'Dwarf Shrub Heath': 2.0,
        'Built-up Areas and Gardens': 3.0,
        'Bracken': 5.0 if near_wood else 2.0,
        'Arable and Horticultural': 1.0,
        'Bare Ground': 0.0,
        'Bare Sand': 0.0,
        'Coastal Saltmarsh': 0.0,
        'Coastal Sand Dunes': 0.0,
        'Unclassified': 0.0,
    }
    base, a_name, b_name, p_a, p_b = _weighted_score(
        a_pred, a_prob, b_pred, b_prob, scores)
    targets = {
        'Broadleaved, Mixed and Yew Woodland',
        'Scrub',
        'Fen, Marsh and Swamp',
        'Coniferous Woodland',
    }
    return _apply_conservation_rules(
        base, a_name, b_name, p_a, p_b, is_desig,
        is_ancient_wood, targets)
