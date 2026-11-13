---
title: "Bin Tug Rev G5 - [waste collector] bin compatibility (desk study)"
subtitle: "Which domestic bins the GH-B2 grabber and the G3 tug can take, and what it costs to cover the rest. Desk research + re-analysis of the G3 Monte Carlo. 8 November 2026."
geometry: margin=1.8cm
fontsize: 9pt
colorlinks: true
toc: true
toc-depth: 2
---

# 0. Answers first

**[waste collector] gives houses only two-wheel 140 L and 240 L wheelie bins plus a 25 L kerbside caddy.** It does not list 80 L, 120 L, 360 L, 660 L or 1100 L bins for households (sections 1.1-1.2).

| [waste collector] domestic container | Verdict for the G3 tug (GH-B2) |
|---|---|
| 240 L general waste (green, or black / burgundy) | **HANDLED** |
| 240 L recycling (blue) | **HANDLED** |
| 140 L general waste (Xtralite plan) | **HANDLED** |
| 140 L recycling (Xtralite plan) | **HANDLED** |
| 140 L brown organic ([nearby city] City + suburbs, [nearby town]; Terra plans) | **HANDLED** |
| 25 L caddy (glass in [nearby city] City + suburbs, food waste elsewhere) | **NOT HANDLED** (it has no wheels and no rear bar; it is carried by its handle) |

**Coverage:**

* **100 % of the [waste collector] wheeled bin types (5 of 5)** sit inside the envelope that GH-B2 was tested on.
* **83 % of all [waste collector] domestic container types (5 of 6).** The 25 L caddy is the one left out.
* **Per household, counted by containers:** a rural "Country Standard" house (240 L waste + 240 L recycling + 25 L food caddy) is **2 of 3 (67 %)**. A [nearby city] City / [nearby town] "City Standard" house (240 + 240 + 140 L brown + 25 L glass caddy) is **3 of 4 (75 %)**.
* **Per household, counted by volume:** about **95-96 %** is covered (480 of 505 L, or 620 of 645 L).

"Handled" means the bin's published geometry falls inside the G3 test envelope. It does **not** mean every grab works. The G3 Monte Carlo was re-cut to the geometry that matches [waste collector] bins: 200 mm wheels, bar 0.98-1.06 m, bar section 36 mm or less. On that slice GH-B2 captures **93 % of the time including one re-dock (27 of 29 runs; 66 % on the first try)**. The figure is **95 % for 140 L-class bins**. It drops to **61 % if the actual bars are moulded sections of 37 mm or more** (section 4).

**Recommended changes, in order:**

1. **Site survey of Brian's own [waste collector] bins (EUR 0-15).** Measure the bar section, the bar height, the hand gap, the spacing between the handle webs and the wheel size. Read the maker and the date: EN 840-1 cl. 9.1 requires both to be marked on the body. This one step decides whether change 3 is needed at all.
2. **Mass interlock in firmware (EUR 0).** Use the K5 tilt-current sensing that is already in the BOM to refuse to tow any bin estimated above ~110 kg gross. This makes a 360 L bin (other collectors) or an over-filled bin safe by default.
3. **Only if the survey finds moulded bars of 37-42 mm: a GH-B4 hook candidate (about EUR 40-60 in parts, plus a targeted Monte Carlo).** Thinner lip top, throat 48 -> 52 mm, pawl blade extended. The re-dock also approaches from a different mast angle. This is **not verified**. It must pass the same acceptance rule as GH-B3: clear the large-bar misses with no new false positives.
4. **25 L caddy:** ask [waste collector] to swap it for a **140 L brown wheelie bin** (EUR 0 hardware; a per-lift price difference may apply). The fallback is a caddy cradle on the tug (about EUR 25-45). It only works if the tug waits at the kerb until the crew has emptied the caddy.

**360 L bins (Barna, Panda, KWD; not [waste collector] domestic):** the handle geometry fits. A **full** 360 L (up to ~160 kg gross) is outside the 108 kg tow design. It is handled "with change": the interlock (EUR 0) covers light loads such as recycling. Full loads need a heavier actuator, more ballast and a 25 mm step rule, about **EUR 200-400 + re-simulation** (section 5). **660 L / 1100 L four-wheel bins are commercial, are not offered to [waste collector] households, and are out of scope.**

# 1. [waste collector]'s domestic bins

## 1.1 What [waste collector] lists for households

| Container | Sizes | Colour (body / lid) | Plans and areas | Source |
|---|---|---|---|---|
| General waste | **240 L / 140 L** | green, "also available in black or burgundy" (FAQ: "black or wine") | 240 L on Standard, Lite, TerraUrban, TerraKildare; 140 L on Pay-Per-Lift (Xtralite) | [household page]([waste collector website]), [FAQ Q18]([waste collector website]), [quote page]([waste collector website]) |
| Recycling | **240 L / 140 L** | blue | as above | same |
| Organic (brown) | **140 L** ([nearby city] City + suburbs, [nearby town]; Terra plans) **or 25 L** ("route dependant") | brown | City Standard / City Lite / Xtralite city: 140 L; Country plans: 25 L | same |
| Glass | **25 L caddy** ([nearby city] City + suburbs only) | photo: green caddy, glass label | City plans; free per lift | same |
| Home composter | on request | - | not collected | household page |
| Kitchen caddy | 5 L, indoor | - | free on some plans | quote page |

What the plans contain, from the [quote page]([waste collector website]):

* **Household Standard (City):** 240 L waste + 240 L recycling + 140 L organic + 25 L glass.
* **Household Standard (Country):** 240 L waste + 240 L recycling + 25 L organic.
* **Lite:** the same as Standard, priced per lift.
* **Pay Per Lift (Xtralite):** the 140 L versions (140 L waste, 140 L recycling, 140 L or 25 L organic).
* **TerraUrban / TerraKildare:** 240 + 240 + 140 L organic.

Weight allowances per lift are 20-25 kg for waste and 15 kg for recycling. The Standard plan has a 300 kg per 6 months limit. Both are far below the 0.4 kg/L EN 840 design load.

**No 80 L, 120 L, 360 L, 660 L or 1100 L bin appears on any [waste collector] household page or plan.** The [commercial page]([waste collector website]) also lists only 140/240 L and 25 L. [waste collector]'s site does have orphan image pages named "Wheelie Bin 1100L Blue" and "1100-litre-wheelie-bin green" ([1]([waste collector website]), [2]([waste collector website])). These are commercial. **660/1100 L bins are therefore out of scope**, as the brief assumed.

## 1.2 How common each size is in [county] / [nearby city] (inferred)

[waste collector] does not publish a split. The following is **inferred** from the plan structure:

* The headline "Household Standard" plan (EUR 27/month intro) and the Lite plan both issue **240 L** waste and recycling bins. 240 L is therefore the default and almost certainly the most common size.
* **140 L** waste and recycling bins come only with the pay-per-lift Xtralite plan, which is aimed at small households.
* The **brown 140 L** goes to [nearby city] City + suburbs and [nearby town]. Elsewhere, including rural [county], households get the **25 L** organic caddy.
* **[village]:** whether it is on a "[nearby city] City and suburbs" route or a Country route is not stated anywhere public. Brian's welcome pack or the bins themselves will show it.

[waste collector] serves ~37,000 households ([home page]([waste collector website])). It is permitted for [county] and [nearby city] and appears on [IWMA's [county] list](https://iwma.ie/household-waste/iwma-members-in-your-area) alongside Clean Ireland and AES/Bord na Mona.

## 1.3 Manufacturer / model

**Not published by [waste collector].** The [household photo]([waste collector website]) shows a 240 L green body with a black lid, a narrow brown 140 L, a blue 240 L and a green 25 L glass caddy, all with [waste collector] stickers. The maker cannot be identified from the photo, so I have not guessed one.

* **Likely candidates.** These are the brands distributed or made for the Irish market:
  * Craemer and Weber, via MES Ireland, the Laois distributor that also handles Taylor. MES says the Craemer range is "tried and tested on the Irish market" with "30 mm diameter ergonomic handles" ([MES partner page](https://www.midland-environmental.ie/company/about-us), [MES catalogue](https://rubbermaid.ie/wp-content/uploads/2023/09/MES-Product-Catalog-A4.pdf)).
  * MGB Plastics / One51 (Irish-owned, with sites in the UK and Ireland: [letsrecycle](https://www.letsrecycle.com/news/investments-see-market-success-mgb-plastics/)).
  * ESE and SULO (Plastic Omnium).
* **How to settle it:** EN 840-1 cl. 9.1 requires every compliant bin to be durably marked on the body with EN 840-1, the nominal volume, the **manufacturer's name or trademark**, the total permissible mass and the **year and month** of manufacture ([EN 840-1:2012 text](https://kievspecteh.com/sites/default/files/technic-files/evropeyskiy-standart-en-840-1-2014.pdf)). Reading that marking on Brian's bins answers this question in a minute.

# 2. Bin data (EN 840 and manufacturer data sheets)

## 2.1 EN 840 rules that matter to the grabber

| Rule | Value | Source |
|---|---|---|
| Handle clearance | **>= 36 mm all round** the handle, handle length >= 120 mm | EN 840-6 cl. 5.2 ([iTeh sample](https://cdn.standards.iteh.ai/samples/62796/fc341dcb68de42b79347dfba011f1ca5/SIST-EN-840-6-2020.pdf), [BS EN 840-6:2004](https://www.sturdyproducts.com/wp-content/uploads/2020/10/BS-EN-840-6.2004.pdf)) |
| Handle height (upright, centre of handle) | **875-1300 mm** (900 +400/-25); >= 800 mm when tilted, for bins >= 140 L | EN 840-6 cl. 5.3 |
| Handle section | one of the forms in EN 840-6 Fig. 1 (round, ring or U); no diameter is fixed | EN 840-6 cl. 5.2 |
| Nominal load | **0.4 kg/L** x nominal volume (120 L: 48 kg; 140 L: 56 kg; 240 L: 96 kg; 360 L: 144 kg) | EN 840-1 cl. 6 |
| Wheel | 200 mm (dim 11, "larger wheels accepted"); 100 kg static per wheel | EN 840-1 Tables 2/3, cl. 5.4 |
| Width (dim 1) | 140 L: 505 max; 240 L: 580 +/-5; 340 L: 665 max | EN 840-1 Tables 2/3 |
| Height incl. lid handles (dim 4) | 140 L / 240 L: 1100 max; 340 L: 1115 max | EN 840-1 Tables 2/3 |
| Depth (dim 3) | 140 L: 555 max; 240 L: 740 max; 340 L: 880 max | EN 840-1 Tables 2/3 |

## 2.2 Published dimensions by size (ranges across makers)

All values are in mm and kg. "Bar height" is the handle centre height above the ground, upright. Only Plastik Gogic publishes it as a column; the others publish total and comb height. "Axle width" is overall width across the wheels.

| Size | Overall H | Overall W | Overall D | Bar (handle) height | Bar section | Wheel D | Axle width | Empty mass | Nominal load / max gross |
|----|---|---|---|-----|-----|---|---|---|---|
| **140 L** | 1030-1100 | 478-505 | 550-555 | ~1005 (Gogic 140 Std) | 28-30 typical (see 2.3) | 200 (250 opt.) | 478-484 | 9-11 | 56 / ~66-70 |
| **240 L** | 1003-1100 | 576-585 | 715-740 | ~1014-1015 (Gogic 240) | 28-30 typical (SULO: oval) | 200 (250 opt.) | 569-575 | 9.7-15.5 | 96 / ~106-110 |
| 120 L (not [waste collector]) | 930-1005 | 475-505 | 480-555 | **904-941** | 27-30 | 200 (250 opt.) | 478-483 | 8-9 | 48 / ~60 |
| 360 L (not [waste collector]) | 1090-1115 | 585-620 (SULO 370: 747) | 860-880 | ~1025 (Gogic 360 Urban) | ESE "large diameter" | 200 (300 opt.) | 525-570 | 15-19.8 | 144 / ~160-170 |
| 25 L caddy | ~400 | - | - | carry handle, no wheels | - | none | - | ~1-2 | - |
| 660 / 1100 L (commercial) | 1213-1463 | 1255-1375 | 772-1085 | push handles, trunnions | - | 4 castors 200 | - | 37.6-62 | 270-440 payload |

Row sources:

* **140 L**:
  * ESE CL 140: H 1030, W 480, D 553, comb 969, 9 kg, max 70 kg ([ESE 2-wheel brochure](https://www.ese.com/fileadmin/templates/files/Downloads/Broschueren/LL_2-wheel_ESE_EN.pdf)); axle 478 ([ESE operating instructions](https://www.ese.com/fileadmin/templates/files/Downloads/Dokumente/INSTRUCTION_MANUAL_ESE_GmbH_2-4_Wheel_EN.pdf)).
  * Weber 140: 1050 x 550 x 478, 10.0 kg ([Weber](https://www.w-weber.com/en/wheelie-bins.html)).
  * Craemer MGBplus/neo 140: 505 x 555 x 1100 max, 56 kg ([Craemer MGBneo](https://www.craemer.com/uk/wheelie-bins/mgbneo/mgbneo-120-360l)).
  * Plastik Gogic 140 Standard: handle 1005, tilted 828, axle 483 ([Gogic manual](https://plastikgogic.rs/wp-content/uploads/2024/01/User-manual.pdf)).
* **240 L**:
  * ESE CL 240: 1003 / 580 / 738, comb 938, 11 kg. ESE SL 240: 1079 / 583 / 737, comb 1005, 13 kg, max 110; axle 569.
  * Weber 240: 1067 x 720 x 576, 11.7 kg.
  * SULO Citybac 240: 1068-1075 / 582-583 / 728-734, comb 991-998, 12.3 kg, max 110 ([SULO data sheet](https://downloads.sulo.com/Solutions/Products/Citybac/240-L-HF/SULO-Datasheet-Citybac-240-L-HF-EN.pdf), [SULO brochure](https://downloads.sulo.com/Solutions/Products/Citybac/240-L-HF/SULO-Brochure-Citybac-240-L-EN.pdf)).
  * MGB Plastics 240: 1057 / 580 / 715, 9.7 kg ([MGB data sheet](https://egberttaylor.com/assets/uploads/2020/04/MGB-Plastics-240L-Wheelie-Bin-Datasheet-GCC_EN.pdf)).
  * Hoffmann 240: 1100 / 585 / 740, 14.9 kg ([Hoffmann](https://assets.hoffmann-group.com/d/2/5/b/d25b4052-d442-4080-b380-79bf2dec9661/dsh_en-gb_73670.pdf)).
  * Gogic 240: handle 1014-1015, tilted 834-839, axle 571.
  * ecostore.ie 240 sold in Ireland: 1070 / 585 / 740 ([ecostore.ie](https://www.ecostore.ie/p/240l-wheelie-bin/mgb240std)).
* **120 L**: ESE CL 120 932 / 480 / 553, 8 kg; Weber 120 930 x 550 x 475, 8.2 kg; Gogic 120 handle 904-941.
* **360 L**:
  * ESE SL 360: 1112 / 585 / 880, comb 1020, 15 kg, max 160; axle 570.
  * Weber 360: 1098 x 878 x 596, 18.9 kg, 300 mm wheel option.
  * Craemer MGBneo 360: 590 +/-20 / 880 / 1115, 144 kg.
  * SULO Citybac 370: 1092 / 800 / 747, 300 mm wheels, 19.8 kg, max 170 ([SULO 370](https://downloads.sulo.com/Solutions/Products/Citybac/390-L-HF/SULO-Datasheet-Citybac-370-L-HF_EN-web.pdf)).
  * Gogic 360 Urban: handle 1025, axle 525.
* **25 L caddy**: Craemer "Kerbside bin 23 L, one-piece carry handle" ([Craemer folder](https://www.craemer.com/Website-Content/09_Downloads/UK/BranchenfolderMGB_2024_EN-UK_final_web.pdf)); [waste collector] photo.
* **660 / 1100 L**: ESE 4-wheel table; Weber 660 1230 x 772 x 1371, 37.6 kg; 1100 FL 1330 x 1065 x 1375, 47.4 kg.

## 2.3 Handle bar section and handle-to-body gap

* **Published diameters:**
  * Craemer MGBneo: **30 mm** "ergonomic handle" ([Craemer](https://www.craemer.com/uk/wheelie-bins/mgbneo/mgbneo-120-360l), [MES catalogue](https://rubbermaid.ie/wp-content/uploads/2023/09/MES-Product-Catalog-A4.pdf)).
  * SSI Schaefer GMT Duron: **28 mm** "enlarged diameter" ([SSI](https://ssi-plastic.com/en/waste-technology-digital-solutions/disposal-containers/plastic-disposal-containers/gmt-duron-two-wheeler/)).
  * ESE small bins: **27 mm**. ESE SL: "large diameter", value not given ([ESE brochure](https://www.ese.com/fileadmin/templates/files/Downloads/Broschueren/LL_2-wheel_ESE_EN.pdf)).
  * SULO Citybac 240: "**oval, corrugated and bigger** handle bar", value not given ([SULO brochure](https://downloads.sulo.com/Solutions/Products/Citybac/240-L-HF/SULO-Brochure-Citybac-240-L-EN.pdf)).
* **Round tube vs moulded:** Weber states the rear handle "is formed together with the body ... in a single injection moulding process" ([Weber](https://www.w-weber.com/engl/2rad/240-handgriff.html)). On current EN 840 bins the bar is mostly an **integrally moulded, hollow, near-round or oval section**, not a separate steel tube. The G3 model represents a moulded bar as a **rectangular box** (sim_g3.py), which is a conservative stand-in for a rounded oval.
* **Handle-to-body gap:** EN 840-6 sets a minimum of **36 mm** clearance. No maker publishes the actual gap. G3 sampled 35-60 mm.
* **Spacing between the handle webs:** not published by most makers. SULO AU 240 L gives "F handle width ~400 mm" ([SULO AU](https://sulo.com.au/product/240-litre-container)). That is narrower than the 440-560 mm G3 assumed for 240 L, but inside the 340-420 mm range G3 tested for small bins at 95 % capture. With the hooks at +/-150 mm (plates to +/-155 mm) and +/-40 mm lateral float, any web spacing above ~330-340 mm leaves the plates clear of the webs.

# 3. Robot limits used (from RESULTS_G3_mech.md, GH-B2)

| Limit | Value | Where |
|---|---|---|
| Cup throat | **48 mm** (x -24..+24); lip 12 mm; takes **D25-42** bars; lip + throat = 60 mm = smallest hand gap (35) + smallest bar (25) | section 2.1 |
| Pawl | closes the cup mouth to < 25 mm | section 2.1 |
| Hooks | twin 10 mm plates at **+/-150 mm**; +/-190 mm did not fit 120-140 L (340-420 mm between webs) | section 2.1 |
| Float | -100 / +130 mm, ratchet, counter-spring +30 N; bar may arrive up to ~250 mm above the cup | section 2.1 |
| Lateral float | +/-40 mm on UHMW pads | section 1 |
| Tested bin envelope | 240 L: bar 0.98-1.10 m, webs 440-560 mm, 20 % on 250 mm wheels; 120-140 L: bar 0.95-1.00 m, webs 340-420 mm; tube D25-32 or moulded 30-42 mm; gap 35-60 mm | section 2.4 |
| Capture | 87 % incl. one re-dock (52 % first try); **6 misses on 38-42 mm moulded bars** (GH-B3 cleared 3 of them, plus 1 false positive -> rejected) | sections 0, 2.3 |
| Tow mass | full 240 L ~**108 kg**; 95 kg tug recommended | sections 0, 3, 5 |
| Step | **40 mm** sharp step PASS, 50/60 mm STALL (full bin, 95 kg); bin wheel climb, not traction, is the limit | section 3 |
| Tip | full bin to 20 deg within 60 s is actuator-limited (2.5 kN) | section 2.4 notes |
| Funnel / wheel stops | 650 mm flared funnel mouth, wheel-contact switches, anti-tip rollers moved to y = +/-460 mm | REVG_DESIGN, section 1 |

**Discrepancy noted:** RESULTS_G3_mech.md section 2.3 says GH-B2 had "0 false positives in 100 runs". However, `revG/sim/results_G3_mc_GH-B2.json` and the outcome table in section 2.4 both show **1 false positive** (run 14: tube D31, bar 1.06 m, 250 mm wheels, full). This report uses the JSON.

# 4. Compatibility per bin

## 4.1 [waste collector] domestic bins

| Bin | Key geometry vs GH-B2 | Mass vs 108 kg | Verdict | Expected capture (G3 MC slice) |
|---|---|---|---|---|
| **240 L general (green / black / burgundy)** | bar ~1.01-1.02 m (in 0.98-1.10 band); width 576-585; axle 569-575 (funnel 650 mouth OK); 200 mm wheels; bar 28-30 mm typical (inside D25-42); gap >= 36 | 96 + 10-15 = 106-111 kg (design case) | **HANDLED** | **93 %** incl. re-dock (27/29; 66 % first try) on the 200 mm-wheel, bar <= 1.06 m, section <= 36 mm slice; 88 % (36/41) if any section; **61 % if moulded >= 37 mm** |
| **240 L recycling (blue)** | same body | real loads light (15 kg/lift allowance; ~20-40 kg typical) | **HANDLED** | as above |
| **140 L general (Xtralite)** | bar ~1.0 m; W 478-505; webs ~340-420 (inferred from width); 200 mm wheels | 56 + 9-11 = 65-67 kg | **HANDLED** | **95 %** incl. re-dock (18/19 small-bin runs; 47 % first try) |
| **140 L recycling (Xtralite)** | same | light | **HANDLED** | 95 % |
| **140 L brown organic** | same; note it is narrow (photo) | 56 kg nominal, but wet food waste is dense: check the K5 current | **HANDLED** | 95 % |
| **25 L caddy (glass or food)** | no wheels, no rear bar, ~400 mm tall | 25 L glass can be ~10-15 kg | **NOT HANDLED** | - |

Caveats:

* **Small-bin edge.** G3 sampled small-bin bar heights of 0.95-1.00 m. The only published 140 L handle height (Gogic) is 1.005 m, just above that, but inside the 240 L band GH-B2 also covers. This is not a gap, just an untested combination: small web spacing with a 1.0-1.05 m bar.
* **What the misses correlate with** (G3 GH-B2 MC, 100 runs):
  * moulded section 36-42 mm: 76 % / 67 % capture;
  * bar height 1.08-1.10 m: 71 %;
  * 250 mm wheels: 75 %;
  * hand gap 40-49 mm: 74 %.
  
  Published [waste collector]-type bins (200 mm wheels, bar ~1.0 m) sit in the good part of that space. Only the bar section is unknown.

## 4.2 Other bins (context: other Irish collectors)

| Bin | Who issues it to houses | Verdict | What limits it |
|---|---|---|---|
| 240 L | everyone: Panda (Greenstar merged into Panda in 2016), City Bin (240 L only, red body / coloured lids), Barna, Oxigen, Country Clean, Greyhound | **HANDLED** | as for [waste collector] |
| 140 L | Panda, Barna, Oxigen, Greyhound, KeyGreen | **HANDLED** | as for [waste collector] |
| 120 L | Greyhound (Dublin) offers 120 L | **HANDLED WITH CHANGE (to verify)** | bar 0.90-0.94 m is **below** the 0.95 m G3 lower bound; needs a MC run at 0.88-0.95 m; if the float bottom stop is short, extend the rails / ratchet rack by 50-70 mm (EUR 10-20) |
| 360 L | Barna (household: 45 kg/lift allowance), Panda (listed), KWD (360 L recycling as standard) | **HANDLED WITH CHANGE** | geometry fits (bar ~1.025 m, W 585-620); mass up to ~160-170 kg gross is 1.5x the design case; 300 mm wheel option untested |
| 660 / 1100 L 4-wheel | commercial only (Panda 600/1100 L business list) | **NOT HANDLED, out of scope** | castors, no 2-wheel rear bar, 270-440 kg payload |
| 25 L / 23 L caddies | most collectors (food) | **NOT HANDLED** | no wheels |

Sources:

* Panda: [containers page](https://www.panda.ie/business/business-recycling/containers-equipment) (140/240/360/600/1100 L, business list).
* Barna: [household page](https://www.barnarecycling.com/) (140/240/360 L allowances 15/24/45 kg per lift).
* City Bin: 240 L only, per its [official FAQ](https://www.citybin.com/faq/types-of-household-bin-available/) as quoted by [recyclingcentreireland.org](https://recyclingcentreireland.org/city-bin-co-bin-sizes/). Not opened directly.
* Oxigen: [sizes](https://oxigen.ie/bin-collection-sizes) (140/240 L).
* Greyhound: [size guide](https://greyhound.ie/what-size-wheelie-bin-do-i-need-dublin-bin-size-guide) (45/120/140/240 L).
* KWD: [options](https://kwd.ie/m/mobile_options.php) (360 L recycling).
* Panda/Greenstar merger: [CCPC determination M/22/067](https://assets.ccpc.ie/data/docs/default-source/merger-attachments/m-2022/thorntons-recycling-carducci-holdings-(the-city-bin-co.)/m-22-067-phase-2-determination.pdf?sfvrsn=1790ff6b_1) (refers to M/16/008 PandaGreen/Greenstar).

# 5. Design changes to cover the rest

| # | Change | Covers | Est. cost (one-off, IE/EU, not quotes) | Status |
|--|----------------|------|------|-----|
| C0 | **Site survey** of Brian's [waste collector] bins: bar section (calipers, at 3 points), bar height upright, hand gap, distance between the inner faces of the handle webs, wheel D, axle width, embossed maker + date, gross mass of a full bin (bathroom scale under one wheel x2 is close enough) | decides C2; replaces EN 840 ranges in the MC with real values | EUR 0-15 (calipers) | do first |
| C1 | **Mass interlock (firmware):** estimate gross bin mass from K5 tilt current at the start of the tip; refuse to tow and alert above ~110 kg; tow at reduced speed with a 25 mm step rule between 108 and 130 kg if later validated | over-filled 240 L; light 360 L (recycling); protects step / anti-wheelie margins | EUR 0 (K5 INA219 already in BOM) + 1 h bench calibration with sand bags | recommended now |
| C2 | **GH-B4 hook candidate** for 37-42 mm moulded bars: lip top thinned 12 -> 8 mm over its top 20 mm (plate stays 10 mm S355), throat 48 -> 52 mm so lip + throat stays 60 mm, pawl blade extended ~4 mm so it still closes the mouth to < 25 mm; re-dock approaches 0.5 deg further back on the mast, with the float starting 20 mm lower | the 6 large-moulded-bar misses (61 % -> target >= 85 %) | 2 x GR-03 re-cut + galvanise EUR 25-40; 2 x GR-04 pawls EUR 10-20; total **EUR 40-60** + ~1 day of targeted MC (26 samples, same as the B3 test) | **unverified**; adopt only if it clears the large-bar misses with **no new false positive** (GH-B3 rule) |
| C3 | **25 L caddy:** (a) ask [waste collector] for a **140 L brown wheelie bin** instead (they issue it on City routes; route-dependent); (b) fallback: a caddy cradle on the tug deck (2 mm bent steel tray + strap); only workable if the tug waits at the kerb until the crew empties the caddy | food caddy (Country) or glass caddy (City) | (a) EUR 0 hardware; per-lift price differs (Lite plan: 140 L organic EUR 7.50 vs 25 L EUR 3.00 per lift, [quote page]([waste collector website])); (b) EUR 25-45 | (a) preferred |
| C4 | **Full 360 L kit (other collectors only):** heavier tilt actuator (~4-6 kN class, 24 V, IP66), +15-25 kg sand (re-run the anti-wheelie climb), lane rule **sharp steps <= 25 mm** (calc below), check kingpin and hooks at 1.5x load, check 300 mm-wheel bins in the funnel and wheel stops | 360 L at up to ~160-170 kg gross | actuator upgrade EUR 150-300 extra; sand EUR 5; extra kerb ramps EUR 15-40 each; **EUR 200-400 + a re-simulation** | not needed for [waste collector] |
| C5 | **120 L (other collectors):** MC at bar 0.88-0.95 m; if the float cannot reach, lower the float bottom stop / lengthen the GR-08 rack 50-70 mm | 120 L | EUR 10-20 if needed | not needed for [waste collector] |

**Step estimate for heavier bins.** The horizontal pull needed to roll a wheel of radius r over a sharp step h is F/W = sqrt(h(2r - h)) / (r - h). For r = 100 mm this gives 1.33 at 40 mm and 2.29 at 60 mm, matching the "~1.6 x / 2.3 x" quoted in G3 section 3.

The G3 tug passed 40 mm and stalled at 50 mm with 108 kg, so the available pull is 1.33-1.73 x the 108 kg wheel load. Holding that pull fixed:

| Gross bin mass | Largest sharp step, 200 mm wheels | Largest sharp step, 300 mm wheels |
|---|---|---|
| 130 kg | 32-42 mm | 49-64 mm |
| 160 kg | **25-35 mm** | 38-52 mm |

These are first-order numbers only: they assume the same wheel-load share and drive pull, so they need a re-simulation.

**Kingpin at 1.5x load:** the worst moment rises from 1976 to ~2960 N m. The M16 8.8 safety factor falls from 2.7 to ~1.8 on yield. This is still above 1.5 but must be re-checked in the tow model.

**Costs not included:** fabrication labour; any change to the companion/SITL software beyond the interlock threshold.

# 6. What is solid and what is not

* **Solid:**
  * [waste collector]'s domestic container list (their own household, FAQ, quote and commercial pages).
  * The EN 840 handle clearance, height and nominal-load rules.
  * Published overall dimensions, wheel sizes and masses (data sheets linked).
  * The G3 MC re-cut (read straight from `revG/sim/results_G3_mc_GH-B2.json`, 100 runs).
* **Not established:**
  * Which maker supplies [waste collector].
  * The actual bar section, hand gap and web spacing of [waste collector] bins. No maker publishes the gap or web spacing.
  * Whether [village] is a City or Country route.
  * The real share of 140 L vs 240 L households.
  * Whether [waste collector] will swap the 25 L caddy for a 140 L brown bin on a Country route.

  All of these are cheap to settle on site or with one call to [waste collector] (061 351127).
* **Model limits carried over from G3:** rigid plastic (no handle flex); the moulded bar is modelled as a box; the EN 840 ranges are not measurements. The capture percentages are simulation results with 95 % CIs of roughly +/-7-15 points at these sample sizes.

# 7. Files

| File | What |
|---|---|
| `revG/BINS_[waste collector]_G5.md` / `.pdf` | this report |
| `revG/RESULTS_G3_mech.md` | robot limits and hook geometry used (read only) |
| `revG/sim/results_G3_mc_GH-B2.json` | MC runs re-sliced in section 4 (read only) |
| `web/downloads/[waste collector]/` | [waste collector] bin photos used for colours and caddy type |
