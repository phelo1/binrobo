"""G5 explicit bin models from manufacturer data sheets / drawings (mm -> m). Each entry: published values + what was scaled from a
drawing + what is unknown (sampled). Sources in RESULTS_G5_binrange.md section 1.
 bar_abs : handle-bar centre height above ground, upright (value, +/- spread sampled uniformly)
 bar_x   : bar centre behind the wheel axle, towards the tug (value, +/-)
 cb      : bar centre to the body back face at rim height (value, +/-)
 sections: list of (shape, r_min, r_max) to sweep; published single section -> one entry
 web     : inner half-spacing between the outer handle webs (value, +/-)
 knuckles: inner hinge knuckles on the bar [(y centre, half thickness)] or 'maybe' (sampled 50 %)"""
SWEEP=[('tube',0.0125,0.0125),('tube',0.015,0.015),('tube',0.021,0.021),('moulded',0.019,0.021)]   # D25, D30, D42 round, 38-42 moulded
BINS={
 'WEB140':dict(name='Weber 140 L',cls='narrowest',H=1.050,W=0.475,D=0.545,comb=1.001,wheel=0.20,track=0.479,empty=10.0,fill_full=56.0,
               bar_abs=(0.998,0.008),bar_x=(0.143,0.008),cb=(0.075,0.006),sections=SWEEP,web=(0.1685,0.003),knuckles=[(0.045,0.0045)],
               src='Weber 140 L dimensioned drawing (w-weber.com PDF): H 1050, W 475, D 545, axle 479, wheels 200, handle span 355 o/a; bar height/offset scaled from the drawing'),
 'ESE140CL':dict(name='ESE 140 CL',cls='narrowest',H=1.030,W=0.480,D=0.553,comb=0.969,wheel=0.20,track=0.478,empty=9.0,fill_full=61.0,
               bar_abs=(0.981,0.015),bar_x=(0.150,0.015),cb=(0.072,0.012),sections=[('tube',0.0135,0.0135)],web=(0.172,0.012),knuckles='maybe',
               src='ESE brochure (H 1030, W 480, D 553, comb 969, 9 kg, max 70), ESE manual (axle 478), ESE product page (continuous handle approx. D27)'),
 'ESE240SL':dict(name='ESE 240 SL (200 mm wheels)',cls='widest',H=1.079,W=0.583,D=0.737,comb=1.005,wheel=0.20,track=0.569,empty=13.0,fill_full=97.0,
               bar_abs=(1.017,0.015),bar_x=(0.152,0.013),cb=(0.072,0.012),sections=[('tube',0.0135,0.0135)],web=(0.202,0.013),knuckles='maybe',
               src='ESE brochure (H 1079, W 583, D 737, comb 1005, 13 kg, max 110, wheels 200/250), ESE manual (axle 569), ESE 240 SL page (continuous handle D27)'),
 'ESE240SL250':dict(name='ESE 240 SL (250 mm wheels)',cls='widest',H=1.104,W=0.583,D=0.737,comb=1.030,wheel=0.25,track=0.580,empty=13.6,fill_full=96.4,
               bar_abs=(1.042,0.015),bar_x=(0.152,0.013),cb=(0.072,0.012),sections=[('tube',0.0135,0.0135)],web=(0.202,0.013),knuckles='maybe',
               src='as ESE 240 SL; 250 mm wheel option raises the body ~25 mm; axle width with 250 mm wheels not published (580 assumed)'),
 'SULO240':dict(name='SULO Citybac 240',cls='widest',H=1.075,W=0.582,D=0.728,comb=0.991,wheel=0.20,track=0.575,empty=10.2,fill_full=99.8,
               bar_abs=(1.012,0.010),bar_x=(0.164,0.010),cb=(0.060,0.010),sections=SWEEP,web=(0.197,0.005),knuckles=[(0.038,0.005)],
               src='SULO Citybac 240 data sheet (H 1068-1077, comb 998, D 734, W 583, 10.2 kg, max 110) + brochure ("oval, corrugated and bigger handle bar"); bar height/offset/web spacing scaled from the data-sheet drawing; axle width not published (575 assumed)'),
 'ESE240CL':dict(name='ESE 240 CL (lowest handle)',cls='lowest',H=1.003,W=0.580,D=0.738,comb=0.938,wheel=0.20,track=0.569,empty=11.0,fill_full=99.0,
               bar_abs=(0.950,0.015),bar_x=(0.152,0.013),cb=(0.072,0.012),sections=[('tube',0.0135,0.0135)],web=(0.202,0.013),knuckles='maybe',
               src='ESE brochure (H 1003, W 580, D 738, comb 938, 11 kg, max 110), ESE manual (axle 569), ESE 240 CL page (continuous handle approx. D27)'),
 'CRA240':dict(name='Craemer MGBneo 240 (tallest)',cls='tallest',H=1.100,W=0.580,D=0.740,comb=None,wheel=0.20,track=0.590,empty=12.0,fill_full=96.0,
               bar_abs=(1.061,0.012),bar_x=(0.153,0.008),cb=(0.084,0.008),sections=[('tube',0.015,0.015)],web=(0.202,0.013),knuckles='maybe',
               src='Craemer MGBneo page + data sheet (W 580+/-5, D 740 max, H 1100 max, 96 kg, wheels 200/250, handle D30) + technical drawing (wheels 590 max o/a; bar height/offset scaled); empty mass not published (12 kg assumed)'),
}
