#!/usr/bin/env python3
"""Bin Tug Rev G7 BOM (11 Nov 2026): electrical / functional-safety / BOM fix pass after REVIEW_G6_coldeye (B4, M5, M6, M9, M10, m3, m5)
and the GA Rev B loom pass (work/out/revG6/drawings sheet X3, src/crosscheck.json, src/issues.py).
Import-and-override on bom_revG6.py (nothing upstream edited). EUR incl. 23 % IE VAT. Same contingency rules as G6;
status 'checked-11Nov' = price page fetched 11 Nov 2026 (5 %), 'excerpt' = search-result excerpt (8 %), 'est' = estimate (12 %), LOCAL 15 %.
usage: python3 revG/bom_revG7.py -> revG/bom_revG7.csv + .json (+ prints totals). Design note: revG/ELEC_SAFETY_G7.md.
FX as G4: 1 USD = 0.86 EUR, 1 GBP = 1.15 EUR, 1 DKK = 0.134 EUR.
"""
import copy, csv, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bom_revG6 as G6   # noqa: E402
import bom_revG4 as G4   # noqa: E402
import bom_revG as M     # noqa: E402
DATE = '2026-11-11'; USD, GBP, DKK, VAT = 0.86, 1.15, 0.134, 0.23
def usd_ie(x): return round(x * USD * (1 + VAT), 2)          # non-EU goods: import VAT on goods (duty in DUTY line)
def exvat_ie(x): return round(x * (1 + VAT), 2)               # EU shop ex-VAT price -> IE VAT
def R(id_, area, item, real, status, origin, url='', why='', kind='new', fix=''):
    return dict(id=id_, area=area, item=item, real=round(real, 2), status=status, origin=origin, url=url, why=why, kind=kind, fix=fix, g4_real=0.0)

# ---------------------------------------------------------------- overrides of G6 lines
OVR = {
 'G4': dict(kind='deleted', real=0.0, status='est', origin='LOCAL', fix='M5',
   item='DELETED: donor powerchair (no repeatable drive spec, conflicts with the end-product rule) -> DRV-M7 / DRV-W7 / DRV-C7',
   why='Review M5: donor kt/ratio unknown; drive must meet 30-39 N m/wheel continuous on 12 % with margin.'),
 'G5a': dict(kind='deleted', real=0.0, status='est', origin='LOCAL', fix='M5', item='DELETED: casters from donor -> DRV-C7', why='No donor chair.'),
 'G5b': dict(kind='deleted', real=0.0, status='est', origin='IE', fix='m5', item='DELETED: tyre sealant (solid/foam-filled tyres on DRV-W7)', why='Review m5: hawthorn/blackthorn flail debris.'),
 'G6': dict(kind='substitution', real=usd_ie(915.00), status='checked-11Nov', origin='US', fix='B4/M5',
   item='Motor controller Roboteq FDCG3260T (RoboG4): 3 ch brushed DC, 40 A cont / 60 A 30 s per ch, 60 V, encoder inputs, CAN/USB/RS485, '
        'certified STO (PL e, Cat 3, SIL 3). Ch1/Ch2 = drive motors (ALIM 40 A), Ch3 = mast actuator (replaces KA1/KA2 reversing relays). '
        'Replaces Cytron MDDS30.',
   url='https://www.roboteq.com/products/products-brushed-dc-motor-controllers/fdcg3260t-328-detail',
   why='US$915 (fetched). STO inputs driven by the PNOZ s5 delayed semiconductor outputs (stop category 1). 40 A cont covers 24.8 A/motor at 39 N m, '
       'and 31 A at 39 x 1.25 N m (revG/g7elec/drive_calc_g7.json). Smaller SDCMG3260T (US$715) is 20 A cont -> too small.'),
 'G8': dict(kind='correction', real=13.0, status='est', origin='CN', fix='X3 tilt IMU',
   item='Yaw-lock solenoid pin + AS5600 yaw encoder (crossbar tilt IMU DELETED - unwired, I2C over 3 m through yaw + hinge not workable)',
   why='GA Rev B X3: tilt IMU had no wiring. Mast angle now from the actuator position output (G10 CAHB "with position output") + AS5600; tug pitch from the FC IMU.'),
 'G10': dict(kind='substitution', real=round(617.61 / 1.24 * 1.23 + 10, 2), status='checked-11Nov', origin='GR', fix='M6/X3 actuator',
   item='Mast actuator Ewellix CAHB-20-F3E (24 V, manual override, 4,500 N rated / 6,300 N clutch, IP69K/66M, -40..+85 C, position output), '
        'STROKE 405 mm made to order -> retracted 246+405 = 651 / extended 1,056 mm pin-pin (window 656-1,042) + 2 bushes to the D12 clevis pins (est EUR 10). '
        'Replaces ELA 0041941-1 (BOM) and LINAK LA36 (CAD). CONDITION: Ewellix to confirm >= 3.1 kN at -20 C, else buy LA36 (EUR 1,058.45).',
   url='https://eshop.papadopoulos-sa.com/linear-actuators/75292-ewellix-cahb-20-f3e-4500696-bba0pt-000-linear-actuators-7333314280503.html',
   why='EUR 617.61 incl. 24 % GR VAT for the 450 mm-stroke catalogue variant (fetched); 405 mm is a stroke code of the same family (quote needed). '
       'RL formula 246+S from the Ewellix CAHB catalogue IL-06022-2 p.19. 4,500 N = 1.8 x the 2,473 N sim peak at 0..40 C. Saves ~EUR 445 vs LA36.'),
 'G13': dict(kind='correction', real=10.0, status='est', origin='CN', fix='B4',
   item='IP67 NC switches: seat + wheel-contact (bumper switches moved to BMP-G7 safety switches)', why='Bumper sensing is now a PL d safety input.'),
 'G19': dict(kind='correction', real=48.0, status='excerpt', origin='CN', fix='M9',
   item='RTK base only: LC29HBS base core board + L1/L5 antenna + ESP32 NTRIP server (rover LC29HDA deleted -> HDG-G7 UM982)',
   why='Rover half removed (est -EUR 30). Base RTCM3 (MSM, L1/L5) feeds the UM982 rover; bench-check the L1/L5-only correction set with the UM982 before the walk test.'),
 'G22': dict(kind='correction', real=10.0, status='est', origin='IE', fix='B4', item='EVA foam faces for the front bumper bar and rear corner bumpers (tape switches deleted)',
   why='Tape switches are not safety-rated; actuation is now by BMP-G7 positive-opening switches.'),
 'S1': dict(kind='correction', real=12.0, status='est', origin='CN', fix='X3 S1 / M5',
   item='Main fuse F1 50 A MIDI (slow) + holder at battery +', why='BOM said 30 A, harness 40 A; G7 drive gives 24 A climb / ~47 A peak at ALIM 40 A/ch -> 50 A, below the 60 A BMS, above the load.'),
 'S5': dict(kind='substitution', real=exvat_ie(291.40), status='checked-11Nov', origin='DE', fix='B4/X3 S5',
   item='Safety relay Pilz PNOZ s5 750105 (24 VDC; 2 instant NO + 2 delayed NO relay, 2 instant + 2 delayed semiconductor outputs, delay 0.04-300 s; '
        'PL e Cat 4; cross-fault detection; monitored reset; feedback loop). Replaces the Finder K1 + K2 pair (the G6 BOM bought only one of the two).',
   url='https://www.automation24.com/safety-relay-pilz-750105-pnoz-s5-24vdc-2-n-o-2-n-o-t',
   why='EUR 291.40 ex VAT, in stock (fetched). If the PL d upgrade is NOT adopted, the minimum G6 fix is 2 x Finder 55.34.9.024.0040 + 94.04 (EUR 36).'),
 'S6': dict(kind='correction', real=10.0, status='est', origin='CN', fix='X3 PB-01',
   item='Relays: KC charge path (24 V 40 A + socket) + KR reset (5 V). Actuator reversing pair KA1/KA2 DELETED (actuator on Roboteq ch3)',
   why='Removes 2 of the 3 PB-01 relays that had no pod loom; KC gets the PC-G7 loom.'),
 'S8': dict(kind='substitution', real=35.0, status='est', origin='IE', fix='B4',
   item='E-stop station to ISO 13850: mushroom twist-release, 2 NC positive-opening (dual channel) + 1 NO aux, IP66/67, yellow housing', why='Cat 3 needs two channels; G6 had 1 NC.'),
 'F1': dict(kind='correction', real=round(75 - 37 + 50 * 16 * DKK, 2), status='checked-8Nov', origin='IE', fix='X3 Nord-Lock',
   item='Fasteners A4-70 set as G3; 50 pairs Nord-Lock NL8ss (birgerahandel.dk, 16 DKK/pair at 25+) for the ~49 M8 joints',
   why='GA Rev B fasteners.json: FX-M8 49 joints vs 24 pairs bought.'),
 'L2': dict(kind='correction', real=21.90, status='checked-7Nov', origin='DE', fix='X3 markers',
   item='Red position markers: 2 pairs LED Global LG124 (CAD has 3 markers: mast top + 2 rear)', why='GA Rev B issue list (L).'),
 'L3': dict(kind='correction', real=G6.ex_gb(15.49), status='excerpt', origin='GB', fix='X3 beacon',
   item='Amber beacon LAP MLPB050 (ECE R65 + R10, IP67, 10-30 V, 0.4 A, D120 x 40, 3-bolt PCD 110 mm). SN-59 plate REDRILLED to the LAP 3-hole PCD 110 '
        '(was M10 PCD 100) and CAD envelope changed from CA7045 D130 x 100 to D120 x 40 - confirm PCD on the LAP drawing before laser cutting.',
   url='https://www.bowerspartsonline.co.uk/lighting/beacons-warning-lights/beacons/led-beacons/compact-12v24v-3-bolt-mounting-low-profile-led-flashing-amber-beacon-ece-r10r65',
   why='GA Rev B: BOM beacon vs CAD bolt circle mismatch. The plate change is free inside FAB-G6.'),
 'AU-G6': dict(kind='correction', real=round(133.40 - 6 + 12 + 12, 2), status='excerpt+est', origin='AT', fix='X3 mic',
   item='Two-way audio: Visaton DK 97 IP67 horn (EUR 107.40) + MAX98357A amp + Gore vent + pod USB hub; MIC = USB mic at the mast top (est EUR 12) '
        'on a new 2-port mast-top USB hub HUB2 in the sensor-post box (est EUR 12). I2S ICS-43434 deleted (I2S over 2.9 m not viable).',
   url='https://www.visatonshop.at/en/Industry/Re-Entrant-Horn-Speakers/DK-97-8-Ohm.html', why='GA Rev B: harness H08 expects USB mic + HUB2; HUB2 had no BOM line.'),
 'IND-OPEN': dict(kind='closed', real=24.0, status='est', origin='CN', fix='X3 feelers',
   item='B-GR-62 feeler sensors x2: M8 inductive PNP 3-wire IP67 (closes IND-OPEN). Wired on T3 spare cores 12/13 as FEELER L/R, +24 V/0 V from MJ-01 busbars',
   why='GA Rev B: feelers were unwired and EUR 0.'),
 'RD-G6': dict(kind='correction', real=round(32.78 + 15, 2), status='excerpt+est', origin='DE', fix='X3 radar',
   item='Radar x2 HLK-LD2451 + CP2105 + ASA radomes; ADDED: factory-soldered sealed pigtail (no 2.54 mm header), acrylic conformal coat, 3 mm drain hole + IP67 M8 4-pin connector per radar (est EUR 15)',
   why='GA Rev B: boards protected only by printed covers.'),
}

# ---------------------------------------------------------------- new lines
def new_lines():
    L = []
    L.append(R('DRV-M7', 'Drive', 'Drive gearmotor PAIR peiscooter PEWM-39: brushed 24 V, 450 W each, 39:1 spur gearbox, motor 4,000 rpm, RATED OUTPUT 48 N m, '
               'electromagnetic spring brake (EMB) + hand release, 22 mm shaft / 8 mm key, left + right', usd_ie(815.00), 'checked-11Nov', 'CN',
               'https://www.peipeiscooter.com/products/102',
               'US$815/pair (category page, fetched); 48 N m vendor rating >= 45 N m target (review M5). Derived constants (drive_calc_g7.json): kt 0.046 N m/A, '
               'R 0.20 ohm -> 24.8 A/motor at 39 N m, 31 A at 39 x 1.25. Free speed 2.2 m/s at 29.2 V on 330 mm -> SLS (PNOZ s30) needed. ACCEPTANCE: dyno/pull test per M5 on receipt.', fix='M5'))
    L.append(R('DRV-W7', 'Drive', 'Drive wheels x2: 330 mm (13 in) solid or foam-filled PU tyres on hubs bored 22 mm with 8 mm keyway + retaining bolt', 90.0, 'est', 'CN',
               why='Replaces donor wheels; solid tyres close m5. Re-check crr and traction (B1) with the chosen tyre.', fix='M5/m5'))
    L.append(R('DRV-C7', 'Drive', 'Swivel casters x2: 200 x 50 mm solid PU, ball-bearing fork, plate mount', 60.0, 'est', 'IE', why='Replaces donor casters.', fix='M5'))
    L.append(R('PWR-G7', 'Enclosure & wiring', 'Power-path re-size: 10 mm2 silicone B+ trunk ISO-KM-F1-controller (~1.6 m), 6 mm2 motor runs, 2 x Deutsch DTHD04-1-8 (size 8, 60 A) '
               'motor connectors replacing paired 1.5 mm2 in DT12 pins, M8 lugs, brake leads on DT04-2P; delete F2 25 A', 45.0, 'est', 'CN',
               why='drive_calc_g7.json: 24 A climb, ~47 A peak; drop 0.13 V trunk + 0.17 V motor run.', fix='M5/X3 motor pins'))
    L.append(R('SPD-G7', 'Safety & power dist.', 'Safe speed monitor Pilz PNOZ s30 750330 (standstill + speed, 2 axes, proximity-switch inputs, PL e) for SF3 SLS 0.6 m/s / '
               '0.3 m/s in the mouth; relay outputs in series with the PNOZ s5 input channels', exvat_ie(662.06), 'excerpt', 'DE',
               'https://www.elektronetshop.de/pilz-sicherheitsschaltgeraet-750330-typ-pnoz-s30-24-240vacdc-2-n-o-2-n-c/',
               'EUR 787.85 incl. DE VAT / 662.06 ex (search excerpt; Amazon.de EUR 743). Required because the free speed is 2.2 m/s.', fix='B4'))
    L.append(R('SPD-S7', 'Safety & power dist.', 'Speed sensors for PNOZ s30: 2 x M12 inductive PNP IP67 on a 12-tooth target ring per drive hub (rings in FAB-G6)', 30.0, 'est', 'CN', fix='B4'))
    L.append(R('BMP-G7', 'Safety & power dist.', 'Safety bumpers: front bar + 2 rear corner bumpers on sprung guides, each actuating 2 x positive-opening (IEC 60947-5-1 Annex K) IP67 '
               'safety position switches (4 total, one per channel), 25 mm pre-travel + >= 120 mm foam overtravel', 160.0, 'est', 'DE',
               why='Dual-channel tactile detection (EN ISO 13856-3 bumper principle) into PNOZ s5. Cheaper than 4-wire edges + Mayser SG-EFS 104/4L (EUR 420 each).', fix='B4'))
    L.append(R('RST-G7', 'Safety & power dist.', 'Monitored reset: IP67 blue illuminated reset button on the tug + reset relay for the supervised remote reset (Pi output, camera check first)', 15.0, 'est', 'IE', fix='B4'))
    L.append(R('HDG-G7', 'Navigation', 'Heading: Holybro H-RTK Unicore UM982 dual-antenna (moving-baseline yaw 0.1 deg/1 m baseline, RTK rover, 2 helical antennas + mounts + cables); '
               'antennas >= 0.6 m apart on the fixed sensor post and rear frame; compass disabled', usd_ie(249.99) + 10, 'checked-11Nov', 'CN',
               'https://holybro.com/products/h-rtk-unicore-um982', 'US$249.99 (fetched) + ground-plane brackets est EUR 10. ArduPilot GPS1_TYPE 25, EK3_SRC1_YAW 2.', fix='M9'))
    L.append(R('GR-08S', 'Hitch & grabber', 'Ratchet-pawl lift solenoid GR-08S, SEALED: Landa TU2551 24 V DC tubular push-pull IP65, 0-10 mm, D25 x 51 mm (x2 incl. 1 spare) '
               '+ nitrile boot on the plunger', usd_ie(2 * 15.0) + 3, 'excerpt', 'CN', 'https://www.landamagnet.com/landa-tu2551-12v/24v-dc-screw-mount-tubular-linear-solenoid-10-100-duty-cycle-0-35n-force-l51x25mm-actuator',
               'US$15/pc, MOQ 2 (search excerpt). Was a 12 V open-frame part with no BOM line. Driven 24 V hit-and-hold (100 % 0.2 s, then 30 % PWM).', fix='M10/X3 GR-08S'))
    L.append(R('GR-08D', 'Hitch & grabber', 'GR-08S drive + interlock: 1 channel of the L6 MOSFET board (logic-level, >= 5 A) with PWM, flyback diode, new fuse F14 2 A on the 24 V SIG busbar; '
               'M8 PNP IP67 pawl-up sensor in the pre-tip / pre-release interlock; T3b 7-core PUR 0.5 mm2 2.9 m through the hinge (solenoid +/-, pawl-up, 2 spare)', 32.0, 'est', 'CN',
               why='GA Rev B: no wiring, fuse or driver channel; T3 has only the 2 spare cores now used by the feelers.', fix='M10/X3 GR-08S'))
    L.append(R('HTR-G7', 'Power', 'Pack heater: 2 x RS PRO silicone mat 12 V 15 W 75 x 200 mm (RS 245-562) in series on 24 V (30 W peak, PWM to 15 W mean from the dock controller), '
               'KSD9700 40 C NC bimetal cutout in series, logic-level MOSFET; charge enable stays NTC >= +3 C', 2 * 54.59 + 6, 'checked-11Nov', 'IE',
               'https://ie.rs-online.com/web/p/heater-pads/0731350', 'RS IE shows EUR 54.59 incl. VAT for 245-562 (the listed alternative to 731-350). Heater runs only on dock power.', fix='m3/E-3'))
    L.append(R('PC-G7', 'Enclosure & wiring', 'Pod <-> PB-01 control loom: 6 x 0.5 mm2 LiYCY (KC coil +/-, INA226 SDA/SCL/+3V3/0V) 0.6 m + DT06-6S/DT04-6P pair', 12.0, 'est', 'CN',
               why='GA Rev B: KC/KA in PB-01 fed from the pod with no loom. KA1/KA2 deleted, so only KC + INA226 remain.', fix='X3 PB-01'))
    L.append(R('FL1-G7', 'Enclosure & wiring', 'W109 protection: FL1 10 A moved to ISO-2 (origin of the 1.5 mm2 run) in a sealed inline ATO holder', 5.0, 'est', 'CN',
               why='GA Rev B: W109 1.5 mm2 (16 A) was protected only by F1 until FL1 in PB-01.', fix='X3 W109'))
    L.append(R('YS-G7', 'Hitch & grabber', 'Yaw stops: YS-01 4 x UHMW-PE blocks (machined) + YS-02 2 x M10 A4 pins with PA sleeves (drawn and added to Drawings_G6)', 18.0, 'est', 'LOCAL',
               why='GA Rev B: in CAD only, no BOM line.', fix='X3 yaw stops'))
    return L

DELETE_FROM_TOTAL = set()
LOG_G7 = {'SHIP-US': (45, 'Roboteq US -> IE courier, est'), 'SHIP-PEWM': (120, 'PEWM-39 pair ~12 kg by air from Shanghai (peiscooter "extra ship cost"), est'),
          'SHIP-HB': (25, 'Holybro UM982, est'), 'SHIP-GR': (25, 'Papadopoulos (Ewellix) GR -> IE, est'), 'SHIP-PILZ': (15, 'automation24 + elektronetshop (DE), est'),
          'SHIP-RS': (8, 'RS Ireland heater mats, est'), 'SHIP-LANDA': (20, 'Landa solenoids CN, est')}
# import duty (EUR, on customs value) for non-EU lines that are not small: DC motors 8501 2.7 %, controller 8537/8504 ~2.1 % est, GNSS 8526 3.7 % est
DUTY_G7 = round((815 * USD * 0.027 + 915 * USD * 0.021 + 249.99 * USD * 0.037) * (1 + VAT) + 2 * M.DUTY_EUR * (1 + VAT), 2)

COSTDOWN = [
 ('CD1', 'STO route: keep Cytron MDDS30 (30 A/ch) + 2 x DC contactors with mirror contacts in series in the motor supply, monitored by the PNOZ s5 feedback loop; '
         'actuator back on 2 relays', -(usd_ie(915) - 82.95 - 150 - 6), 'Cat 3 / PL d still reachable (contactor redundancy + EDM). Loses certified STO, '
         'encoder closed loop and per-motor current limit in hardware (do the limit in Pi firmware). Contactor + relay prices est.'),
 ('CD2', 'Tray CH-01 + CH-14 in 2 mm Z275 instead of 5083 (review s.8 item 2)', -90.0, 'Team figure; extra 6.9 kg replaces ballast sand.'),
 ('CD3', 'Horn: IP66 PA/marine horn speaker instead of Visaton DK 97 (review s.8 item 3)', -70.0, 'Unverified; check the 2-way audio level.'),
 ('CD4', 'GR-08S: drive the pawl lift from a 2nd lobe on the GR-07 cam (no solenoid, no driver, no T3b cores)', -38.0, 'Review M10 option; needs the cam re-timed and a MuJoCo re-check.'),
 ('CD5', 'Safety relay: equivalent PL e dual-channel delay relay from a second brand (e.g. Schmersal SRB-E or Phoenix PSR) instead of PNOZ s5', -100.0, 'Unverified estimate; must keep delayed semiconductor outputs for STO or add a contact expansion.'),
 ('CD6', 'Holybro UM982 bought from an EU stockist on promotion, or ArduSimple UM982 board with own antennas, if cheaper on the day', -30.0, 'Market dependent.'),
 ('CD8', 'SF3 by inherent design: a gearmotor whose free speed is <= 0.8 m/s at 29.2 V (e.g. ~80:1 on the 330 mm wheel) plus a risk assessment that accepts the inherent limit -> delete PNOZ s30 + speed sensors', -(exvat_ie(662.06) + 30), 'Conditional: needs a verified slower gearmotor with >= 45 N m (not found with a datasheet today) and the ISO 12100 sign-off; otherwise keep SPD-G7.'),
 ('CD7', 'Drop the F405 FC only if A-7 chooses option (ii) (Pi + safety layer); fence then runs on the Pi', -35.0, 'Conditional: the FC hosts the EKF/UM982 yaw and the firmware fence in the recommended stack.'),
]

def build():
    S6 = G6.build(); out = []
    for r in S6['lines']:
        n = copy.deepcopy(r); n['g6_real'] = r['real']; n.setdefault('fix', '')
        if r['id'] in OVR:
            o = OVR[r['id']]; n.update({k: o[k] for k in o}); n.setdefault('url', r.get('url', ''))
            if 'url' not in o: n['url'] = r.get('url', '')
        else:
            n['kind'] = 'unchanged'
        out.append(n)
    for r in new_lines():
        r['g6_real'] = 0.0; out.append(r)
    log = [dict(id=x['id'], g6_real=x['real'], real=(round(DUTY_G7 + x['real'], 2) if x['id'] == 'DUTY' else x['real']), why='') for x in S6['log']]
    for x in log:
        if x['id'] == 'DUTY': x['why'] = 'G6 duty + G7 non-EU lines (motors 2.7 %, controller ~2.1 %, GNSS ~3.7 %, +2 small lines) incl. VAT on duty'
    for k, (v, w) in LOG_G7.items():
        log.append(dict(id=k, g6_real=0.0, real=float(v), why=w))
    parts = sum(r['real'] for r in out); lg = sum(x['real'] for x in log)
    cont = 0.0
    for r in out:
        st = r['status'].split('+')[-1] if '+' in r['status'] else r['status']
        if r['origin'] == 'LOCAL': k = G4.CONT_LOCAL_USED
        elif st.startswith('checked'): k = 0.05
        else: k = G4.CONT.get(st, 0.12)
        cont += r['real'] * k
    cont += G4.CONT_LOG * lg
    tot = dict(parts=round(parts, 2), logistics=round(lg, 2), subtotal=round(parts + lg, 2), risk_weighted_contingency=round(cont, 2),
               with_risk_weighted=round(parts + lg + cont, 2), with_15pct=round((parts + lg) * 1.15, 2))
    cd = round(sum(c[2] for c in COSTDOWN if c[0] not in ('CD7', 'CD8')), 2)
    return dict(g6=S6['g6'], g7=tot, lines=out, log=log, costdown=COSTDOWN, costdown_sum_excl_conditional=cd,
                la36_alternative_delta=round(1058.45 - out[[r['id'] for r in out].index('G10')]['real'], 2))

def write():
    S = build()
    with open(os.path.join(H, 'bom_revG7.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'area', 'item', 'eur_G6', 'eur_G7', 'delta', 'kind', 'fix_ref', 'status', 'order_group', 'url', 'why'])
        for r in S['lines']:
            w.writerow([r['id'], r['area'], r['item'], r['g6_real'], r['real'], round(r['real'] - r['g6_real'], 2), r['kind'], r.get('fix', ''), r['status'], r['origin'], r.get('url', ''), r.get('why', '')])
        for x in S['log']:
            w.writerow([x['id'], 'Logistics', '', x['g6_real'], x['real'], round(x['real'] - x['g6_real'], 2), 'logistics', '', 'est', '', '', x['why']])
        for k, lab in (('parts', 'TOTAL parts (incl. IE VAT)'), ('subtotal', 'TOTAL incl. shipping + duty'), ('with_risk_weighted', 'TOTAL + risk-weighted contingency (ALL-IN)')):
            w.writerow(['', '', lab, S['g6'][k], S['g7'][k], round(S['g7'][k] - S['g6'][k], 2)])
        w.writerow([]); w.writerow(['', '', 'COST-DOWN (no capability cut) - not applied in the totals'])
        for c in S['costdown']:
            w.writerow([c[0], 'Cost-down', c[1], '', round(c[2], 2), '', 'cost-down', '', '', '', '', c[3]])
    json.dump(dict(meta=dict(date=DATE, base='bom_revG6.py', fx=dict(USD=USD, GBP=GBP, DKK=DKK), vat_ie=VAT, note='revG/ELEC_SAFETY_G7.md'),
                   totals=dict(g6=S['g6'], g7=S['g7']), overrides=OVR, lines=S['lines'], logistics=S['log'],
                   costdown=[dict(id=c[0], what=c[1], eur=round(c[2], 2), note=c[3]) for c in S['costdown']],
                   costdown_sum_excl_conditional=S['costdown_sum_excl_conditional'], la36_alternative_delta=S['la36_alternative_delta']),
              open(os.path.join(H, 'bom_revG7.json'), 'w'), indent=1)
    return S
if __name__ == '__main__':
    S = write(); print('G6', S['g6']); print('G7', S['g7']); print('cost-down (excl CD7/CD8):', S['costdown_sum_excl_conditional'], ' LA36 instead of CAHB: +', S['la36_alternative_delta'])
    for r in S['lines']:
        if abs(r['real'] - r['g6_real']) > 0.01: print('%-9s %8.2f -> %8.2f  %-12s %s' % (r['id'], r['g6_real'], r['real'], r['kind'], r.get('fix', '')))
    for x in S['log']:
        if abs(x['real'] - x['g6_real']) > 0.01: print(x['id'], x['g6_real'], '->', x['real'])
