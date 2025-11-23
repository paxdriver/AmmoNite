# AN_system_anchoring_sizer.py
# Dual-anchored first-pass calculator for an AN + water + binder plant.
# Drive by AN output (tpd), or by available electricity (MWh/day),
# and/or by electrolyzer capacity (MW). Reports surpluses/deficits.
#
# Units: day basis; electrical (MWh), thermal (MWhth). Mid-range, conservative.

from dataclasses import dataclass
from typing import Optional, Dict

KW_PER_MW = 1000.0
HOURS_PER_DAY = 24.0

@dataclass
class Inputs:
    # Independent drivers (any may be None)
    an_tpd: Optional[float] = None  # ammonium nitrate (100% basis), t/day
    available_electricity_MWh_per_day: Optional[float] = None  # site-wide
    electrolyzer_power_MW: Optional[float] = None  # nameplate cap, MW

    # Electrolysis (conservative)
    kWh_per_kg_H2: float = 52.0
    el_waste_kWhth_per_kg_H2: float = 10.0  # recoverable, 60–80 °C

    # HB / Ostwald auxiliaries (electric) — uncertain; keep conservative
    hb_aux_MWh_per_t_NH3: float = 0.25
    acid_aux_MWh_per_t_HNO3: float = 0.10

    # Nitric acid steam export to site (thermal)
    hno3_steam_MWhth_per_t: float = 0.6  # net export; tune with vendor

    # Desal (MED) — thermal sink
    med_kWhth_per_m3: float = 60.0
    med_recovery: float = 0.35  # product/feed (0.25–0.40 typical)

    # Optional RO for surplus electricity
    ro_kWh_per_m3: float = 3.5
    ro_recovery: float = 0.45

    # Seawater composition (approx. Victoria)
    tds_g_per_L: float = 35.0
    nacl_mass_frac_in_tds: float = 0.85
    mg_g_per_L: float = 1.29

    # Mg valorization
    mg_recovery_frac: float = 0.7
    binder_yield_kg_per_kg_MgOH2: float = 1.8
    co2_uptake_kg_per_kg_MgOH2: float = 0.7

    # WWTP oxygen demand (for translating O2 surplus to m3/day aeration)
    o2_demand_kg_per_m3_wwtp: float = 0.25

    # Backup (critical load ride-through)
    critical_load_kW: float = 250   # NOTE: only fractional value of plant's load is being used for critical kW
                                    #       Consider later adding option for fixed critical load value if needed.
    
    # Backup sizing (fraction of plant electrical load)
    critical_load_fraction: float = 0.3  # 0..1, e.g. 0.3 = 30% of plant load
    backup_days: float = 3.0            # days of autonomy at that fraction


def size(i: Inputs) -> Dict[str, float]:
    # Quick sanity check
    if not (0.0 <= i.critical_load_fraction <= 1.0):
        raise ValueError("critical_load_fraction must be between 0 and 1.")
    if i.backup_days < 0:
        raise ValueError("backup_days must be non‑negative.")
    
    # ——— Chemistry constants (exact/standard) ———
    NH3_PER_T_AN = 0.4254       # t NH3 / t AN (0.2127 to acid + 0.2127 to neutralize)
    HNO3_PER_T_AN = 0.7873      # t HNO3 / t AN (100% basis)
    H2_KG_PER_T_NH3 = 176.5     # kg H2 / t NH3 (mass fraction ~0.177)
    O2_PER_T_HNO3 = 64.0 / 63.01  # t O2 / t HNO3 from NH3 + 2O2 -> HNO3 + H2O

    # Derived constants
    H2_KG_PER_T_AN = H2_KG_PER_T_NH3 * NH3_PER_T_AN  # ≈ 75–76 kg H2/t AN

    # Electrical need per t AN (MWh/t AN), conservative, nameplate
    elec_MWh_per_t_AN = (
        i.kWh_per_kg_H2 * H2_KG_PER_T_AN / KW_PER_MW
        + i.hb_aux_MWh_per_t_NH3 * NH3_PER_T_AN
        + i.acid_aux_MWh_per_t_HNO3 * HNO3_PER_T_AN
    )
    # Recoverable low-grade heat and nitric steam per t AN
    el_waste_MWhth_per_t_AN = i.el_waste_kWhth_per_kg_H2 * H2_KG_PER_T_AN / KW_PER_MW
    hno3_steam_MWhth_per_t_AN = i.hno3_steam_MWhth_per_t * HNO3_PER_T_AN

    # ——— Resolve AN_tpd based on drivers ———
    an_from_electric = None
    if i.available_electricity_MWh_per_day is not None:
        if elec_MWh_per_t_AN > 0:
            an_from_electric = i.available_electricity_MWh_per_day / elec_MWh_per_t_AN

    an_from_electrolyzer = None
    if i.electrolyzer_power_MW is not None:
        h2_cap_kgpd = i.electrolyzer_power_MW * HOURS_PER_DAY * KW_PER_MW / i.kWh_per_kg_H2
        if H2_KG_PER_T_AN > 0:
            an_from_electrolyzer = h2_cap_kgpd / H2_KG_PER_T_AN

    # Choose AN_tpd if not given
    if i.an_tpd is None:
        if an_from_electric is None and an_from_electrolyzer is None:
            raise ValueError("Provide an_tpd or available_electricity or electrolyzer_power_MW.")
        # If both limits exist, the bottleneck is the minimum
        if an_from_electric is not None and an_from_electrolyzer is not None:
            an = min(an_from_electric, an_from_electrolyzer)
        else:
            an = an_from_electric if an_from_electric is not None else an_from_electrolyzer
    else:
        an = i.an_tpd

    # ——— Material balances from AN ———
    nh3_total_tpd = NH3_PER_T_AN * an # type: ignore
    hno3_tpd = HNO3_PER_T_AN * an # type: ignore
    h2_kgpd = H2_KG_PER_T_AN * an # type: ignore
    n2_tpd = nh3_total_tpd * 0.823

    # ——— Electricity (minimum to run at this AN) ———
    elec_MWhpd_req = elec_MWh_per_t_AN * an # type: ignore
    hb_aux_MWhpd = i.hb_aux_MWh_per_t_NH3 * NH3_PER_T_AN * an # type: ignore
    acid_aux_MWhpd = i.acid_aux_MWh_per_t_HNO3 * HNO3_PER_T_AN * an # type: ignore

    # Available electricity comparison
    elec_avail = i.available_electricity_MWh_per_day or 0.0
    elec_surplus = elec_avail - elec_MWhpd_req  # negative means deficit

    # Electrolyzer capacity comparison
    h2_cap_kgpd = (
        i.electrolyzer_power_MW * HOURS_PER_DAY * KW_PER_MW / i.kWh_per_kg_H2
        if i.electrolyzer_power_MW is not None
        else None
    )
    h2_surplus_kgpd = None
    if h2_cap_kgpd is not None:
        h2_surplus_kgpd = h2_cap_kgpd - h2_kgpd  # negative means deficit

    # ——— O2 balances ———
    o2_tpd = h2_kgpd * 8.0 / KW_PER_MW
    o2_needed_for_acid_tpd = hno3_tpd * O2_PER_T_HNO3
    o2_left_for_wwtp_tpd = max(0.0, o2_tpd - o2_needed_for_acid_tpd)
    o2_acid_coverage = (
        min(1.0, o2_tpd / o2_needed_for_acid_tpd)
        if o2_needed_for_acid_tpd > 0
        else 1.0
    )

    # ——— Heat to MED ———
    hno3_steam_MWhth_pd = hno3_tpd * i.hno3_steam_MWhth_per_t
    el_waste_MWhth_pd = h2_kgpd * i.el_waste_kWhth_per_kg_H2 / KW_PER_MW
    med_heat_MWhth_pd = hno3_steam_MWhth_pd + el_waste_MWhth_pd
    med_m3pd = med_heat_MWhth_pd * KW_PER_MW / i.med_kWhth_per_m3

    # MED feed / brine and salts
    med_feed_m3pd = med_m3pd / max(1e-6, i.med_recovery)
    med_brine_m3pd = med_feed_m3pd - med_m3pd
    # salts: 1 g/L == 1 kg/m3 → t/day = (g/L * m3/day)/1000
    tds_tpd = i.tds_g_per_L * med_feed_m3pd / KW_PER_MW.0
    nacl_tpd = tds_tpd * i.nacl_mass_frac_in_tds
    mg_kgpd = i.mg_g_per_L * med_feed_m3pd
    mg_captured_kgpd = mg_kgpd * i.mg_recovery_frac
    mgoh2_kgpd = mg_captured_kgpd * (58.3197 / 24.305)
    binder_tpd = mgoh2_kgpd * i.binder_yield_kg_per_kg_MgOH2 / KW_PER_MW
    co2_uptake_tpd = mgoh2_kgpd * i.co2_uptake_kg_per_kg_MgOH2 / KW_PER_MW

    # Optional RO from surplus electricity
    ro_m3pd = 0.0
    if elec_surplus > 0.0:
        ro_m3pd = elec_surplus * KW_PER_MW / i.ro_kWh_per_m3

    # WWTP oxygen service potential
    wwtp_flow_supported_m3pd = (
        (o2_left_for_wwtp_tpd * KW_PER_MW) / i.o2_demand_kg_per_m3_wwtp
        if o2_left_for_wwtp_tpd > 0
        else 0.0
    )

    # Backup energy sizing
    # Full‑load average electrical power in kW
    full_load_kW = elec_MWhpd_req * KW_PER_MW / HOURS_PER_DAY

    # Critical load as fraction of that full‑load power
    critical_load_kW = i.critical_load_fraction * full_load_kW

    # Total backup energy for the specified number of days (MWh)
    e_backup_MWh = critical_load_kW * HOURS_PER_DAY * i.backup_days / KW_PER_MW

    flywheel_MWh = 0.1 * e_backup_MWh
    nh3_backup_MWh = 0.9 * e_backup_MWh

    nh3_genset_kWh_per_kg = 5.17 * 0.35  # NH3 LHV × net elec eff
    nh3_for_backup_per_outage_event = (
        nh3_backup_MWh * KW_PER_MW / nh3_genset_kWh_per_kg
    )

    # What AN could power/electrolyzer limits support?
    an_max_by_electricity = (
        elec_avail / elec_MWh_per_t_AN if elec_MWh_per_t_AN > 0 else None
    )
    an_max_by_h2 = (
        (h2_cap_kgpd / H2_KG_PER_T_AN) if h2_cap_kgpd is not None else None
    )
    bottleneck = "n/a"
    if an_max_by_electricity is not None and an_max_by_h2 is not None:
        bottleneck = (
            "electricity" if an_max_by_electricity <= an_max_by_h2 else "electrolyzer"
        )
    elif an_max_by_electricity is not None:
        bottleneck = "electricity"
    elif an_max_by_h2 is not None:
        bottleneck = "electrolyzer"

    return {
        # Drivers and bottlenecks
        "AN_tpd": an,
        "Electricity_available_MWhpd": elec_avail,
        "Electrolyzer_cap_MW": i.electrolyzer_power_MW or 0.0,
        "AN_max_by_electricity_tpd": an_max_by_electricity or 0.0,
        "AN_max_by_electrolyzer_tpd": an_max_by_h2 or 0.0,
        "Bottleneck": bottleneck,
        "Electricity_required_MWhpd": elec_MWhpd_req,
        "Electricity_surplus_MWhpd": elec_surplus,  # negative = deficit
        "HB_aux_MWhpd": hb_aux_MWhpd,
        "Acid_aux_MWhpd": acid_aux_MWhpd,
        "H2_required_kgpd": h2_kgpd,
        "H2_cap_kgpd": h2_cap_kgpd or 0.0,
        "H2_surplus_kgpd": (h2_surplus_kgpd if h2_surplus_kgpd is not None else 0.0),
        # Reagents / products
        "NH3_total_tpd": nh3_total_tpd,
        "HNO3_tpd_100pct": hno3_tpd,
        "N2_tpd": n2_tpd,
        # O2
        "O2_tpd_from_electrolyzers": o2_tpd,
        "O2_tpd_needed_for_acid": o2_needed_for_acid_tpd,
        "O2_coverage_fraction_for_acid": o2_acid_coverage,
        "O2_tpd_left_for_WWTP": o2_left_for_wwtp_tpd,
        "WWTP_flow_supported_m3pd": wwtp_flow_supported_m3pd,
        # Heat and water
        "El_waste_heat_MWhth_pd": el_waste_MWhth_pd,
        "HNO3_steam_MWhth_pd": hno3_steam_MWhth_pd,
        "MED_water_m3pd": med_m3pd,
        "MED_feed_m3pd": med_feed_m3pd,
        "MED_brine_m3pd": med_brine_m3pd,
        # Salts / binder
        "Salts_from_MED_feed_tpd": tds_tpd,
        "NaCl_tpd_potential": nacl_tpd,
        "Mg_kgpd_in_feed": mg_kgpd,
        "Mg_captured_kgpd": mg_captured_kgpd,
        "MgOH2_kgpd": mgoh2_kgpd,
        "Mg_binder_tpd": binder_tpd,
        "CO2_uptake_tpd_potential": co2_uptake_tpd,
        # RO from surplus electricity (optional)
        "RO_water_m3pd": ro_m3pd,
        # Backup split
        "Backup_energy_MWh_total": e_backup_MWh,
        "Critical_load_kW": critical_load_kW,
        "Critical_load_fraction": i.critical_load_fraction,
        "Backup_days": i.backup_days,
        "Flywheel_energy_MWh": flywheel_MWh,
        "NH3_backup_energy_MWh": nh3_backup_MWh,
        "NH3_for_backup_per_outage_event_kg": nh3_for_backup_per_outage_event,
        # Per‑t AN intensities (for charts/sanity)
        "Elec_MWh_per_t_AN": elec_MWh_per_t_AN,
        "El_waste_MWhth_per_t_AN": el_waste_MWhth_per_t_AN,
        "HNO3_steam_MWhth_per_t_AN": hno3_steam_MWhth_per_t_AN,
        "H2_kg_per_t_AN": H2_KG_PER_T_AN,
    } # type: ignore


if __name__ == "__main__":
    def br(num: int = 25):
        return print("-"*num)
    
    # Examples
    # 1) Drive only by electricity (back-solve AN)
    ex1 = Inputs(available_electricity_MWh_per_day=120.0, electrolyzer_power_MW=1.0)
    print("— From electricity + electrolyzer cap —")
    for k, v in size(ex1).items():
        print(f"{k}: {v}")

    br()

    # 2) Drive by AN and see surpluses/deficits
    ex2 = Inputs(an_tpd=5.0, available_electricity_MWh_per_day=100.0, electrolyzer_power_MW=0.9)
    print("\n— From AN target —")
    for k, v in size(ex2).items():
        print(f"{k}: {v}")
    
    br()
    
    # 3) Micro-model, smallest viable plant 1 tonne per day    
    micro = Inputs(an_tpd=1.0)
    print(size(micro))
    
    br()
    
    # 4) Community-sized model, most viable to poor countries or low populated regions to get started, then build more over time since emissions aren't limiting
    community = Inputs(
        an_tpd=5.0,
        available_electricity_MWh_per_day=25.0,  # gives us some margin
        electrolyzer_power_MW=0.9,               # matches the first concept diagram
    )
    print(size(community))
    
    br()
    
    # 5) Regional-sized model, industrial scale for metropolitan or wealthy nations
    regional = Inputs(an_tpd=20.0)
    print(size(regional))
    
    br()