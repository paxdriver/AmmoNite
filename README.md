# Integrated Ammonium Nitrate, Water, and Resource Recovery Facility  
_A systems‑engineering concept for circular industrial symbiosis with municipal wastewater plants_

---

## Purpose

This project explores and models a **modular, low‑emission industrial facility** that produces
- **Ammonium nitrate (AN)** fertilizer,  
- **Potable water**,  
- **Oxygen** for wastewater aeration, and  
- **Magnesium‑based construction binders** from seawater brine—  
while operating primarily on **renewable electricity** and using **local waste heat and CO₂** as resources.

The repository documents the chemistry, mass‑energy flows, sizing logic, and economic framework for a minimum‑viable plant co‑located with a municipal wastewater treatment plant (WWTP).  
All tools and files here support feasibility assessment and open technical discussion, not detailed engineering design.

---

## Vision

**Turn wastewater, seawater, renewable power, and atmospheric nitrogen into a self‑sustaining source of clean water, fertilizer, and building material—without fossil fuels.**

Key goals:

1. **Close the loop between municipal and industrial systems**  
   - Use renewable O₂ for WWTP aeration.  
   - Capture digestor CO₂ for binder carbonation.  
   - Exchange low‑grade and medium‑grade heat streams.

2. **Demonstrate full process symbiosis**  
   - Electrolytic hydrogen and nitrogen feed Haber‑Bosch ammonia.  
   - Ammonia feeds the Ostwald nitric unit; nitric steam drives desalination.  
   - Brine becomes Mg(OH)₂ → Mg‑binder for eco‑cement applications.  
   - Only treated gases and benign brine leave the site.

3. **Prove financial sustainability through by‑product utilization**  
   - Surplus brine sold as winter road salt.  
   - Construction binder offsets Portland cement emissions.  
   - Potable water supplements community supply.  
   - Fertilizer and chemical outputs provide steady revenue.

4. **Open‑source transparency**  
   - Publish conservative, traceable calculations.  
   - Allow others to replicate and improve the techno‑economic model.

---

## Repository Structure

```text
├── README.md                ← this file
├── docs/                    ← concept notes, diagrams, design briefs
├── modeling/
│   ├── an_module_sizer.py   ← main parameterized sizing model (MVP baseline)
│   ├── examples/            ← example runs and CSV outputs
│   └── data/                ← default constants (densities, efficiency tables)
├── economics/
│   ├── opex_capex_model.xlsx
│   └── sensitivity_analysis.ipynb
└── references/
    └── publications.md      ← citations, patents, and background literature
```

---

## How It Works (Concept Summary)

1. **Electrolysis & Air Separation**  
   Renewable electricity splits water into hydrogen and oxygen, and a PSA unit extracts nitrogen from air.

2. **Haber–Bosch Process**  
   \( N₂ + 3H₂ → 2NH₃ \) at 350–450 °C, 150–250 bar.  
   The exothermic reaction generates heat reused elsewhere.

3. **Ostwald Process**  
   \( NH₃ + 2O₂ → HNO₃ + H₂O \).  
   Hot gas conversion and absorption yields nitric acid and recoverable steam.

4. **AN Neutralization**  
   \( NH₃ + HNO₃ → NH₄NO₃ \).  
   The product is crystallized or granulated as fertilizer.

5. **Desalination**  
   Multi‑effect distillation (MED) uses steam and electrolyzer waste heat to purify seawater, producing potable water and concentrated brine.

6. **Brine Valorization**  
   Seawater brine is treated to precipitate magnesium hydroxide for carbon‑negative construction materials and to store or sell NaCl for winter de‑icing.

7. **Integration with WWTP**  
   - Surplus O₂ replaces part of the aeration blower demand.  
   - WWTP CO₂ and digestor heat aid binder carbonation and ancillary heating.  
   - Shared utilities minimize infrastructure duplication.

8. **Energy Management**  
   - A small ammonia‑fueled generator and a flywheel system provide backup power.  
   - Sensible heat in rock/sand beds smooths diurnal load mismatch.

---

## Current Deliverables

- **`an_module_sizer.py`** — Parametric calculator for sizing hydrogen, ammonia, nitric acid, desal, and brine/binder subsystems.
- **Conservative CAPEX/OPEX estimates** — Equipment and daily operating costs designed to appear loss‑making for rigorous sensitivity testing.
- **Block diagram data** — Stream quantities and cost notes to integrate into process flow illustrations.

---

## Next Steps

1. Finalize the **MVP flow diagram** annotated with cost and chemistry notes.  
2. Refine **energy and O₂ sharing ratios** with a real WWTP data set.  
3. Prototype Mg‑binder formulations using local seawater brine.  
4. Publish open data on performance and update this repository’s models.  
5. Evaluate green‑credit and fertilizer‑offtake pathways.

---

## Disclaimer

This repository is a **conceptual and educational project**.  
It does **not** constitute chemical plant design documentation.  
Real‑world implementation requires full professional process safety, environmental, and engineering reviews.

---

## License

This work is released under the **MIT License** unless otherwise noted.
See [LICENSE](LICENSE) for details.

---

## Contributors

- **Lead Concept & Integration** – _Master_  
- **Process Modeling & Documentation** – _T3 Chat (AI collaborator)_

Contributions, pull requests, and independent validations are welcome.