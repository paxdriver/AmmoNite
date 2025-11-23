# facility_footprint_sizer.py
# Phase 3: height‑constrained facility footprint exploration.
#
# Chain:
#   Inputs  --> AN_system_anchoring_sizer.size(...)
#           --> equipment_volume_sizer.volume_sizer(...)
#           --> facility_footprint_sizer.footprint_sizer(...)
#
# This script:
#   - takes total storage/processing volumes from volume_sizer,
#   - for each material ("service") and roof‑height scenario,
#   - explores different numbers of tanks,
#   - scores each option using service‑specific heuristics
#     (volume range, aspect ratio, tank count, total area),
#   - returns best‑scoring candidates and scenario‑level footprint sums.
#
# No final equipment design is chosen here; this is for comparison and
# for guiding later Blender/CAD work.

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional
from cli_utils import br

from AN_system_anchoring_sizer import Inputs, size
from equipment_volume_sizer import volume_sizer

# -------------------------------------------------------------------
# Global layout parameters (tunable)
# -------------------------------------------------------------------

# Roof‑height scenarios (metres), approximate clear heights
HEIGHT_SCENARIOS_DEFAULT: Dict[str, float] = {
    # Roughly a 2‑storey house from ground to roof peak
    "house": 7.0,
    # Typical retail / light warehouse (grocery, big‑box)
    "warehouse": 10.0,
    # Large logistics / distribution centre with high racking
    "logistics": 14.0,
    # High‑bay industrial / shipbuilding / heavy crane hall
    "shipping": 25.0,
    # Effectively "no height limit" for comparison purposes
    # (100 m is far beyond what you'd actually build)
    "unlimited": 100.0,
}

# Reference footprint used ONLY for "single‑tank reference height"
# reporting (mental check, not a design choice).
REFERENCE_TANK_FOOTPRINT_M2: float = 200.0

# Maximum tanks per service searched; higher values increase runtime
# and are rarely useful for this scale.
GLOBAL_MAX_TANKS: int = 50

# Small number for avoiding divide‑by‑zero
EPS = 1e-9

# -------------------------------------------------------------------
# Service‑specific heuristics
# -------------------------------------------------------------------


@dataclass
class ServiceParams:
    name: str
    volume_key: str

    # Ideal per‑tank volume range (m3). None = no preference.
    ideal_vol_min_m3: Optional[float]
    ideal_vol_max_m3: Optional[float]

    # Ideal aspect ratio range: H / sqrt(A). None = no preference.
    aspect_min: Optional[float]
    aspect_max: Optional[float]

    # Tank count preference: "few_large", "many_moderate", or "neutral".
    preference: str

    # Hard maximum per‑tank volume (m3); None = no hard cap.
    hard_max_per_tank_m3: Optional[float]

    # Absolute cap on number of tanks searched.
    max_tanks: int

    # Weights for scoring terms
    w_vol: float
    w_aspect: float
    w_count: float
    w_area: float

    # Scale used to normalize area penalty; larger value = weaker penalty
    area_scale_m2: float = 1_000.0


SERVICE_PARAMS: Dict[str, ServiceParams] = {
    # 1) Sand / rock / salt thermal storage
    "sand_heat_storage": ServiceParams(
        name="sand_heat_storage",
        volume_key="Heat_storage_sand_volume_m3",
        ideal_vol_min_m3=50.0,
        ideal_vol_max_m3=500.0,
        aspect_min=1.5,          # tallish bed preferred
        aspect_max=4.0,
        preference="few_large",  # fewer, larger beds better thermally
        hard_max_per_tank_m3=None,
        max_tanks=10,
        w_vol=2.0,
        w_aspect=3.0,
        w_count=2.0,
        w_area=0.5,
    ),
    # 2) Potable water storage
    "potable_water": ServiceParams(
        name="potable_water",
        volume_key="Potable_storage_volume_m3",
        ideal_vol_min_m3=50.0,
        ideal_vol_max_m3=300.0,
        aspect_min=0.8,
        aspect_max=2.0,
        preference="neutral",
        hard_max_per_tank_m3=None,
        max_tanks=20,
        w_vol=2.0,
        w_aspect=1.0,
        w_count=1.0,
        w_area=1.0,
    ),
    # 3) Brine storage (corrosive)
    "brine": ServiceParams(
        name="brine",
        volume_key="Brine_storage_volume_m3",
        ideal_vol_min_m3=50.0,
        ideal_vol_max_m3=200.0,
        aspect_min=0.8,
        aspect_max=2.0,
        preference="many_moderate",  # avoid huge single brine tanks
        hard_max_per_tank_m3=None,
        max_tanks=20,
        w_vol=2.0,
        w_aspect=1.0,
        w_count=1.5,
        w_area=1.0,
    ),
    # 4) Binder storage
    "binder": ServiceParams(
        name="binder",
        volume_key="Binder_storage_volume_m3",
        ideal_vol_min_m3=10.0,
        ideal_vol_max_m3=100.0,
        aspect_min=1.0,
        aspect_max=3.0,
        preference="neutral",
        hard_max_per_tank_m3=None,
        max_tanks=10,
        w_vol=2.0,
        w_aspect=1.5,
        w_count=1.0,
        w_area=0.5,
    ),
    # 5) NaCl bulk storage (can be outdoor piles)
    "NaCl": ServiceParams(
        name="NaCl",
        volume_key="NaCl_storage_volume_m3",
        ideal_vol_min_m3=100.0,
        ideal_vol_max_m3=5_000.0,
        aspect_min=None,    # aspect mostly irrelevant
        aspect_max=None,
        preference="few_large",
        hard_max_per_tank_m3=None,
        max_tanks=10,
        w_vol=1.0,
        w_aspect=0.0,
        w_count=0.5,
        w_area=1.0,
        area_scale_m2=5_000.0,  # big piles acceptable
    ),
    # 6) NH3 backup storage (hazardous)
    "NH3_backup": ServiceParams(
        name="NH3_backup",
        volume_key="NH3_backup_volume_m3",
        ideal_vol_min_m3=10.0,
        ideal_vol_max_m3=40.0,
        aspect_min=1.0,
        aspect_max=3.0,
        preference="many_moderate",  # safety prefers more, smaller
        hard_max_per_tank_m3=50.0,   # do not exceed this per tank
        max_tanks=20,
        w_vol=3.0,
        w_aspect=1.5,
        w_count=2.0,
        w_area=0.5,
    ),
}

# Order in which services will be reported
SERVICE_ORDER: List[str] = [
    "sand_heat_storage",
    "potable_water",
    "brine",
    "binder",
    "NaCl",
    "NH3_backup",
]


# -------------------------------------------------------------------
# Scoring helpers
# -------------------------------------------------------------------


def _penalty_volume(
    vol_m3: float,
    ideal_min: Optional[float],
    ideal_max: Optional[float],
) -> float:
    """Soft penalty for per‑tank volume outside ideal range."""
    if vol_m3 <= 0.0:
        return 5.0  # strongly discourage degenerate cases
    if ideal_min is None or ideal_max is None:
        return 0.0

    if ideal_min <= vol_m3 <= ideal_max:
        return 0.0

    if vol_m3 < ideal_min:
        ratio = ideal_min / max(vol_m3, EPS)
    else:
        ratio = vol_m3 / ideal_max

    penalty = (ratio - 1.0) ** 2
    return min(penalty, 25.0)


def _penalty_aspect(
    height_m: float,
    area_m2: float,
    aspect_min: Optional[float],
    aspect_max: Optional[float],
) -> float:
    """Soft penalty on slenderness H/sqrt(A) outside ideal range."""
    if aspect_min is None or aspect_max is None:
        return 0.0
    if height_m <= 0.0 or area_m2 <= 0.0:
        return 5.0

    slenderness = height_m / max(math.sqrt(area_m2), EPS)

    if aspect_min <= slenderness <= aspect_max:
        return 0.0

    if slenderness < aspect_min:
        ratio = aspect_min / max(slenderness, EPS)
    else:
        ratio = slenderness / aspect_max

    penalty = (ratio - 1.0) ** 2
    return min(penalty, 25.0)


def _penalty_count(n_tanks: int, preference: str) -> float:
    """Penalty based on number of tanks and qualitative preference."""
    n = max(1, n_tanks)

    if preference == "few_large":
        # Zero at N=1, grows sub‑linearly with N.
        return (n - 1) ** 0.5

    if preference == "many_moderate":
        # High penalty if only 1 big tank; smaller penalty as N grows.
        return 1.0 / float(n)

    # neutral: soft penalty for very many tanks
    return max(0.0, (n - 1)) ** 0.3


def _penalty_area(total_area_m2: float, area_scale_m2: float) -> float:
    """Penalty proportional to total footprint scaled by area_scale."""
    if total_area_m2 <= 0.0 or area_scale_m2 <= 0.0:
        return 0.0
    return total_area_m2 / area_scale_m2


def _evaluate_candidates_for_service(
    params: ServiceParams,
    total_volume_m3: float,
    max_height_m: float,
    max_tanks_global: int = GLOBAL_MAX_TANKS,
) -> List[Dict[str, float]]:
    """
    For a given service and roof height, enumerate tank counts and score
    each candidate. Returns a list of variants sorted by total score
    (lower is better).
    """
    variants: List[Dict[str, float]] = []

    if total_volume_m3 <= 0.0 or max_height_m <= 0.0:
        return [
            {
                "tanks": 0.0,
                "tank_height_m": max_height_m,
                "per_tank_volume_m3": 0.0,
                "per_tank_footprint_m2": 0.0,
                "per_tank_linear_dim_m": 0.0,
                "total_footprint_m2": 0.0,
                "slenderness_H_over_sqrtA": 0.0,
                "score": 0.0,
                "score_components": {
                    "vol": 0.0,
                    "aspect": 0.0,
                    "count": 0.0,
                    "area": 0.0,
                },
                "hard_volume_cap_triggered": False,
            }
        ]

    # Hard minimum tank count from volume cap, if any
    if params.hard_max_per_tank_m3 and params.hard_max_per_tank_m3 > 0.0:
        n_min = math.ceil(total_volume_m3 / params.hard_max_per_tank_m3)
    else:
        n_min = 1

    n_min = max(1, n_min)
    n_max = min(
        max_tanks_global,
        max(params.max_tanks, n_min),
    )

    for n in range(n_min, n_max + 1):
        per_tank_vol = total_volume_m3 / float(n)
        per_tank_area = per_tank_vol / max_height_m
        per_tank_area = max(per_tank_area, 0.0)
        per_tank_side = math.sqrt(per_tank_area) if per_tank_area > 0.0 else 0.0
        total_area = per_tank_area * float(n)

        # Penalty terms
        p_vol = _penalty_volume(
            per_tank_vol,
            params.ideal_vol_min_m3,
            params.ideal_vol_max_m3,
        )
        p_aspect = _penalty_aspect(
            max_height_m,
            per_tank_area,
            params.aspect_min,
            params.aspect_max,
        )
        p_count = _penalty_count(n, params.preference)
        p_area = _penalty_area(total_area, params.area_scale_m2)

        score = (
            params.w_vol * p_vol
            + params.w_aspect * p_aspect
            + params.w_count * p_count
            + params.w_area * p_area
        )

        hard_cap_triggered = (
            params.hard_max_per_tank_m3 is not None
            and per_tank_vol > params.hard_max_per_tank_m3 + EPS
        )

        # Compute slenderness for reporting
        slenderness = (
            max_height_m / max(per_tank_side, EPS) if per_tank_side > 0.0 else 0.0
        )

        variants.append(
            {
                "tanks": float(n),
                "tank_height_m": max_height_m,
                "per_tank_volume_m3": per_tank_vol,
                "per_tank_footprint_m2": per_tank_area,
                "per_tank_linear_dim_m": per_tank_side,
                "total_footprint_m2": total_area,
                "slenderness_H_over_sqrtA": slenderness,
                "score": score,
                "score_components": {
                    "vol": params.w_vol * p_vol,
                    "aspect": params.w_aspect * p_aspect,
                    "count": params.w_count * p_count,
                    "area": params.w_area * p_area,
                },
                "hard_volume_cap_triggered": hard_cap_triggered,
            }
        )

    # Sort by increasing score
    variants.sort(key=lambda v: v["score"])
    return variants


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------


def footprint_sizer(
    inputs: Inputs,
    height_scenarios: Optional[Dict[str, float]] = None,
    reference_tank_area_m2: float = REFERENCE_TANK_FOOTPRINT_M2,
    top_k_per_service: int = 3,
) -> Dict[str, Dict]:
    """
    Run volume_sizer(inputs), then for each service volume and each
    roof‑height scenario, compute and score candidate tank layouts.

    Returns a nested dict:

    {
      "services": {
         <service_name>: {
            "total_volume_m3": ...,
            "single_tank_reference_height_m": ...,
            "scenarios": {
               <scenario_name>: {
                  "max_height_m": ...,
                  "candidates": [ {variant1}, {variant2}, ... ]
               },
               ...
            }
         },
         ...
      },
      "scenario_totals": {
         <scenario_name>: {
             "max_height_m": ...,
             "best_total_footprint_m2": ...,
             "best_total_footprint_ha": ...,
             "per_service_best": {
                 <service_name>: {variant_for_best_choice}
             }
         },
         ...
      }
    }
    """
    if height_scenarios is None:
        height_scenarios = HEIGHT_SCENARIOS_DEFAULT

    # Phase 2 results: volumes and areas
    vols = volume_sizer(inputs)

    services_out: Dict[str, Dict] = {}

    # Per‑service layouts
    for service_name in SERVICE_ORDER:
        params = SERVICE_PARAMS[service_name]
        total_volume_m3 = float(vols.get(params.volume_key, 0.0))

        service_entry: Dict[str, Dict] = {}
        service_entry["total_volume_m3"] = total_volume_m3

        if reference_tank_area_m2 > 0.0:
            ref_height = total_volume_m3 / reference_tank_area_m2
        else:
            ref_height = 0.0
        service_entry["single_tank_reference_height_m"] = ref_height

        scen_dict: Dict[str, Dict] = {}

        for scen_name, max_height_m in height_scenarios.items():
            max_h = float(max_height_m)

            variants = _evaluate_candidates_for_service(
                params=params,
                total_volume_m3=total_volume_m3,
                max_height_m=max_h,
            )

            # Keep only the best K variants for reporting
            scen_dict[scen_name] = {
                "max_height_m": max_h,
                "candidates": variants[:top_k_per_service],
            }

        service_entry["scenarios"] = scen_dict
        services_out[service_name] = service_entry

    # Scenario‑level totals using the *best* candidate for each service
    scenario_totals: Dict[str, Dict] = {}
    for scen_name, max_height_m in (height_scenarios or {}).items():
        max_h = float(max_height_m)
        total_area = 0.0
        per_service_best: Dict[str, Dict] = {}

        for service_name in SERVICE_ORDER:
            svc_entry = services_out[service_name]
            scen_entry = svc_entry["scenarios"][scen_name]
            candidates = scen_entry["candidates"]

            if not candidates:
                continue

            best_variant = candidates[0]
            total_area += best_variant["total_footprint_m2"]
            per_service_best[service_name] = best_variant

        scenario_totals[scen_name] = {
            "max_height_m": max_h,
            "best_total_footprint_m2": total_area,
            "best_total_footprint_ha": total_area / 10_000.0,
            "per_service_best": per_service_best,
        }

    return {
        "services": services_out,
        "scenario_totals": scenario_totals,
    }


# -------------------------------------------------------------------
# Example CLI usage
# -------------------------------------------------------------------

if __name__ == "__main__":

    def run_example(label: str, inp: Inputs) -> None:
        print(f"\n=== {label} example ===")
        print("— Base process sizing (selected fields) —")
        base = size(inp)
        for key in (
            "AN_tpd",
            "Electricity_required_MWhpd",
            "MED_water_m3pd",
            "MED_brine_m3pd",
            "Mg_binder_tpd",
            "NaCl_tpd_potential",
            "NH3_for_backup_per_outage_event_kg",
        ):
            print(f"{key:45s}: {base[key]}")
        br()

        fp = footprint_sizer(inp, top_k_per_service=3)

        print("— Scenario‑level best footprints —")
        for scen_name, scen in fp["scenario_totals"].items():
            print(
                f"  Scenario '{scen_name}' (H_max={scen['max_height_m']} m): "
                f"best total A={scen['best_total_footprint_m2']:.1f} m2 "
                f"({scen['best_total_footprint_ha']:.3f} ha)"
            )
        br()

    # 1) Micro module: ~1 t/d AN
    micro_inputs = Inputs(
        an_tpd=1.0,
        critical_load_fraction=0.3,
        backup_days=3.0,
    )
    run_example("micro_1_tpd", micro_inputs)

    # 2) Community module: ~5 t/d AN
    community_inputs = Inputs(
        an_tpd=5.0,
        available_electricity_MWh_per_day=25.0,
        electrolyzer_power_MW=0.9,
        critical_load_fraction=0.3,
        backup_days=3.0,
    )
    run_example("community_5_tpd", community_inputs)

    # 3) Regional module: ~20 t/d AN
    regional_inputs = Inputs(
        an_tpd=20.0,
        critical_load_fraction=0.3,
        backup_days=3.0,
    )
    run_example("regional_20_tpd", regional_inputs)