# Process Overview
1 - Sun → heat + electricity
Solar field heats a sand/rock bed and powers the electrolyzers

2 - Electricity + water + air → H₂ + N₂ + O₂
Electrolyzers make H₂ and O₂. PSA/membrane separates N₂ from air

3 - H₂ + N₂ → NH₃ (Haber‑Bosch)
Iron catalyst, high pressure, high temperature, recycle loop

4 - NH₃ + O₂ → HNO₃ (Ostwald)
Platinum/rhodium gauze, then absorption in water, steam generation

5 - NH₃ + HNO₃ → AN
Neutralization and crystallization → product AN

6 - Nitric + electrolyzer heat → MED → water + brine
Multi‑effect distillation makes fresh water and concentrated brine

7 - Brine → Mg(OH)₂ → binder + NaCl
Precipitate Mg, turn into binder, stockpile salt

8 - O₂ / CO₂ integration with WWTP, NH₃ backup
Some O₂ to WWTP aeration when available; NH₃ stored as backup fuel

---

# Shorthand References
MED = Multi-Effect Distillation<br>
PSA = Pressure Swing Adsorption<br>
PEM = Proton Exchange Membrane<br>

---

1. ## Solar field and thermal storage

### What it does

- Solar field focuses sunlight onto a receiver (on or near the sand tank).
- Hot fluid (air, or a simple heat‑transfer oil/water loop) carries heat into the sand/rock/salt bed.
- The bed stores heat over hours to days.

During operation, that heat is drawn off to:
    - preheat process gases (Haber‑Bosch feed),
    - generate or boost steam for MED,
    - keep temperatures stable through cloudy periods.


### How it operates

Daily cycle:
1. Morning charge
	- As sun rises, tracking mirrors focus light on the receiver.
	- A circulation fan or pump runs a loop:
		- receiver → sand bed → back to receiver.
	- Gradually raises bed temperature (maybe 100–300 °C range, by design).

2. Day‑time steady
	- Bed is hot; some heat continues to accumulate.
	- A separate loop takes heat from sand bed to process heat exchangers (HB preheat, MED).

3. Evening / night
	- Solar input drops.
	- Sand bed discharges heat: process still gets a stable heat supply while bed temperature slowly falls.
	- Operators watch bed temperature and may ramp down plant if a long cloudy period is forecast.


### Equipment & materials:
- Sand/rock tank: reinforced concrete or steel shell + refractory/insulation inside (cheap bulk materials, high thermal mass, tolerant of high temperature)
- Receivers & piping: carbon steel or low‑alloy steel; some stainless where water/steam is involved.
- Fans/pumps: standard industrial units.

### Operator tasks:
- Start/stop circulation pumps based on sun/temperature.
- Monitor bed temperature trends in DCS (control system).
- Periodic inspection for insulation damage, leaks in piping, mirror alignment.

---

2. ## Electrolysis & air separation (ELEC)

2.1 Electrolyzers – how we get H₂ and O₂
    Principle: water electrolysis splits liquid water into hydrogen and oxygen using DC electricity.

Inside one electrolyzer module:
- Dozens of cells stacked together:
	- Cathode: hydrogen side.
	- Anode: oxygen side.
	- Membrane (PEM) or diaphragm separates gases so they don’t mix.
- Deionized water is fed to one side; under DC current:
	- At cathode: \(2 H₂O + 2e⁻ → H₂ + 2 OH⁻\) (or \(H⁺ + e⁻ → ½ H₂\) in PEM)
	- At anode: \(2 H₂O → O₂ + 4 H⁺ + 4 e⁻\)

Mechanism of action:
- Operators ensure DI water quality (low conductivity) from a polishing unit.
- Rectifiers convert AC from solar/bus to DC for the stack.
- As current flows, H₂ is generated on one side, O₂ on the other, along with heat.

Outputs for 5 t/d AN plant (approx):
- H₂: ~375 kg/day.
- O₂: ~3 t/day.

Materials:
- Cells: stainless steel or titanium bipolar plates; precious metal catalysts (Pt, Ir) on membranes in PEM units.
- Piping: stainless steel for O₂, carbon steel or SS for H₂.
- Skid frame: carbon steel.

Operations:
- Mostly automatic. Operators:
	- Monitor stack voltage, temperature, current.
	- Check deionized water levels.
	- Replace filters, check for leaks (H₂ detectors).


2.2 N₂ from air – PSA / membrane vs cryogenic

If you’re familiar with liquid nitrogen via large cryogenic air separation. For this scale (~5 t/d AN), that’s overkill.

For this application I recommend PSA (Pressure Swing Adsorption) or membranes, which are:
- Compact,
- Air‑fed,
- No liquefaction.

Order of magnitude requirement (5 t/d case):
- NH₃ production: 2.1 t/day.
- N mass fraction in NH₃ ≈ 0.824 → N₂ ≈ 1.75 t/day.
- Convert: 1.75 t/day ≈ 72.9 kg/h.

At ~1.25 kg/m³, ≈ 58 m³/h N₂ at ambient conditions.

This is tiny; PSA plants in this size are very standard.

PSA mechanism:
- Two vertical vessels filled with an adsorbent (e.g., carbon, zeolite).
- Air is compressed (to a few bar) and fed into vessel A.
- At that pressure, O₂, CO₂, H₂O stick to the adsorbent more strongly than N₂.
- The gas leaving the top of A is N₂‑enriched.
- While A is on‑line, vessel B is being regenerated the pressure is dropped, maybe a small purge is applied, so O₂, CO₂, H₂O desorb and are vented.
- After a short cycle (seconds–minutes), the valves switch: B becomes the production bed, A regenerates.

Result: essentially continuous N₂ stream from a pair of “breathing” towers.

Membrane option (for smaller plants):
- Hollow fiber membranes that let some gases pass faster (O₂, H₂O, CO₂) and retain more N₂.
- Less sharp separation than PSA but simpler.

Materials:
- Towers: carbon steel with internal lining or stainless, depending on dew‑point spec.
- Adsorbent: synthetic zeolite beads.
- Lines: carbon steel, instrumented with flow/pressure sensors.

Operators:
- Monitor compressor, filter cartridges, PSA cycle times.
- Replace adsorbent every few years.

---

3. Haber‑Bosch (NH₃ synthesis)

What happens chemically
- Reaction: \(N₂ + 3 H₂ ⇌ 2 NH₃\).
- Exothermic: releases heat.
- Favourable at high pressure and moderate temperature (~150–250 bar, 400–500 °C).

Mechanism & catalysts

Loop components:
1. Feed preparation:
	- PSA N₂ and electrolyzer H₂ are mixed in 1:3 mol ratio.
	- Dried, cleaned over a small guard bed (to remove O₂, CO, CO₂, H₂O, H₂S which poison catalyst).

2. Compression:
	- Gas compressed to operating pressure with a multi‑stage compressor.

3. Reactor:
	- Packed bed of iron catalyst, promoted with K, Al, etc.
	- Gas enters hot; reacts as it passes over catalyst:
		- N₂ triple bond is activated on iron surface.
		- H₂ dissociates.
		- Surface chemistry forms NH₃ which desorbs to the gas phase.

4. Cooling & separation:
	- Hot gas exits reactor, goes through heat exchanger (preheats incoming gas).
	- Further cooled; NH₃ condenses to liquid.
	- Liquid NH₃ drawn off; unreacted N₂ + H₂ recycled back.

At our modest scale, you’d likely run at the lower end of commercial pressures, maybe 80–100 bar, with tailored equipment.

Materials
- Reactor vessel: thick‑wall alloy steel for high pressure and temperature.
- Catalyst: iron‑based, supplied in pellets. Lifespan years, but can be partially rejuvenated.
- Piping: high‑pressure carbon or low alloy steel.

Operators
- Start‑up: careful heat‑up and pressure ramp to avoid thermal stress.
- Routine:
	- Monitor loop pressure, conversion, recycle ratio.
	- Check for H₂ leaks, lube oil systems.
	- Occasionally sample ammonia for purity.
- Maintenance:
	- Every few years: catalyst change‑out by specialists.
	- Compressor overhauls as scheduled.


Material handling is all gaseous/liquid via pipes and valves; no buckets.

---

4. Ostwald (Nitric Acid)

Chemistry in 3 main stages

1. NH₃ oxidation on Pt/Rh gauze:
	- \(4 NH₃ + 5 O₂ → 4 NO + 6 H₂O\) (at 800–900 °C).

2. NO oxidation in gas phase:
	- \(2 NO + O₂ → 2 NO₂\) (as gas cools).

3. NO₂ absorption in water:
	- \(3 NO₂ + H₂O → 2 HNO₃ + NO\) (NO is recycled).


Mechanism in equipment

1. Gas feed: NH₃ gas (from HB loop) plus O₂ / air.
	- In your concept, electrolyzer O₂ covers ~75% of O₂; the rest is air.

2. Burner / converter:
	- Mixture passes through a Pt/Rh wire gauze at ~900 °C.
	- Very rapid catalytic combustion → NO + steam.

3. Cooling & oxidation:
	- Hot NO+steam cooled in waste‑heat boiler (generates steam).
	- As gas cools, NO oxidizes to NO₂.

4. Absorption tower:
	- Tall column with stainless or lined internals.
	- Water / weak nitric acid streams trickle down over packing or trays.
	- NO₂ enters from bottom, contacts descending liquid:
		- Forms HNO₃ in solution.
	- Off‑gas (NO + some NO₂ + O₂) is partly recycled to the converter or sent to a tail‑gas treatment unit.

Materials

- Converter shell: high‑temperature alloy steel; Pt/Rh gauzes are precious and replaced periodically.
- Absorber: stainless steel 316L or nitric‑resistant alloy, rubber‑lined carbon steel is also used sometimes for cost.
- Piping: stainless for acid, carbon steel for air.


Operators

- Adjust NH₃:air/O₂ ratio to maintain catalyst temperature and conversion.
- Monitor tower temperature profile, acid strength, and NOₓ emissions.
- Periodic Pt gauze replacement (careful, expensive).

Again, everything is pumped or blown; operators don’t manually move acid.

---

5. AN Neutralizer, Crystallizer & Product Handling

Chemistry


Simple acid‑base:


- \(NH₃ (aq) + HNO₃ (aq) → NH₄NO₃ (aq)\).

Depending on water content and temperature, you either:


- Sell concentrated AN solution,

- Crystallize/pelletize solid AN.

Mechanism in plant

1. Neutralizer:
	- Stainless steel stirred tank.

	- Measured flows of ammonia solution and nitric acid solution join with enough water to control temperature.

	- pH and temperature kept in a narrow band to avoid runaway.


2. Concentration / crystallization:
	- Evaporator reduces water to reach desired concentration.

	- Crystallizer cools or flashes off water, forming AN crystals.


3. Solid handling:
	- Centrifuge or filter removes mother liquor.

	- Crystals go to dryer, then to silo or bagging line.


Materials & operations

- Vessels: stainless steel for corrosion resistance.

- Controls: temperature and pH critical; safety interlocks.

- Operators:
	- Monitor pH, acid/amm flows, watch for foaming or plugging.

	- Manage dryer, bagging machines, silo levels.


Solid AN is handled with screw conveyors and bucket elevators, not shovels, except perhaps for small cleanups.


---

6. MED Desalination

How Multi‑Effect Distillation works


Goal: Use steam + low‑grade heat from electrolyzers and Ostwald to boil seawater in a cascade of effects, each at lower pressure.


1. Effect 1:
	- Receives steam from nitric unit or a small boiler.

	- Steam condenses on tube side, heating seawater on shell side.

	- Some of the seawater evaporates; the vapour goes to effect 2, condensate becomes fresh water.


2. Effect 2:
	- Operates at lower pressure → lower boiling point.

	- Vapour from effect 1 condenses, heating more seawater; more vapour generated for effect 3.


3. … and so on:
	- You get more distilled water per unit of original steam.


Brine becomes more concentrated as it moves through effects and is eventually discharged or sent to Mg/salt recovery.

Materials

- Tubes: titanium or high‑grade stainless (chloride resistance).

- Shells: carbon steel, lined or coated where needed.

- Piping: duplex SS or PVC for brine.

Operators

- Control feed seawater flow, vacuum levels, and bleed‑off ratio (to control scaling).

- Periodic CIP (clean in place) to remove scale from tubes.

All flows are pumped; brine goes by pipe to storage / Mg system.


---

7. Mg Precipitation & Binder Production

Chemistry


Core idea: extract Mg from brine as Mg(OH)₂, then react it with CO₂ to form a Mg‑carbonate binder.


1. Precipitation:
	- Raise brine pH using a base (e.g., NaOH, Ca(OH)₂, or ammonia).

	- When pH passes ~9–10:
		- \(Mg^{2+} + 2 OH⁻ → Mg(OH)₂ (s)\)


	- Mg(OH)₂ forms fine solids.


2. Solid‑liquid separation:
	- Settling, thickening, or filtration to separate Mg(OH)₂ cake.


3. Binder formation / carbonation:
	- Mg(OH)₂ slurry or compacted solids exposed to CO₂ (from WWTP digesters, flue gas, or bottled CO₂).

	- Reactions (simplified):
		- \(Mg(OH)₂ + CO₂ → MgCO₃·xH₂O\)


	- Forms a solid binder similar to low‑temperature cement.


Materials & ops

- Precipitation tanks: FRP or coated carbon steel (brine + alkaline).

- Filters: plate‑and‑frame or belt filters.

- Carbonation reactors: stainless or concrete chambers; moderate temp/pressure.

Operators:


- Adjust base addition to get target pH and Mg recovery.

- Handle filter cake (augers or screws) to carbonation area.

- Monitor CO₂ flows and binder cure time.

This is where some manual / bulk handling might appear: front‑end loader moving cured binder, but not shovelling into vats continuously.


---

8. Brine & NaCl Handling


After MED and Mg precipitation:


- Remaining brine is rich in NaCl and other salts.

Two options:


1. Mechanical crystallization:
	- Further evaporation (using waste heat or solar ponds).

	- Crystals separated, washed, and dried.


2. Solar evaporation ponds:
	- Shallow ponds; sun/air evaporates water.

	- Salt crust harvested with mechanical scraper, loader.


Given your low‑emissions, low‑complexity goals, solar ponds + simple mechanical harvest are consistent.

Materials:


- Basins: lined earth ponds (HDPE or clay).

- Conveyors or loaders move crystals to NaCl pile.


---

9. WWTP Integration – O₂ & CO₂

O₂ to aeration

- When electrolyzer O₂ exceeds Ostwald demand, we have a surplus.

- That O₂ can be piped to the aeration basins of the WWTP:
	- Either bubble via diffusers (pure O₂ systems),

	- Or use as enrichment in aeration blowers.


- Benefit: lower blower power → less WWTP electricity use.

CO₂ to binder carbonation

- WWTP digesters generate biogas with CO₂ and CH₄.

- If some CO₂ stream is scrubbed or separated, it can be:
	- Piped to the binder carbonation reactors,

	- Or compressed/transported short distances if needed.


Operators coordinate with the WWTP to match O₂ and CO₂ flows, but the physical work is mostly valves and monitor screens.


---

10. NH₃ backup power

Concept

- You store a certain mass of liquid NH₃ (from HB intermediate).

- A small genset uses NH₃ as fuel:
	- Either directly in modified ICE,

	- Or cracked partly to H₂+N₂ then burned.


Operation:


- In a grid or solar shortfall:
	- NH₃ pump feeds engine.

	- Engine drives generator, producing electricity for critical loads (controls, pumps, some reactors).


- Exhaust heat can be recovered into the thermal loop.

Operators:


- Manage NH₃ tank inventory and refilling.

- Routine engine maintenance like any small power plant.

Materials:


- Bullet tanks of NH₃: carbon steel, relief valves, dike.

- Piping with proper ammonia valves and seals.


---

11. Day‑to‑day plant life


To answer your practical question: no one is walking around with wheelbarrows feeding vats.

Daily work is more like this:


- 
Control room operators:


	- Monitor SCADA / DCS for flows, pressures, temperatures.

	- Respond to alarms for off‑spec conditions.

	- Change setpoints (e.g., AN rate, desal rate) slowly over time.


- 
Field operators:


	- Do rounds: listen for pump noise, look for leaks, read local gauges.

	- Take manual samples (acid, AN, water, binder) for lab testing.

	- Start/stop individual skids (e.g., binder line, MED unit) if needed.


- 
Maintenance crew:


	- Mechanical techs handle pumps, valves, compressors, seals.

	- Electrical/instrument techs handle transmitters, PLC I/O, drives.

	- Periodic shutdowns for catalyst change‑outs (HB, Ostwald), MED descaling.


- 
Materials handling:


	- Loader and forklift drivers move solid binder, AN product, and salt.

	- Truck loading operators handle bagging or bulk loadouts.


The plant is mostly pumps, pipes, and automated trains. Manual work is focused on sampling, inspection, and bulk movement of solids, not feeding basic chemistry steps.














