# equipment_volume_sizer.py
# Phase 2, step 1: convert AN_system_anchoring_sizer outputs into
# conservative volumes, masses, and solar collection areas.
#
# No equipment counts, footprints, or vessel dimensions are chosen here.
# Those will be explored in a later script so we can compare options.

from typing import Dict
from AN_system_anchoring_sizer import Inputs, size, KW_PER_MW
from cli_utils import br

# ---------- Physical / environmental assumptions (tunable) ----------

# Solar resource and conversion efficiencies
INSOLATION_KWH_PER_M2_PER_DAY = 6.0   # kWh/m2/day, typical sunny desert
ELECTRIC_COLLECTION_EFF = 0.20        # PV or equivalent elec. fraction
THERMAL_COLLECTION_EFF = 0.60         # solar-thermal to useful heat

# Thermal storage medium (sand / rock / salt mix)
SAND_CP_KJ_PER_KG_K = 0.84            # kJ/(kg·K)
SAND_DENSITY_KG_PER_M3 = 1_600.0      # kg/m3
SAND_DELTA_T_K = 200.0                # allowed temperature swing
HEAT_STORAGE_DAYS = 1.0               # days of full MED heat to store

# Storage durations (days of buffer)
POTABLE_STORAGE_DAYS = 1.0            # potable water buffer
BRINE_STORAGE_DAYS = 1.0              # brine buffer
BINDER_STORAGE_DAYS = 3.0             # Mg-binder buffer
NACL_STORAGE_DAYS = 7.0               # NaCl buffer

# Material densities for volume estimates
BINDER_DENSITY_KG_PER_M3 = 1_200.0    # bulk Mg-binder
NACL_BULK_DENSITY_KG_PER_M3 = 1_300.0 # bulk salt pile
NH3_LIQUID_DENSITY_KG_PER_M3 = 682.0  # liquid ammonia at moderate P,T


def volume_sizer(i: Inputs) -> Dict[str, float]:
    """
    Run AN_system_anchoring_sizer.size(i) and translate key flows into:

      - solar collection areas (m2),
      - thermal storage mass/volume,
      - storage volumes for water, brine, binder, NaCl,
      - backup NH3 storage volume.

    Returns a flat dict; all units are in SI (m2, m3, kg, t, MWh/day).
    """

    r = size(i)  # base process sizing

    # ---- Convenience aliases from base results ----
    elec_MWhpd = r["Electricity_required_MWhpd"]         # MWh_e/day
    med_water_m3pd = r["MED_water_m3pd"]                 # potable water
    med_brine_m3pd = r["MED_brine_m3pd"]                 # brine
    el_waste_MWhth_pd = r["El_waste_heat_MWhth_pd"]      # MWh_th/day
    hno3_steam_MWhth_pd = r["HNO3_steam_MWhth_pd"]       # MWh_th/day
    binder_tpd = r["Mg_binder_tpd"]                      # t/day binder
    nacl_tpd = r["NaCl_tpd_potential"]                   # t/day NaCl
    nh3_backup_kg = r["NH3_for_backup_per_outage_event_kg"]

    # Total useful heat to MED (electrolyzer + nitric steam)
    med_heat_MWhth_pd = el_waste_MWhth_pd + hno3_steam_MWhth_pd

    out: Dict[str, float] = {}

    # ---------- Solar collection areas ----------

    # Electric: MWh/day → kWh/day = *KW_PER_MW
    if elec_MWhpd > 0.0 and INSOLATION_KWH_PER_M2_PER_DAY > 0.0 and ELECTRIC_COLLECTION_EFF > 0.0:
        solar_electric_area_m2 = (
            elec_MWhpd * KW_PER_MW
            / (INSOLATION_KWH_PER_M2_PER_DAY * ELECTRIC_COLLECTION_EFF)
        )
    else:
        solar_electric_area_m2 = 0.0

    out["Solar_electric_area_m2"] = solar_electric_area_m2
    out["Solar_electric_area_ha"] = solar_electric_area_m2 / 10_000.0

    # Thermal: MWh_th/day → kWh_th/day = *KW_PER_MW
    if med_heat_MWhth_pd > 0.0 and INSOLATION_KWH_PER_M2_PER_DAY > 0.0 and THERMAL_COLLECTION_EFF > 0.0:
        solar_thermal_area_m2 = (
            med_heat_MWhth_pd * KW_PER_MW
            / (INSOLATION_KWH_PER_M2_PER_DAY * THERMAL_COLLECTION_EFF)
        )
    else:
        solar_thermal_area_m2 = 0.0

    out["Solar_thermal_area_m2"] = solar_thermal_area_m2
    out["Solar_thermal_area_ha"] = solar_thermal_area_m2 / 10_000.0

    # ---------- Thermal storage (sand / rock) ----------

    # Energy to store: MED heat for HEAT_STORAGE_DAYS (MWh_th)
    heat_to_store_MWh = med_heat_MWhth_pd * HEAT_STORAGE_DAYS

    # Convert MWh_th → kWh_th → kJ
    heat_to_store_kJ = heat_to_store_MWh * KW_PER_MW * 3_600.0

    if SAND_CP_KJ_PER_KG_K > 0.0 and SAND_DELTA_T_K > 0.0 and SAND_DENSITY_KG_PER_M3 > 0.0:
        sand_mass_kg = heat_to_store_kJ / (SAND_CP_KJ_PER_KG_K * SAND_DELTA_T_K)
        sand_vol_m3 = sand_mass_kg / SAND_DENSITY_KG_PER_M3
    else:
        sand_mass_kg = 0.0
        sand_vol_m3 = 0.0

    out["Heat_storage_days"] = HEAT_STORAGE_DAYS
    out["Heat_storage_energy_MWh_th"] = heat_to_store_MWh
    out["Heat_storage_sand_mass_kg"] = sand_mass_kg
    out["Heat_storage_sand_volume_m3"] = sand_vol_m3

    # ---------- Potable water storage ----------

    potable_storage_m3 = med_water_m3pd * POTABLE_STORAGE_DAYS
    out["Potable_storage_days"] = POTABLE_STORAGE_DAYS
    out["Potable_storage_volume_m3"] = potable_storage_m3

    # ---------- Brine storage ----------

    brine_storage_m3 = med_brine_m3pd * BRINE_STORAGE_DAYS
    out["Brine_storage_days"] = BRINE_STORAGE_DAYS
    out["Brine_storage_volume_m3"] = brine_storage_m3

    # ---------- Binder storage ----------

    binder_kgpd = binder_tpd * 1_000.0
    if BINDER_DENSITY_KG_PER_M3 > 0.0:
        binder_storage_vol_m3 = (
            binder_kgpd * BINDER_STORAGE_DAYS / BINDER_DENSITY_KG_PER_M3
        )
    else:
        binder_storage_vol_m3 = 0.0

    out["Binder_storage_days"] = BINDER_STORAGE_DAYS
    out["Binder_storage_volume_m3"] = binder_storage_vol_m3
    out["Binder_daily_mass_kg"] = binder_kgpd

    # ---------- NaCl storage ----------

    nacl_kgpd = nacl_tpd * 1_000.0
    if NACL_BULK_DENSITY_KG_PER_M3 > 0.0:
        nacl_storage_vol_m3 = (
            nacl_kgpd * NACL_STORAGE_DAYS / NACL_BULK_DENSITY_KG_PER_M3
        )
    else:
        nacl_storage_vol_m3 = 0.0

    out["NaCl_storage_days"] = NACL_STORAGE_DAYS
    out["NaCl_storage_volume_m3"] = nacl_storage_vol_m3
    out["NaCl_daily_mass_kg"] = nacl_kgpd

    # ---------- NH3 backup storage ----------

    if NH3_LIQUID_DENSITY_KG_PER_M3 > 0.0:
        nh3_backup_vol_m3 = nh3_backup_kg / NH3_LIQUID_DENSITY_KG_PER_M3
    else:
        nh3_backup_vol_m3 = 0.0

    out["NH3_backup_mass_kg"] = nh3_backup_kg
    out["NH3_backup_volume_m3"] = nh3_backup_vol_m3

    # ---------- Pass-through key process numbers (for convenience) ----------

    out["AN_tpd"] = r["AN_tpd"]
    out["Electricity_required_MWhpd"] = elec_MWhpd
    out["MED_water_m3pd"] = med_water_m3pd
    out["MED_brine_m3pd"] = med_brine_m3pd
    out["Mg_binder_tpd"] = binder_tpd
    out["NaCl_tpd"] = nacl_tpd
    out["Total_MED_heat_MWhth_pd"] = med_heat_MWhth_pd

    return out


if __name__ == "__main__":

    # Example: community-scale module (5 t/d AN)
    example_inputs = Inputs(
        an_tpd=5.0,
        available_electricity_MWh_per_day=25.0,
        electrolyzer_power_MW=0.9,
        critical_load_fraction=0.3,
        backup_days=3.0,
    )

    print("— Base process sizing (selected fields) —")
    base = size(example_inputs)
    for key in (
        "AN_tpd",
        "Electricity_required_MWhpd",
        "MED_water_m3pd",
        "MED_brine_m3pd",
        "Mg_binder_tpd",
        "NaCl_tpd_potential",
        "NH3_for_backup_per_outage_event_kg",
    ):
        print(f"{key:40s}: {base[key]}")

    br()

    print("— Volumes / Areas —")
    geo = volume_sizer(example_inputs)
    for k, v in geo.items():
        print(f"{k:40s}: {v}")

    br()