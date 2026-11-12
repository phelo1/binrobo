#!/usr/bin/env python3
"""BinRobo BT-6 Rev G8 BOM - design-to-cost (11 Nov 2026). Private-use machine (Brian, 11 Nov 2026).
Three configurations, all meeting every function in revG/COSTDOWN_G8.md s.2:
  LEAN      - target < EUR 2,000 all-in (written to bom_revG8.csv / .json)
  BALANCED  - more bought-in certainty (certified / datasheet parts where lean relies on a bench test)
  G7        - reference (bom_revG7.py, EUR 8,218 all-in)
Import-and-override on bom_revG7.py (nothing upstream edited). EUR incl. 23 % IE VAT.
Status: 'checked-11Nov' = product/category page fetched today (5 % contingency); 'excerpt' = search excerpt only, UNVERIFIED (8 %);
'est' = estimate (12 %); LOCAL / used = 15 %; logistics 10 %. FX as G4: 1 USD = 0.86 EUR, 1 GBP = 1.15 EUR.
Concept: LEAN is costed on concept A' (tow + sprung pad + yaw damper; the A' delta lines of revG/sim/cg/res/cost_cg_g7.json are included).
The concept-B delta is computed beside it (concept_B_delta) because the concept gate is still running.
usage: PYTHONPATH=/workspace/work/pylib python3 revG/bom_revG8.py
"""
import copy, csv, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bom_revG7 as G7   # noqa: E402
import bom_revG4 as G4   # noqa: E402
DATE = '2026-11-11'; USD, GBP, VAT = 0.86, 1.15, 0.23
def usd_ie(x): return round(x * USD * (1 + VAT), 2)
def exvat_ie(x): return round(x * (1 + VAT), 2)

# ------------------------------------------------------------------ lean fabrication model (from g6parts/fab_cost_g6.json)
def fab_lean():
    F = json.load(open(os.path.join(H, 'g6parts', 'fab_cost_g6.json'))); r = F['rates']
    rho = 7.85 / 2.66; tot = 0.0; rows = []
    for p in F['rows']:
        if p['id'] in ('CH-51', 'CH-04'):          # deck + battery lid -> 10 mm HDPE offcut, cut by Brian (G3 spec)
            rows.append((p['id'], 'HDPE offcut (in FAB-L line)', 0.0)); continue
        if p['route'] == '5083':                   # tray, bulkhead, pod/battery brackets -> 2 mm DX51D+Z275
            kg = p['kg'] * (2 / 3) * rho
            mat = kg * r['eur_kg']['Z275'] * r['nest_waste']
            las = p['laser'] * r['cut_per_m']['2'] / r['cut_per_m']['3']
            c = mat + las + p['fold']; rows.append((p['id'], '2 mm Z275 (was 3 mm 5083)', round(c, 2)))
        else:
            c = p['material'] + p['laser'] + p['fold']; rows.append((p['id'], p['route'] + ' ' + str(p['thk']) + ' mm', round(c, 2)))
        tot += c
    groups = 5                                     # Z275-2, Z275-3, S355-6, S355-8, S355-10
    setup = groups * r['setup_per_sheet_group'] + r['brake_setup']
    extras = [('Zinga 500 ml x2 (cold galvanising of plates, welds, cut edges) - igoe.ie checked-10Nov', 52.5),
              ('Cavity wax 500 ml', 12.0), ('Tube/bar stock per tube_bar_cut_list.csv, saw-cut by Brian', 60.0),
              ('Shop MIG of the 4 steel tray corner seams + bulkhead tabs (was TIG of 5083, EUR 45)', 30.0),
              ('Deck CH-51 + lid CH-04: 10 mm HDPE offcuts (G3 spec), cut by Brian', 20.0)]
    total = round(tot + setup + sum(e[1] for e in extras), 2)
    return dict(sheet=round(tot, 2), setup=setup, extras=extras, total=total, rows=rows,
                added_steel_kg=round(sum(p['kg'] * ((2 / 3) * rho - 1) for p in F['rows'] if p['route'] == '5083' and p['id'] not in ('CH-51', 'CH-04')), 1))
FABL = fab_lean()

def L(id_, area, item, real, status, origin, url='', why='', kind='substitution', fix=''):
    return dict(id=id_, area=area, item=item, real=round(real, 2), status=status, origin=origin, url=url, why=why, kind=kind, fix=fix)

PE = 'https://www.peipeiscooter.com/categories/100020'
SDR = 'https://www.superdroidrobots.com/product_info/TD-292-120_Test_Report.pdf'
# ------------------------------------------------------------------ LEAN overrides of G7 lines (id -> new line). real=0 + kind deleted = removed.
LEAN = {
 'FAB-G6': L('FAB-L8', 'Structure', 'Local laser + fold package, STEEL ONLY: tray CH-01 + bulkhead CH-14 + pod/battery brackets PD-10/PB-02/PB-03 in 2 mm DX51D+Z275 '
             '(were 3 mm 5083), deck/lid in 10 mm HDPE offcut, 6-10 mm plates S355 + Zinga; same 31-DXF set otherwise (model in bom_revG8.py fab_lean())',
             FABL['total'], 'est', 'LOCAL', 'revG/g6parts/RFQ_LOCAL_FAB_G6.md',
             'Review s.8 item 2 (CD2) extended to every aluminium part. Adds about %.1f kg of steel low in the chassis (tray) - counts toward the ballast. '
             'Same RFQ (ATC / MFS / Metaltech / Flynn); send the steel-only variant.' % FABL['added_steel_kg'], fix='CD2'),
 'G6': L('CTL-L8', 'Drive', 'Motor controller Basicmicro RoboClaw 2x30A (IMC413): 2 x 30 A cont / 60 A peak, 6-34 V, dual quadrature encoder inputs, '
         'closed-loop speed PID, per-channel current limit, voltage clamp output, USB/TTL serial. Replaces Roboteq FDCG3260T (EUR 968).',
         148.44, 'checked-11Nov', 'EU', 'https://eu.robotshop.com/products/roboclaw-2x30a-6-34vdc-regenerative-motor-controller',
         'EUR 148.44 incl. VAT (fetched; "re-stocking soon" - Pololu 3684 US$134.95 is the second source). STO is no longer needed: safe torque-off is done by '
         'two series contactors KM1/KM2 + spring brakes (s.3). Climb needs ~17-20 A/motor (s.4) < 30 A cont; current limit set to 28 A. '
         'Cheaper fallback Cytron MDDS30 EUR 82.95 (vanallesenmeer.nl, fetched) has no settable current limit and no encoder loop - not equal.', fix='M5/B4'),
 'DRV-M7': L('DRV-M8', 'Drive', 'Drive gearmotor PAIR peiscooter PEWM82M-320W: brushed 24 V, 320 W each, 32:1 right-angle wheelchair gearbox, 4,600 rpm, '
             'electromagnetic spring brake + hand release, left + right', usd_ie(298.00), 'checked-11Nov', 'CN', PE,
             'US$298/pair (category page fetched; product page https://www.peipeiscooter.com/products/108). Torque evidence = measured test curve of the same '
             '320 W 4-pole wheelchair motor class (SuperDroid TD-292-120 report: 14.08 N m @ 17.08 A rated, 21.3 N m @ 25.8 A max power at 43:1) -> '
             '10.5 N m @ 17 A at 32:1; with the 3.5:1 chain stage (DRV-W8) 34.8 N m @ 17 A per wheel, 53 N m @ 25.8 A. ACCEPTANCE TEST on arrival (s.10).', fix='M5'),
 'DRV-W7': L('DRV-W8', 'Drive', 'Drive wheels + 3.5:1 chain stage, per side: 330 mm (13 in) solid PU wheel on 2 bearings and a dead stub axle (25 mm), 42T 08B plate sprocket '
             'bolted to the hub, 12T 08B sprocket bored/keyed to the gearmotor shaft, 08B chain ~1.2 m, slotted motor plate for tension, chain guard (laser part in FAB-L8)',
             130.0, 'est', 'IE', '', 'Wheels ~EUR 25 each, sprockets/chain/fixings ~EUR 40 per side (est, quote on order). 3.5:1 turns the 32:1 wheelchair motor into a '
             '112:1 drive: torque x3.3; speed at rated 17 A ~0.79 m/s (test-curve scaling; 0.71 m/s from the vendor 4,600 rpm figure), no-load ~0.9-1.0 m/s at 24-29 V (inherent speed cap, s.3).', fix='M5'),
 'PWR-G7': L('PWR-G8', 'Enclosure & wiring', 'Power path: 10 mm2 B+ trunk ISO-KM1-KM2-F1-controller, 6 mm2 motor runs, Anderson SB50 motor connectors, M8 lugs, brake leads on DT04-2P',
             30.0, 'est', 'CN', '', 'Climb current 17-20 A/motor; SB50 (50 A) replaces DTHD size 8.', fix='M5'),
 'G10': L('ACT-L8', 'Hitch & grabber', 'Mast actuator QC/FDI series 24 V, 400 mm stroke, 4,000 N, IP65, -50..+45 C, limit switches, L 620 mm retracted '
          '-> pin-pin 620/1,020 + 30 mm clevis spacer = 650/1,050 (window 656-1,042) + 2 bushes; aux-power Anderson socket + hold-to-run pendant for '
          'lowering a loaded mast with a dead pack (replaces the CAHB manual override)', exvat_ie(113.31) + 25.0, 'checked-11Nov', 'LT',
          'https://www.anodas.lt/en/fdi-linear-actuator-24v-400mm-6mm-s',
          'EUR 113.31 ex VAT (fetched) + IE VAT; spacer/bushes/pendant est EUR 25. 4,000 N = 1.6 x the 2,473 N sim peak, 1.29 x the 3.1 kN cold target. '
          'Speed 6 mm/s (CAHB 11 mm/s): tilt ~64 s instead of ~35 s. No position output: mast angle from the AS5600 (G8) on the hinge. '
          'Fallback REMORE RE601G 6,000 N IP65 -26..+65 C, 892.99 PLN (technika-cnc.pl, fetched). BENCH TEST force at -20 C (s.10).', fix='M6'),
 'GR-08S': L('GR-08S', 'Hitch & grabber', 'DELETED: pawl-lift solenoid -> 2nd lobe on the GR-07 cam lifts the ratchet pawl (review M10 option, CD4)', 0.0, 'est', 'CN',
             kind='deleted', why='G7 CD4. Needs the cam re-timed and a MuJoCo re-check of the release sequence.', fix='M10'),
 'GR-08D': L('GR-08D', 'Hitch & grabber', 'Pawl-up sensor (M8 PNP IP67) kept in the pre-tip / pre-release interlock; solenoid driver channel, F14 and T3b cable deleted',
             12.0, 'est', 'CN', why='Interlock kept (review M10).', fix='M10'),
 'GR-07': L('GR-07', 'Hitch & grabber', 'Cam gearmotor 5840-31ZY 24 V ~10 rpm 100 kg.cm worm, self-locking + 2 limit switches + SECOND CAM LOBE for the pawl lift (laser, in FAB-L8)',
            14.0, 'excerpt', 'CN', 'https://www.aliexpress.com/w/wholesale-12v-dc-motor-30-rpm.html', 'Unchanged price; lobe is a laser part.', kind='correction', fix='M10'),
 'HTR-G7': L('HTR-L8', 'Power', 'Pack heater: 2 x 24 V 15-30 W silicone pads with 3M adhesive (PWM to 15 W mean from the dock controller), KSD9700 40 C NC cutout, logic MOSFET',
             24.0, 'excerpt', 'CN', 'https://www.jsr2.com/product/2x-7-51-x-178mm-120v-25w-w-3m-w-plug-ithermal-silicone-flexible-heater-pad',
             'Same function as the RS PRO mats (EUR 109): heater power, adhesive mount, hardware over-temperature cutout and NTC charge gate unchanged. '
             'Price from search excerpts (JSR 80x220 mm 24 V 30 W US$12.50; AliExpress pads GBP 3-7) - UNVERIFIED.', fix='m3'),
 'S4': L('KM-L8', 'Safety & power dist.', 'TWO main contactors in series KM1 + KM2: 100 A DC, 24 V coil (SW100 class), each coil switched by its own safety-relay output channel',
         2 * 28.66, 'excerpt', 'DE', 'https://jazgot.at/sch%C3%BCtze/18407-antriebssch%C3%BCtz-dc-24v-100a-sw100.html',
         'EUR 28.66 incl. AT VAT each (excerpt; jazgot.de page checked 6 Nov at EUR 28). Redundant power removal replaces the Roboteq STO (s.3).', fix='B4'),
 'S5': L('SR-L8', 'Safety & power dist.', 'Safety relay Pilz PNOZ X3 774310 USED, tested, 3-month warranty (24 VAC/DC; 3 NO safety + 1 NC aux + 1 semiconductor; '
         '1/2-channel with cross-fault detection; feedback loop; manual/auto start; Cat 4 / PL e as new)', exvat_ie(49.80), 'checked-11Nov', 'DE',
         'https://cncbote.de/en/product/pilz-pnoz-x3-24vac-24vdc-3n-o-1n-c-1so-sicherheitsrelais/',
         'EUR 49.80 net (cncbote listing on the fetched PNOZ X2.8P page, 11 Nov; the X2.8P itself is sold out). Alternatives: PNOZ X2.8P new from EUR 101.45 '
         '(idealo excerpt), used X2.8P US$75 (igam.com excerpt), PNOZ s4 used EUR 69.80 (cncbote). Instant (stop category 0) outputs; see s.3.', fix='B4'),
 'SPD-G7': L('SLS-L8', 'Safety & power dist.', 'Dual-channel speed / standstill monitor + contactor EDM, own build: 2 x RP2040-Zero (one per channel, separate 5 V buck each), '
             '2 x 2-pole relays (one pole in the PNOZ input loop, one read back), voltage-sense dividers on KM1/KM2 outputs, perfboard + IP65 box',
             30.0, 'est', 'CN', '', 'Replaces the PNOZ s30 (EUR 814). Channel A counts the two inductive sensors (SPD-S8), channel B the wheel encoders (G9) - '
             'diverse sensing; each MCU trips its own channel on > 0.6 m/s (0.3 m/s zone input), wheel-to-wheel or A/B implausibility, or loss of the other '
             'MCU heartbeat; outputs de-energise to trip. Equivalence argument in s.3.', fix='B4'),
 'SPD-S7': L('SPD-S8', 'Safety & power dist.', 'Speed sensors channel A: 2 x M12 inductive PNP IP67 (LJ12A3 class) on 12-tooth target rings (rings in FAB-L8)',
             10.0, 'est', 'CN', '', 'Channel B uses the G9 wheel encoders.', fix='B4'),
 'HDG-G7': L('RTK-L8', 'Navigation', 'RTK rover single antenna: Quectel LC29HDA core board + L1/L5 active antenna (rover of the G4 LC29H pair). '
             'Heading from the EKF GSF yaw (moving), wheel odometry + gyro (pivot / standstill), and an absolute reset from the dock ArUco tag 20 at each departure',
             33.0, 'excerpt', 'CN', 'https://www.aliexpress.com/item/1005008988611057.html',
             'G4 sourcing: LC29H ~US$15-17 (AliExpress), EUR 16.20 tekmodul.de; antenna EUR 15-18 (excerpts). Saves EUR 241 vs the UM982. '
             'Heading performance under canopy is a RISK (s.10).', fix='M9'),
 'G23b': L('G23b', 'Sensing', 'microSD high-endurance 32 GB (Samsung PRO Endurance / SanDisk High Endurance class); clean shutdown kept by the S11 UPS HAT',
           15.0, 'est', 'EU', '', 'Industrial SLC/pSLC card (EUR 39.90) bought power-loss immunity; S11 already gives a clean shutdown.', kind='substitution'),
 'AU-G6': L('AU-L8', 'Comms', 'Two-way audio: Eagle P630TA IP65 8 ohm 15 W horn + MAX98357A amp + Gore vent + pod USB hub; MIC = USB mic at the mast top on a 3 m '
            'cable straight to the pod hub (HUB2 deleted)', exvat_ie(35.12) + 32.0, 'checked-11Nov', 'NL', 'https://www.eijlander.nl/hoorn-luidsprekers.html',
            'Horn EUR 35.12 ex VAT (fetched category page). Review s.8 item 3 / CD3. 2.9-3 m USB 2.0 is inside the 5 m limit. Check sound level on the bench.', fix='CD3'),
 'F1': L('F1', 'Enclosure & wiring', 'Fasteners A4-70 set as G3 + 50 pairs generic DIN 25201 A4 M8 wedge-lock washers (Nord-Lock pattern)', 38.0 + 15.0, 'est', 'CN', '',
         'Same locking principle (wedge pair, DIN 25201) as Nord-Lock at a fraction of the price; keep Nord-Lock on the 4 kingpin/hub bolts if in doubt.', kind='substitution'),
 'BMP-G7': L('BMP-L8', 'Safety & power dist.', 'Safety bumpers: front bar + 2 rear corner bumpers on sprung guides, actuated by 4 x Omron D4N-4120 positive-opening '
             'safety limit switches (1NC/1NO, direct opening per IEC 60947-5-1 Annex K, IP67), NC contacts wired 2-channel into the PNOZ', 4 * exvat_ie(19.69) + 40.0,
             'excerpt', 'DE', 'https://fluidics-equipment.com/d/FL-D4N4120.html',
             'EUR 19.69 net each (search excerpt, fluidics-equipment; TME EUR 31.86 net, RS DE EUR 25.65 net) + bars/guides/springs est EUR 40. G7 line was EUR 160 est.', fix='B4'),
 'D1': L('D1', 'Dock', 'Dock frame: 2 posts + rubber-faced dummy-wheel blocks + nose block + tag-20 backboard from treated timber offcuts, bolted to the paving pad', 15.0, 'est', 'LOCAL', kind='correction'),
 'D3': L('D3', 'Dock', 'Dock controller: ESP32-C3 + INA219 + 10 A relay + reed switch & magnet + 2.2 kOhm sense source, powered from the charger via a buck (USB PSU deleted)', 15.0, 'est', 'CN', kind='correction'),
}
# new LEAN lines (not in G7)
LEAN_NEW = [
 L('CG-A1', 'Hitch & grabber', "Concept A' parts (cost_cg_g7.json): sprung load-transfer pad 2 rollers/slide/2 die springs (55), yaw centring torsion bar + gas damper (60), "
   "tapered-roller trailer hub replacing the kingpin kit, net (25), upper wheel-stop roller (15), stop-bar 60 mm retract cam (45), float clamp 2nd pawl + solenoid + driver (30), "
   "wheel-on-ground load sensor (20)", 250.0, 'est', 'LOCAL', 'revG/sim/cg/res/cost_cg_g7.json', "Concept A' as frozen at 08:08 (PROGRESS_concept.md).", kind='new', fix='B1/B2'),
]
# ------------------------------------------------------------------ logistics (LEAN)
LOG_LEAN = {
 'SHIP-PEI': (110.0, 'peiscooter motors ~11 kg by air from Shanghai ("extra ship cost" category), est'),
 'SHIP-CN': (8.0, 'AliExpress consolidated (one order, Choice/IOSS), est'),
 'DUTY': (63.0, 'EUR 3 per tariff line on ~18 AliExpress lines (EU low-value rule from 1 Jul 2026) + 2.7 % on the motors incl. VAT on duty, est'),
 'SHIP-DE': (18.0, 'jazgot (contactors) + cncbote (PNOZ, free over EUR 89 net else 8.90), est'),
 'SHIP-EU': (15.0, 'robotshop EU (RoboClaw), est'),
 'SHIP-LT': (20.0, 'anodas.lt actuator to IE (negotiated individually on the page), est'),
 'SHIP-NL': (15.0, 'NKON cells + eijlander horn + dataio, est'),
 'SHIP-EU2': (15.0, 'neven7.eu (Radxa) + other EU single items, est'),
 'SHIP-FR': (10.0, 'clavipro charger, as G6'),
 'SHIP-GB': (15.0, 'beacon (bowers) + trailer cable (12voltplanet), as G6'),
 'SHIP-IE': (8.0, 'RS IE / Screwfix / local, as G6'),
 'SHIP-LOCAL': (15.0, 'fabricator collection, as G6'),
}

# ------------------------------------------------------------------ BALANCED = LEAN with these replaced (more bought-in certainty)
BAL = {
 'FAB-G6': L('FAB-B8', 'Structure', 'Local laser + fold package as G7 FAB-G6 but tray CH-01 + CH-14 in 2 mm Z275 (CD2); other 5083 parts kept', 713.29 - 90.0, 'est', 'LOCAL',
             'revG/g6parts/RFQ_LOCAL_FAB_G6.md', 'G7 model minus CD2.', fix='CD2'),
 'DRV-M7': L('DRV-B8', 'Drive', 'Drive gearmotor pair peiscooter PEWM-S 400 W x2, 32:1, with output sprockets, spring brakes (+25 % motor thermal margin over the 320 W lean motor)',
             usd_ie(398.00), 'checked-11Nov', 'CN', PE, 'US$398/pair (category page p.2 fetched). Same 3.5:1 chain stage.', fix='M5'),
 'G10': L('G10', 'Hitch & grabber', 'Mast actuator Ewellix CAHB-20-F3E 405 mm (as G7): manual override, position output, IP69K, -40..+85 C', 622.63, 'checked-11Nov', 'GR',
          'https://eshop.papadopoulos-sa.com/linear-actuators/75292-ewellix-cahb-20-f3e-4500696-bba0pt-000-linear-actuators-7333314280503.html', 'As G7.', fix='M6'),
 'S5': L('SR-B8', 'Safety & power dist.', 'Safety relay Pilz PNOZ X2.8P 777301 NEW (3 NO + 1 NC, 1/2-channel, cross-fault, feedback loop, Cat 4 / PL e)', 101.45, 'excerpt', 'DE',
         'https://www.idealo.de/preisvergleich/OffersOfProduct/202061547_-pnoz-x2-8p-24vacdc-3n-o-1n-c-777301-pilz-the-spirit-of-safety.html',
         'Lowest idealo offer EUR 101.45 incl. shipping (excerpt) - UNVERIFIED; eibabo GBP 135.54.', fix='B4'),
 'HDG-G7': L('HDG-G7', 'Navigation', 'Heading: Holybro H-RTK Unicore UM982 dual-antenna (as G7)', 274.44, 'checked-11Nov', 'CN', 'https://holybro.com/products/h-rtk-unicore-um982', 'As G7.', fix='M9'),
 'G23b': None, 'F1': None, 'HTR-G7': None,   # None = keep the G7 line
}
LOG_BAL = dict(LOG_LEAN); LOG_BAL['SHIP-GR'] = (25.0, 'Papadopoulos (Ewellix) GR -> IE, as G7'); LOG_BAL['SHIP-HB'] = (25.0, 'Holybro UM982, as G7')
LOG_BAL['SHIP-LT'] = (0.0, 'no LT order'); LOG_BAL['SHIP-RS'] = (8.0, 'RS Ireland heater mats, as G7'); LOG_BAL['DUTY'] = (75.0, 'as lean + GNSS line, est')

# ------------------------------------------------------------------ concept B delta on the LEAN list
B_REMOVE = ['CG-A1', 'G8', 'G11', 'K1', 'K3', 'K4', 'GR-10', 'GR-08', 'GR-08D', 'GR-G6', 'IND-OPEN', 'RF-10/11/12', 'YS-G7', 'G10']
B_ADD = [('ACT-B (FDI 24 V 300 mm 4 kN lifter, priced as the 400 mm unit - upper bound)', exvat_ie(113.31) + 25.0, 'checked-11Nov'),
         ('Lifter: 2 x 1 m linear rail + 4 carriages', 90.0, 'est'), ('Comb tooth with 12 mm nib + keeper fingers (GR-07 reused as keeper drive)', 20.0, 'est'),
         ('Sprung lower pad', 35.0, 'est'), ('Lip-root ToF sensor + nib seat switch', 15.0, 'est'),
         ('Fabrication net: no rear frame / tilting mast / funnel arms; adds side arms, lifter mast, 0.80 m axle beam', -60.0, 'est'),
         ('Ballast: steel plate in the arms instead of BT-01 cans + sand', -7.0, 'est')]

# ------------------------------------------------------------------ LEAN-D: donor powerchair base + Brian-built hitch frame (cheapest config keeping every function)
D_REMOVE = ['DRV-M7', 'DRV-W7', 'DRV-C7', 'BT-01', 'HTR-G7', 'D6', 'G14', 'FAB-G6']   # G7 ids (their LEAN replacements are dropped too)
def fab_donor():
    F = json.load(open(os.path.join(H, 'g6parts', 'fab_cost_g6.json'))); r = F['rates']
    keep = ['GR-51', 'GR-06', 'GR-08', 'GR-56', 'GR-57', 'GR-59', 'GR-03', 'GR-04', 'MA-52', 'MA-53', 'MA-54', 'SN-51', 'SN-58', 'SN-59', 'KP-G7', 'DE-02', 'RF-11', 'RF-13']
    c = sum(p['material'] + p['laser'] + p['fold'] for p in F['rows'] if p['id'] in keep)
    setup = 4 * r['setup_per_sheet_group'] + r['brake_setup']
    return round(c + setup + 52.5 + 60.0 + 25.0, 2), round(c, 2)
FABD, FABD_PL = fab_donor()
D_NEW = [
 L('DNR-D8', 'Drive', 'DONOR powerchair, rear- or mid-wheel drive, 24 V, 2 brushed gearmotors with spring brakes, solid/foam tyres or fitted with them, '
   'casters, frame, 2 x 12 V AGM 35-55 Ah, off-board 24 V charger (moves to the dock). Seat, joystick and controller removed (resale not credited). '
   'BUY ONLY AFTER the pull test in s.10 (>= 450 N drawbar at walking pace for 3 min on the seller\'s driveway, luggage scale + rope)', 400.0, 'excerpt', 'LOCAL',
   'https://www.donedeal.ie/all?words=electric+wheelchair',
   'Irish listings EUR 380-850 for working chairs (DoneDeal / adverts.ie search excerpts, 11 Nov), eBay IE Jazzy Elite ES "needs battery" EUR 384. '
   'A chair rated for a 136 kg user on 6-9 deg moves 246 kg up 10.5-15.8 %: drawbar demand of the tug + bin at 12 % is 386-451 N, i.e. inside that envelope '
   'only for chairs rated >= 8 deg (s.4).', kind='new', fix='M5'),
 L('FAB-D8', 'Structure', 'Hitch/mast frame, sensor post and bay brackets bolted to the chair frame: RHS + flat stock saw-cut and drilled by Brian, '
   'laser-cut only the grabber / mast / hub / sensor plates (18 DXFs of the G6 set), Zinga, chair-frame clamp plates', FABD, 'est', 'LOCAL', 'revG/g6parts/fab_cost_g6.json',
   'Plates EUR %.2f (G6 fab model rows) + 4 sheet groups + brake set-up EUR 120 + Zinga EUR 52.50 + stock EUR 60 + clamp plates EUR 25.' % FABD_PL, kind='new', fix='CD2'),
 L('BAT-D8', 'Power', 'Traction battery = the donor AGM pair (24 V 35-55 Ah, 21-30 kg, also the ballast). Replace with 2 x 12 V 35 Ah AGM (~EUR 140) if the capacity test '
   'shows < 80 %. LiFePO4 pack, its BMS and the pack heater are not needed (AGM charges below 0 C at reduced current)', 0.0, 'est', 'LOCAL', '',
   'Risk carried in s.10 (EUR 140).', kind='new'),
]
LOG_D = dict(LOG_LEAN); LOG_D.pop('SHIP-PEI'); LOG_D['DUTY'] = (45.0, 'EUR 3 per tariff line on ~15 AliExpress lines, est'); LOG_D['COLLECT'] = (40.0, 'collect the donor chair (fuel/van), est')
LOG_D['SHIP-NL'] = (8.0, 'eijlander horn only (no NKON cells)')

def contingency(lines, log):
    c = 0.0
    for r in lines:
        st = r['status'].split('+')[-1] if '+' in r['status'] else r['status']
        if r['origin'] == 'LOCAL' or r['id'] in ('SR-L8',): k = G4.CONT_LOCAL_USED   # local fab, used parts
        elif st.startswith('checked'): k = 0.05
        else: k = G4.CONT.get(st, 0.12)
        c += r['real'] * k
    return c + G4.CONT_LOG * sum(v for v in log.values())

def apply(base, ovr, new, log):
    out = []
    for r in base:
        n = copy.deepcopy(r); n['g7_real'] = r['real']; n['g7_id'] = r['id']
        if r['id'] in ovr and ovr[r['id']] is not None:
            o = ovr[r['id']]; n.update({k: o[k] for k in o})
        else:
            n['kind'] = 'unchanged'
        out.append(n)
    for r in new:
        r = copy.deepcopy(r); r['g7_real'] = 0.0; out.append(r)
    parts = sum(r['real'] for r in out); lg = sum(v[0] for v in log.values())
    cont = contingency(out, {k: v[0] for k, v in log.items()})
    return out, dict(parts=round(parts, 2), logistics=round(lg, 2), subtotal=round(parts + lg, 2), contingency=round(cont, 2), all_in=round(parts + lg + cont, 2))

def build():
    S7 = G7.build(); base = S7['lines']
    lean, tl = apply(base, LEAN, LEAN_NEW, LOG_LEAN)
    bal_ovr = dict(LEAN); bal_ovr.update({k: v for k, v in BAL.items() if v is not None})
    for k, v in BAL.items():
        if v is None: bal_ovr.pop(k, None)
    bal, tb = apply(base, bal_ovr, LEAN_NEW, LOG_BAL)
    # concept B on lean
    keep = [r for r in lean if r['id'] not in B_REMOVE]; rem = sum(r['real'] for r in lean if r['id'] in B_REMOVE)
    addl = [dict(id='B-%d' % i, area='Concept B', item=a, real=round(v, 2), status=s, origin='LOCAL' if s == 'est' else 'LT', url='', why='', kind='new', fix='CG') for i, (a, v, s) in enumerate(B_ADD)]
    bl = keep + addl; bparts = sum(r['real'] for r in bl); blog = {k: v[0] for k, v in LOG_LEAN.items()}
    bc = contingency(bl, blog); bt = dict(parts=round(bparts, 2), logistics=round(sum(blog.values()), 2), contingency=round(bc, 2), all_in=round(bparts + sum(blog.values()) + bc, 2))
    # LEAN-D
    dl = [r for r in lean if r['id'] not in D_REMOVE and r.get('g7_id', r['id']) not in D_REMOVE]
    dl = [r for r in dl if r['id'] not in ('DRV-M8', 'DRV-W8', 'FAB-L8', 'HTR-L8')]
    dl += [dict(copy.deepcopy(x), g7_real=0.0) for x in D_NEW]
    dparts = sum(r['real'] for r in dl); dlog = {k: v[0] for k, v in LOG_D.items()}
    dc = contingency(dl, dlog)
    dt = dict(parts=round(dparts, 2), logistics=round(sum(dlog.values()), 2), subtotal=round(dparts + sum(dlog.values()), 2), contingency=round(dc, 2), all_in=round(dparts + sum(dlog.values()) + dc, 2))
    by_area_d = {}
    for r in dl: by_area_d[r['area']] = round(by_area_d.get(r['area'], 0) + r['real'], 2)
    by_area = {}
    for r in lean: by_area[r['area']] = round(by_area.get(r['area'], 0) + r['real'], 2)
    return dict(g7=S7['g7'], lean=lean, lean_tot=tl, bal=bal, bal_tot=tb, conceptB=dict(removed=round(rem, 2), added=addl, totals=bt),
                by_area=by_area, fab=FABL, donor=dl, donor_tot=dt, by_area_d=by_area_d)

def write():
    S = build()
    with open(os.path.join(H, 'bom_revG8.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'area', 'item', 'eur_G7', 'eur_G8_lean', 'delta', 'kind', 'fix_ref', 'status', 'order_group', 'url', 'why'])
        for r in S['lean']:
            w.writerow([r['id'], r['area'], r['item'], r['g7_real'], r['real'], round(r['real'] - r['g7_real'], 2), r['kind'], r.get('fix', ''), r['status'], r['origin'], r.get('url', ''), r.get('why', '')])
        for k, (v, why) in LOG_LEAN.items():
            w.writerow([k, 'Logistics', '', '', v, '', 'logistics', '', 'est', '', '', why])
        t = S['lean_tot']; g = S['g7']
        w.writerow(['', '', 'TOTAL parts (incl. IE VAT)', g['parts'], t['parts'], round(t['parts'] - g['parts'], 2)])
        w.writerow(['', '', 'TOTAL incl. shipping + duty', g['subtotal'], t['subtotal'], round(t['subtotal'] - g['subtotal'], 2)])
        w.writerow(['', '', 'Risk-weighted contingency', g['risk_weighted_contingency'], t['contingency'], ''])
        w.writerow(['', '', 'TOTAL ALL-IN (LEAN, concept A\')', g['with_risk_weighted'], t['all_in'], round(t['all_in'] - g['with_risk_weighted'], 2)])
        w.writerow(['', '', 'TOTAL ALL-IN (LEAN, concept B variant)', '', S['conceptB']['totals']['all_in'], ''])
        w.writerow(['', '', 'TOTAL ALL-IN (BALANCED, concept A\')', '', S['bal_tot']['all_in'], ''])
        w.writerow(['', '', 'TOTAL ALL-IN (LEAN-D donor powerchair base, concept A\') - see bom_revG8_donor.csv', '', S['donor_tot']['all_in'], ''])
    with open(os.path.join(H, 'bom_revG8_donor.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'area', 'item', 'eur', 'status', 'order_group', 'url', 'why'])
        for r in S['donor']:
            w.writerow([r['id'], r['area'], r['item'], r['real'], r['status'], r['origin'], r.get('url', ''), r.get('why', '')])
        for k, (v, why) in LOG_D.items():
            w.writerow([k, 'Logistics', '', v, 'est', '', '', why])
        t = S['donor_tot']
        for k in ('parts', 'logistics', 'subtotal', 'contingency', 'all_in'): w.writerow(['', '', k.upper(), t[k]])
    json.dump(dict(meta=dict(date=DATE, base='bom_revG7.py', fx=dict(USD=USD, GBP=GBP), vat_ie=VAT, note='revG/COSTDOWN_G8.md'),
                   totals=dict(g7=S['g7'], lean=S['lean_tot'], balanced=S['bal_tot'], lean_conceptB=S['conceptB']['totals'], lean_donor=S['donor_tot']),
                   donor_lines=S['donor'], by_area_donor=S['by_area_d'], logistics_donor={k: dict(eur=v, why=w) for k, (v, w) in LOG_D.items()},
                   by_area_lean=S['by_area'], fab_lean=S['fab'], lean_lines=S['lean'], logistics_lean={k: dict(eur=v, why=w) for k, (v, w) in LOG_LEAN.items()},
                   balanced_lines=S['bal'], logistics_balanced={k: dict(eur=v, why=w) for k, (v, w) in LOG_BAL.items()}, conceptB=S['conceptB']),
              open(os.path.join(H, 'bom_revG8.json'), 'w'), indent=1)
    return S

if __name__ == '__main__':
    S = write()
    print('G7 all-in', S['g7']['with_risk_weighted'])
    print('LEAN', S['lean_tot']); print('LEAN concept B', S['conceptB']['totals']); print('BALANCED', S['bal_tot'])
    for k, v in sorted(S['by_area'].items(), key=lambda x: -x[1]): print('  %-24s %8.2f' % (k, v))
    print('fab', S['fab']['total'], 'added steel kg', S['fab']['added_steel_kg'])
    print('LEAN-D', S['donor_tot'])
    for k, v in sorted(S['by_area_d'].items(), key=lambda x: -x[1]): print('  D %-24s %8.2f' % (k, v))
