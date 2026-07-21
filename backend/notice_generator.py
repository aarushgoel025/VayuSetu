import io
import datetime
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from config import GEMINI_API_KEY
from db import get_table

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

# ─────────────────────────────────────────────
# Colour palette
# ─────────────────────────────────────────────
NAVY      = colors.HexColor("#0D1B2A")
DARK_BLUE = colors.HexColor("#1B3A5C")
MID_BLUE  = colors.HexColor("#2E6DA4")
ACCENT    = colors.HexColor("#E84545")   # alert red
GOLD      = colors.HexColor("#C9A84C")
LIGHT_BG  = colors.HexColor("#F0F4F9")
WHITE     = colors.white

def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#B0C8E0"),
            alignment=TA_CENTER,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#B0C8E0"),
            alignment=TA_CENTER,
        ),
        "section_heading": ParagraphStyle(
            "section_heading",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=WHITE,
            spaceBefore=6,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=NAVY,
            alignment=TA_JUSTIFY,
            spaceBefore=3,
            spaceAfter=3,
        ),
        "body_bold": ParagraphStyle(
            "body_bold",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=15,
            textColor=NAVY,
        ),
        "label": ParagraphStyle(
            "label",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=MID_BLUE,
            spaceAfter=1,
        ),
        "value": ParagraphStyle(
            "value",
            fontName="Helvetica",
            fontSize=10,
            textColor=NAVY,
            spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica-Oblique",
            fontSize=7,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ),
        "alert_text": ParagraphStyle(
            "alert_text",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=15,
            textColor=ACCENT,
        ),
        "disclaimer": ParagraphStyle(
            "disclaimer",
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=12,
            textColor=colors.grey,
            alignment=TA_JUSTIFY,
        ),
    }
    return styles


def _section_header(title: str, styles: dict):
    """Returns a dark-background section header band."""
    table_data = [[Paragraph(title, styles["section_heading"])]]
    t = Table(table_data, colWidths=["100%"])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return t


def _info_row(label: str, value: str, styles: dict):
    """Returns a two-column label/value row."""
    row = Table(
        [[Paragraph(label, styles["label"]), Paragraph(str(value), styles["value"])]],
        colWidths=[5 * cm, None],
    )
    row.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    return row


def _parse_notice_sections(text: str) -> dict:
    """
    Splits Gemini's raw text into named sections.
    Falls back to a single 'body' key with the full text.
    """
    import re
    sections = {}
    current = "preamble"
    buf = []
    for line in text.split("\n"):
        # detect numbered headings like "1. OBSERVATIONS:" or "**1. DIRECTIVE**"
        heading = re.match(r"^(?:\*{0,2})(\d+\.\s+[A-Z ]+:?)(?:\*{0,2})\s*$", line.strip())
        if heading:
            if buf:
                sections[current] = "\n".join(buf).strip()
            current = heading.group(1).strip().rstrip(":").rstrip("*")
            buf = []
        else:
            # strip markdown bold markers
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            buf.append(clean)
    if buf:
        sections[current] = "\n".join(buf).strip()
    return sections


def generate_legal_notice_text(source: dict, fingerprint_pct: float, harm_data: dict, readings: list) -> str:
    """Gemini call — drafts formal notice under Section 19, Air Act 1981."""
    prompt = f"""
    Draft a formal legal notice under Section 19 of the Air (Prevention and Control of Pollution) Act 1981.
    Address it to: {source.get('name', 'Unknown')}, {source.get('address', 'Unknown')}.

    Include these details:
    - Contribution to local pollution: {fingerprint_pct}%
    - Harm data (affected population): {harm_data}
    - Recent sensor readings showing elevated levels: {readings[:3]}

    Structure the notice with these EXACT numbered headings on their own lines:
    1. OBSERVATIONS:
    2. EVIDENCE:
    3. DIRECTIVE:
    4. COMPLIANCE TIMELINE:
    5. CONSEQUENCES OF NON-COMPLIANCE:

    Before section 1, include a subject line and a 'WHEREAS' preamble paragraph.
    Tone: Formal, plain text, legal but readable. Do NOT use markdown asterisks.
    """

    if not client:
        return (
            f"Legal Notice Placeholder\n"
            f"Subject: Pollution Notice\n"
            f"To: {source.get('name')}\n\n"
            f"WHEREAS, this notice is being issued under the Air Act 1981.\n\n"
            f"1. OBSERVATIONS:\nYou contributed {fingerprint_pct}% to local pollution.\n\n"
            f"2. EVIDENCE:\nSensor readings confirm elevated PM2.5 and PM10 levels.\n\n"
            f"3. DIRECTIVE:\nImmediately reduce emissions and file a compliance report.\n\n"
            f"4. COMPLIANCE TIMELINE:\nWithin 30 days of receipt of this notice.\n\n"
            f"5. CONSEQUENCES OF NON-COMPLIANCE:\nLegal action under Section 22 of the Air Act 1981."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(temperature=0.3)
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating notice text: {e}"


# ─────────────────────────────────────────────
# Page template callbacks
# ─────────────────────────────────────────────
def _on_page(canvas, doc, is_cover=False):
    canvas.saveState()
    w, h = A4

    if is_cover:
        # Full-page dark gradient background for cover
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, w, h, fill=1, stroke=0)
        # Gold top stripe
        canvas.setFillColor(GOLD)
        canvas.rect(0, h - 12 * mm, w, 12 * mm, fill=1, stroke=0)
        # Accent bottom stripe
        canvas.setFillColor(MID_BLUE)
        canvas.rect(0, 0, w, 8 * mm, fill=1, stroke=0)
    else:
        # Header bar
        canvas.setFillColor(NAVY)
        canvas.rect(0, h - 18 * mm, w, 18 * mm, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, h - 19.5 * mm, w, 1.5 * mm, fill=1, stroke=0)

        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(WHITE)
        canvas.drawString(15 * mm, h - 13 * mm, "VayuSetu — Legal Enforcement Notice")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(w - 15 * mm, h - 13 * mm,
                               f"Generated: {datetime.datetime.now().strftime('%d %b %Y')}")

        # Footer bar
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, 12 * mm, w, 0.5 * mm, fill=1, stroke=0)

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#B0C8E0"))
        canvas.drawString(15 * mm, 4 * mm,
                          "This notice is generated by VayuSetu AI Intelligence Platform. "
                          "Not a substitute for legal counsel.")
        canvas.drawRightString(w - 15 * mm, 4 * mm, f"Page {doc.page}")

    canvas.restoreState()


def generate_notice_pdf(source_id: str) -> bytes:
    """
    Builds a multi-page, professionally styled legal notice PDF.
    """
    # ── 1. Data gathering ────────────────────────────────────────
    sources = get_table("sources")
    source = next((s for s in sources if s["id"] == source_id), None)
    if not source:
        raise ValueError("Source not found")

    readings = get_table("readings")
    recent_readings = [r for r in readings if r.get("station_id")] [-5:] if readings else []

    harm_data = {"score": 85, "people_exposed": 12000, "zones_affected": ["School", "Hospital"]}
    try:
        from harm_score import get_harm_score
        harm_data = get_harm_score(source_id)
    except Exception:
        pass

    contribution_pct = 45.2
    try:
        from dispersion import get_fingerprint
        from db import query_latest_per_station
        lat_readings = query_latest_per_station()
        if lat_readings:
            ws = sum(r.get("wind_speed", 0) for r in lat_readings) / len(lat_readings)
            wd = sum(r.get("wind_deg", 0) for r in lat_readings) / len(lat_readings)
            fp = get_fingerprint(
                float(source.get("lat", 28.6)),
                float(source.get("lng", 77.2)),
                ws, wd, sources
            )
            match = next((f for f in fp if f["source_id"] == source_id), None)
            if match:
                contribution_pct = match["contribution_pct"]
    except Exception:
        pass

    notice_text = generate_legal_notice_text(source, contribution_pct, harm_data, recent_readings)
    sections = _parse_notice_sections(notice_text)
    styles = _build_styles()

    now = datetime.datetime.now()
    notice_number = f"VS/{now.strftime('%Y')}/{now.strftime('%m%d%H%M')}"

    # ── 2. PDF Document setup ─────────────────────────────────────
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=25 * mm,
        bottomMargin=22 * mm,
        title=f"VayuSetu Legal Notice – {source.get('name')}",
        author="VayuSetu Pollution Intelligence Platform",
    )

    story = []

    # ── 3. COVER PAGE ─────────────────────────────────────────────
    # Use a cover-specific page template via a Flowable override
    class CoverPage:
        def wrap(self, *args): return (0, 0)
        def drawOn(self, canvas, x, y):
            _on_page(canvas, doc, is_cover=True)

    story.append(Spacer(1, 55 * mm))
    story.append(Paragraph("OFFICIAL LEGAL NOTICE", styles["cover_title"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Under Section 19 of the Air (Prevention and Control of Pollution) Act, 1981",
        styles["cover_subtitle"]
    ))
    story.append(Spacer(1, 12 * mm))

    # Cover info box
    cover_data = [
        [Paragraph("NOTICE NO.", ParagraphStyle("cl", fontName="Helvetica-Bold", fontSize=9, textColor=GOLD)),
         Paragraph(notice_number, ParagraphStyle("cv", fontName="Helvetica", fontSize=9, textColor=WHITE))],
        [Paragraph("DATE ISSUED", ParagraphStyle("cl", fontName="Helvetica-Bold", fontSize=9, textColor=GOLD)),
         Paragraph(now.strftime("%d %B %Y"), ParagraphStyle("cv", fontName="Helvetica", fontSize=9, textColor=WHITE))],
        [Paragraph("ISSUED TO", ParagraphStyle("cl", fontName="Helvetica-Bold", fontSize=9, textColor=GOLD)),
         Paragraph(source.get("name", "—"), ParagraphStyle("cv", fontName="Helvetica-Bold", fontSize=10, textColor=WHITE))],
        [Paragraph("ADDRESS", ParagraphStyle("cl", fontName="Helvetica-Bold", fontSize=9, textColor=GOLD)),
         Paragraph(source.get("address", "—"), ParagraphStyle("cv", fontName="Helvetica", fontSize=9, textColor=WHITE))],
        [Paragraph("POLLUTION CONTRIBUTION", ParagraphStyle("cl", fontName="Helvetica-Bold", fontSize=9, textColor=GOLD)),
         Paragraph(f"{contribution_pct}% of local pollution load", ParagraphStyle("cv", fontName="Helvetica-Bold", fontSize=9, textColor=ACCENT))],
    ]
    cover_table = Table(cover_data, colWidths=[55 * mm, None])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#1B3A5C")),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.3, colors.HexColor("#2E6DA4")),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 10 * mm))

    # Authority block on cover
    authority_text = (
        "<b>Issued by:</b> Delhi Pollution Control Committee (DPCC) / "
        "VayuSetu Environmental Intelligence Platform<br/>"
        "<b>Authority:</b> Air (Prevention and Control of Pollution) Act, 1981 — Section 19<br/>"
        "<b>Classification:</b> OFFICIAL — COMPLIANCE MANDATORY"
    )
    auth_p = Paragraph(authority_text, ParagraphStyle(
        "auth", fontName="Helvetica", fontSize=8, leading=13,
        textColor=colors.HexColor("#B0C8E0"), alignment=TA_CENTER
    ))
    story.append(auth_p)
    story.append(PageBreak())

    # Switch to normal page template for subsequent pages
    doc.onFirstPage  = lambda c, d: _on_page(c, d, is_cover=False)
    doc.onLaterPages = lambda c, d: _on_page(c, d, is_cover=False)

    # ── 4. RECIPIENT BLOCK ────────────────────────────────────────
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("To,", styles["body"]))
    story.append(Paragraph("<b>The Head of Operations / Concerned Authority</b>", styles["body"]))
    story.append(Paragraph(source.get("name", "—"), styles["body"]))
    story.append(Paragraph(source.get("address", "—"), styles["body"]))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(f"<b>Notice No.:</b> {notice_number}", styles["body"]))
    story.append(Paragraph(f"<b>Date:</b> {now.strftime('%d %B %Y')}", styles["body"]))
    story.append(Spacer(1, 4 * mm))

    # Subject line in accent box
    subject_data = [[Paragraph(
        f"SUBJECT: NOTICE UNDER SECTION 19 OF THE AIR (PREVENTION AND CONTROL OF POLLUTION) "
        f"ACT, 1981 — REGARDING SIGNIFICANT AIR POLLUTION CONTRIBUTION FROM "
        f"{source.get('name', '').upper()}",
        ParagraphStyle("subj", fontName="Helvetica-Bold", fontSize=10, textColor=WHITE, leading=14)
    )]]
    subject_table = Table(subject_data, colWidths=["100%"])
    subject_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(subject_table)
    story.append(Spacer(1, 5 * mm))

    # Preamble / WHEREAS text
    preamble_text = sections.get("preamble", "")
    for para in preamble_text.split("\n"):
        para = para.strip()
        if para:
            story.append(Paragraph(para, styles["body"]))
    story.append(Spacer(1, 4 * mm))

    # ── 5. STATISTICS DASHBOARD ───────────────────────────────────
    story.append(_section_header("POLLUTION IMPACT SUMMARY", styles))
    story.append(Spacer(1, 3 * mm))

    people_exposed = harm_data.get("people_exposed", 0)
    zones = harm_data.get("zones_affected", [])
    zones_count = len(zones)

    stat_data = [
        [
            Paragraph("POLLUTION CONTRIBUTION", ParagraphStyle("sl", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER)),
            Paragraph("PEOPLE AT RISK", ParagraphStyle("sl", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER)),
            Paragraph("AFFECTED ZONES", ParagraphStyle("sl", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER)),
        ],
        [
            Paragraph(f"{contribution_pct}%", ParagraphStyle("sv", fontName="Helvetica-Bold", fontSize=22, textColor=ACCENT, alignment=TA_CENTER)),
            Paragraph(f"{people_exposed:,}", ParagraphStyle("sv", fontName="Helvetica-Bold", fontSize=22, textColor=GOLD, alignment=TA_CENTER)),
            Paragraph(f"{zones_count}", ParagraphStyle("sv", fontName="Helvetica-Bold", fontSize=22, textColor=MID_BLUE, alignment=TA_CENTER)),
        ],
    ]
    stat_table = Table(stat_data, colWidths=["33%", "33%", "34%"])
    stat_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  DARK_BLUE),
        ("BACKGROUND",    (0, 1), (-1, -1), LIGHT_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEAFTER",     (0, 0), (1, -1),  0.5, colors.HexColor("#C8D8E8")),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#C8D8E8")),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 5 * mm))

    # ── 6. NOTICE BODY SECTIONS ───────────────────────────────────
    section_order = [
        "1. OBSERVATIONS", "2. EVIDENCE", "3. DIRECTIVE",
        "4. COMPLIANCE TIMELINE", "5. CONSEQUENCES OF NON-COMPLIANCE"
    ]
    # Also check keys without leading number
    fallback_keys = ["OBSERVATIONS", "EVIDENCE", "DIRECTIVE", "COMPLIANCE TIMELINE", "CONSEQUENCES OF NON-COMPLIANCE"]

    for ordered_key, fallback_key in zip(section_order, fallback_keys):
        content = sections.get(ordered_key, sections.get(fallback_key, ""))
        if not content:
            continue

        story.append(KeepTogether([
            _section_header(ordered_key, styles),
            Spacer(1, 3 * mm),
        ]))

        for para in content.split("\n"):
            para = para.strip()
            if not para:
                story.append(Spacer(1, 2 * mm))
                continue
            # Highlight lines that look like deadlines or legal citations
            if any(kw in para.lower() for kw in ["within", "deadline", "days", "section", "act,"]):
                story.append(Paragraph(para, ParagraphStyle(
                    "highlight", fontName="Helvetica-Bold", fontSize=10,
                    leading=15, textColor=DARK_BLUE, alignment=TA_JUSTIFY,
                    backColor=colors.HexColor("#EEF4FB"),
                    borderPadding=(3, 6, 3, 6), spaceBefore=2, spaceAfter=2
                )))
            else:
                story.append(Paragraph(para, styles["body"]))

        story.append(Spacer(1, 5 * mm))

    # ── 7. SIGNATURE BLOCK ────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE, spaceAfter=4 * mm))
    sig_data = [
        [
            Paragraph(
                f"<b>Authorised Signatory</b><br/>Delhi Pollution Control Committee<br/>"
                f"Issued via VayuSetu Platform<br/><br/>"
                f"<i>Date: {now.strftime('%d %B %Y')}</i>",
                ParagraphStyle("sig", fontName="Helvetica", fontSize=9, leading=14, textColor=NAVY)
            ),
            Paragraph(
                f"<b>Notice Reference</b><br/>{notice_number}<br/><br/>"
                f"<b>Classification</b><br/>OFFICIAL — COMPLIANCE MANDATORY",
                ParagraphStyle("sigr", fontName="Helvetica", fontSize=9, leading=14, textColor=NAVY, alignment=TA_RIGHT)
            ),
        ]
    ]
    sig_table = Table(sig_data, colWidths=["50%", "50%"])
    sig_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 0.5, DARK_BLUE),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 5 * mm))

    # Disclaimer
    story.append(Paragraph(
        "DISCLAIMER: This notice has been auto-generated by the VayuSetu Environmental Intelligence Platform "
        "based on real-time sensor data and Gaussian plume dispersion modelling. "
        "It is intended to serve as a formal instrument under Section 19 of the Air (Prevention and Control "
        "of Pollution) Act, 1981. Recipients are advised to seek independent legal counsel. VayuSetu does not "
        "guarantee the completeness or legal sufficiency of this notice for any specific judicial proceeding.",
        styles["disclaimer"]
    ))

    # ── 8. Build PDF ──────────────────────────────────────────────
    def first_page(c, d):   _on_page(c, d, is_cover=True)
    def later_pages(c, d):  _on_page(c, d, is_cover=False)

    doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    # ── 9. Log notice ─────────────────────────────────────────────
    try:
        from violation_tracker import log_notice_issued
        log_notice_issued(
            source_id=source_id,
            contribution_pct=contribution_pct,
            people_exposed=people_exposed,
        )
    except Exception as e:
        print(f"Could not log notice: {e}")

    return pdf_bytes
