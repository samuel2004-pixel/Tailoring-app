"""
certificate.py
Generates a filled "Certificate of Completion" PDF by overlaying the
student's name and course dates on top of the centre's official
3-month / 6-month certificate templates (assets/cert_3_months.pdf,
assets/cert_6_months.pdf), using the exact text coordinates measured
from those templates so the result looks identical to a hand-filled
certificate.
"""
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from pypdf import PdfReader, PdfWriter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

TEMPLATES = {
    3: os.path.join(ASSETS_DIR, "cert_3_months.pdf"),
    6: os.path.join(ASSETS_DIR, "cert_6_months.pdf"),
}

PAGE_W, PAGE_H = 792, 612  # landscape letter, matches the templates

# Cream background colour used inside the certificate border (matches the
# template's inner panel), used to blank out the printed underscores before
# writing the real date on top.
CREAM = Color(0.882, 0.882, 0.761)

# Coordinates below were measured directly from the certificate template
# PDFs (pdfplumber word/line extraction), in points, bottom-left origin.
NAME_CENTER_X = 501.5
NAME_BASELINE_Y = 325
NAME_FONT_SIZE = 20

DATE1_BOX = (508, 209.5, 607.5, 226)   # start date blank (x0, y0, x1, y1)
DATE2_BOX = (628.5, 209.5, 724, 226)   # end date blank
DATE_FONT_SIZE = 13


def _draw_date(c, box, text):
    x0, y0, x1, y1 = box
    c.setFillColor(CREAM)
    c.rect(x0, y0, x1 - x0, y1 - y0, stroke=0, fill=1)
    c.setFillColor(Color(0, 0, 0))
    c.setFont("Helvetica", DATE_FONT_SIZE)
    cx = (x0 + x1) / 2
    cy = y0 + (y1 - y0) / 2 - 4
    c.drawCentredString(cx, cy, text)


def generate_certificate(name, duration_months, start_date, end_date):
    """
    name: student's full name (str)
    duration_months: 3 or 6 (int)
    start_date, end_date: strings already formatted as DD/MM/YYYY
    Returns: bytes of the finished, filled certificate PDF.
    """
    duration_months = 6 if int(duration_months) >= 5 else 3
    template_path = TEMPLATES[duration_months]

    # Build the overlay (name + dates) as its own single-page PDF
    overlay_buf = io.BytesIO()
    c = canvas.Canvas(overlay_buf, pagesize=(PAGE_W, PAGE_H))

    c.setFillColor(Color(0, 0, 0))
    c.setFont("Helvetica-Bold", NAME_FONT_SIZE)
    c.drawCentredString(NAME_CENTER_X, NAME_BASELINE_Y, name.strip())

    _draw_date(c, DATE1_BOX, start_date)
    _draw_date(c, DATE2_BOX, end_date)

    c.save()
    overlay_buf.seek(0)

    # Merge overlay onto the template
    base_reader = PdfReader(template_path)
    overlay_reader = PdfReader(overlay_buf)

    writer = PdfWriter()
    base_page = base_reader.pages[0]
    base_page.merge_page(overlay_reader.pages[0])
    writer.add_page(base_page)

    out_buf = io.BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue()
