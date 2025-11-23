# Integrated Ammonium Nitrate, Water, and Resource Recovery Facility  
_A systems‑engineering concept for circular industrial symbiosis with coastal communities_

---

## Purpose

This project explores and models a **modular, low‑emission industrial facility** that produces:

- **Ammonium nitrate (AN)** fertilizer (primary objective)  
- **Potable water** from seawater  
- **Magnesium‑based construction binders** from brine  
- **Surplus oxygen** for wastewater treatment (when available)

The plant is intended for **sunny, arid coastal regions** (e.g., Sahel, Horn of Africa, Arabian Peninsula, Pacific islands) where:

- Seawater and sand/rock/salt are plentiful,
- Fresh water and fertilizer are scarce,
- Skilled maintenance and complex supply chains are limited.

The facility is designed to run primarily on **solar‑derived heat and electricity**, using **local sand/rock/salt as thermal storage media**, and to operate with **minimal fossil inputs**.

This repository currently focuses on **first‑pass sizing and mass‑energy balances**, not detailed engineering.

---

## Vision

**Turn seawater, sunlight, local sand, and atmospheric nitrogen into a self‑sustaining source of fertilizer, water, and building material — with minimal emissions and maximal local ownership.**

Key goals:

1. **AN‑anchored design**

   - Ammonium nitrate output (t/day) defines all major process flows.  
   - The plant’s **own process needs are always prioritized** (H₂, O₂, heat, water).  
   - Surpluses (water, O₂, salts, binders) are offered to adjacent users only after AN production and plant reliability are secured.

2. **Simple, modular, locally maintainable**

   - Prefer sand/rock/salt beds and simple reflectors over exotic thermal storage.  
   - Avoid large, complex wind turbines and specialty materials where possible.  
   - Design around **repeatable modules** (e.g., 1 t/d, 5 t/d, 20 t/d AN) that can be replicated as demand and local skills grow.

3. **Circular integration with wastewater and the local community**

   - Co‑locate with a municipal WWTP where feasible.  
   - Use surplus O₂ (when available) for WWTP aeration.  
   - Use WWTP CO₂ and low‑grade heat to aid Mg‑binder carbonation and ancillary heating.  
   - Provide potable water and fertilizer to nearby farms and settlements.

4. **Low‑emission energy management**

   - Solar reflector fields pre‑heat sand/rock/salt beds that supply process heat to Haber–Bosch, Ostwald, and desalination.  
   - Modest PV and/or mechanically simple wind‑driven flywheels may supplement electricity.  
   - An ammonia‑fueled genset covers **multi‑day reduced‑load operation** when sun is insufficient, without depending on diesel or grid fuel.

5. **Open, conservative modeling**

   - Use conservative, traceable assumptions (energy intensities, recoveries, compositions).  
   - Make the trade‑offs between AN output, water, and by‑products explicit.  
   - Provide a transparent basis for others to critique, extend, or adapt the design.

---

## Process Concept (High‑Level)

1. **Electrolysis & Air Separation (ELEC)**  
   - Solar‑derived electricity splits water into **H₂ + O₂**.  
   - A simple air separation system supplies **N₂** (and optionally part of the O₂ demand).  
   - Recoverable low‑grade heat from the electrolyzer is sent to desalination.

2. **Haber–Bosch Ammonia (HB)**  
   - \( N₂ + 3H₂ → 2NH₃ \) at high temperature and pressure.  
   - Waste heat is captured into the thermal storage system for re‑use.

3. **Ostwald Nitric Acid (HNO₃)**  
   - \( NH₃ + 2O₂ → HNO₃ + H₂O \).  
   - Electrolyzer O₂ is used **first** to meet nitric acid O₂ demand; air makes up any shortfall.  
   - Steam from the nitric unit provides medium‑grade heat to desalination.

4. **Ammonium Nitrate Neutralization (AN)**  
   - \( NH₃ + HNO₃ → NH₄NO₃ \) (solid or solution).  
   - This node is the **anchor**: specifying AN t/day fixes upstream H₂/N₂ requirements and downstream water/brine/binder flows.

5. **Multi‑Effect Distillation (MED)**  
   - Uses **nitric steam + electrolyzer waste heat** to distill seawater.  
   - Produces potable water and a concentrated brine.

6. **Brine Handling & Mg‑Binder Production**  
   - Brine is split into:
     - **NaCl‑rich stream** (road salt / industrial salt), and  
     - **Mg‑rich stream** precipitated as Mg(OH)₂, then converted into **Mg‑based binder** that can uptake CO₂.  

7. **WWTP Integration (optional but encouraged)**  
   - Surplus O₂ (after acoustic/process needs) can reduce WWTP aeration energy.  
   - WWTP CO₂ and digestor heat support binder curing and low‑temperature heating loops.  
   - Shared intakes/outfalls reduce duplicated civil works.

8. **Backup & Load Management**

   - A small **NH₃‑fueled generator** and a **flywheel** provide ride‑through power for essential loads.  
   - Thermal storage in sand/rock/salt beds keeps process temperatures stable during solar fluctuations.  
   - Backup capacity is sized as a **fraction of full plant load for several days**, not just a short outage.

---

## Phase 1: Sizing & System Anchoring (Completed)

The first phase of this project focuses on **mass‑energy balance and basic sizing** around AN output.

### `AN_system_anchoring_sizer.py`

This script is the core tool for Phase 1. It:

- Takes as **drivers** any combination of:
  - Target AN production (`an_tpd`),  
  - Available electricity (MWh/day),  
  - Electrolyzer nameplate capacity (MW).

- Computes, on a **per‑day basis**:
  - Minimum electricity required to support that AN rate.  
  - H₂, NH₃, HNO₃, N₂, and O₂ flows.  
  - Recoverable low‑grade (electrolyzer) and medium‑grade (nitric) heat.  
  - MED desalinated water, feed volume, and brine volume.  
  - Salts from brine (NaCl), Mg(OH)₂ production, Mg‑binder output, and potential CO₂ uptake.  
  - Surplus electricity that could drive RO desalination.  
  - Surplus O₂ that could support WWTP aeration (after nitric acid O₂ needs are met).  
  - Backup energy requirements:
    - Choose a **fraction of full plant electrical load** and a **number of days** of autonomy;  
    - The script sizes the total backup MWh, splits between flywheel and NH₃ genset, and returns the **NH₃ inventory per outage event**.

- Reports **bottlenecks**:
  - Whether AN rate is limited by electricity or electrolyzer capacity.  
  - Maximum AN possible given one constraint while holding the other fixed.

- Provides **per‑ton‑AN intensities** for key variables (MWh/t AN, m³ water/t AN, t salts/t AN, etc.), which are used to reason about modular scaling (e.g., 1 t/d vs 5 t/d vs 20 t/d).

This script is intentionally **conservative**: it leans toward higher energy use and lower recoveries to avoid optimistic bias.

---

## Transition to Phase 2: Geometry & Equipment Sizing

With Phase 1 complete, we now have:

- Order‑of‑magnitude **AN production levels** for a micro plant (~1 t/d), a community module (~5 t/d), and a regional module (~20 t/d).  
- Corresponding **flows of water, heat, salts, Mg‑binder, and backup NH₃**.  

Phase 2 will use these outputs to size **actual equipment and geometry**, and to visualize the plant.

Planned work:

1. **Blender‑based 3D components**

   - Build parametric models of major hardware:
     - Electrolyzer skids  
     - HB and Ostwald reactors and associated vessels  
     - AN neutralizer and storage  
     - MED units and brine tanks  
     - Mg‑binder reactors and curing areas  
     - Thermal storage beds (sand/rock/salt)  
     - Solar reflector fields (area and layout)  
   - Use outputs from `AN_system_anchoring_sizer.py` to drive Blender scale (e.g., tank volumes, field area).

2. **Equipment sizing script (Phase 2 tool)**

   - A new Python module will:
     - Import `AN_system_anchoring_sizer`.  
     - Run a scenario (e.g., 5 t/d AN, 25 MWh/d renewable input, 0.9 MW electrolyzer).  
     - Convert flows and energies into **equipment sizes**, such as:
       - Tank diameters and heights  
       - Thermal storage bed volume and mass of sand/rock/salt  
       - Solar reflector count and land area  
       - Brine storage capacity and loading throughput  
       - Flywheel and NH₃ tank sizes for specified backup days
   - This creates a **chain**: scenario → sizer outputs → equipment sizing → Blender visualization.

3. **Refined layout concepts**

   - Use Blender scenes to explore:
     - Compact vs spread‑out layouts for different sites.  
     - Co‑location patterns with existing WWTPs.  
     - Access paths, brine outfalls, and solar field arrangement.

4. **Iterative refinement**

   - Feed any geometric or practical constraints (e.g., maximum reasonable tank height, land availability) back into the sizer assumptions.  
   - Adjust the modular base size (1 t/d vs 5 t/d) for different deployment contexts.

---

## Future Phases (Beyond Phase 2)

- Integrate simplified **CAPEX/OPEX models** tied directly to equipment counts and sizes.  
- Explore **local manufacturing pathways** for sand/rock/salt thermal storage and Mg‑binder production.  
- Investigate **policy and financing mechanisms** for deploying multiple modules in poorer coastal regions.  
- Add optional modules for **simple mechanical wind capture** feeding flywheel storage, if and when that design is matured.

---

## Disclaimer

This repository is a **conceptual and educational project**.  
It is **not** chemical plant design documentation and is **not** sufficient for construction, permitting, or operation.

Any real‑world implementation would need:

- Full process design by qualified engineers,  
- Hazard and operability (HAZOP) studies,  
- Environmental impact assessments,  
- Regulatory and safety reviews appropriate to the jurisdiction.

---

## License

This work is released under the **MIT License** unless otherwise noted.

---

## Contributors

- **Lead Concept & Integration** – Kristopher Driver