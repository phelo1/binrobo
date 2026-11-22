#!/usr/bin/env python3
"""Assemble the drawing sheets (sheets/sheetNN.png, A3 landscape at 200 dpi) into one A3 PDF and a zip of the PNG files.
usage: make_pdf.py <out_dir> <pdf_name> <zip_name> <title>"""
import os, sys, glob, zipfile
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas

H = os.path.dirname(os.path.abspath(__file__))
out, pdf, zname, title = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
sheets = sorted(glob.glob(os.path.join(H, 'sheets', 'sheet*.png')))
W, Ht = landscape(A3)
c = canvas.Canvas(os.path.join(out, pdf), pagesize=(W, Ht))
c.setTitle(title); c.setAuthor('Claude (reviewer and tester), for Brian'); c.setSubject('Concept drawings, not for manufacture')
for s in sheets:
    c.drawImage(s, 0, 0, width=W, height=Ht)
    c.showPage()
c.save()
with zipfile.ZipFile(os.path.join(out, zname), 'w', zipfile.ZIP_DEFLATED) as z:
    for s in sheets:
        z.write(s, os.path.basename(s))
print(len(sheets), 'sheets ->', os.path.join(out, pdf), round(os.path.getsize(os.path.join(out, pdf)) / 1e6, 1), 'MB')
