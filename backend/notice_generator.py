import io
import datetime
from google import genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from config import GEMINI_API_KEY
from db import get_table

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

def generate_legal_notice_text(source: dict, fingerprint_pct: float, harm_data: dict, readings: list[dict]) -> str:
    """Gemini call, temperature=0.3. Drafts formal notice under Section 19, Air Act 1981."""
    prompt = f"""
    Draft a formal legal notice under Section 19 of the Air (Prevention and Control of Pollution) Act 1981.
    Address it to: {source.get('name', 'Unknown')}, {source.get('address', 'Unknown')}.
    
    Include these details:
    - Contribution to local pollution: {fingerprint_pct}%
    - Harm data (affected population): {harm_data}
    - Recent sensor readings showing elevated levels: {readings[:3]}
    
    Structure the notice with:
    1. Subject
    2. Observations
    3. Evidence
    4. Directive
    5. Compliance timeline
    
    Tone: Formal, plain text, legal but readable.
    """
    
    if not client:
        return f"Legal Notice Placeholder\nSubject: Pollution Notice\nTo: {source.get('name')}\nObservation: You contributed {fingerprint_pct}% to local pollution."
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(temperature=0.3)
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating notice text: {e}"

def generate_notice_pdf(source_id: str) -> bytes:
    """Fetches source + readings + fingerprint + harm score. Calls generate_legal_notice_text()."""
    # 1. Fetch Source
    sources = get_table("sources")
    source = next((s for s in sources if s["id"] == source_id), None)
    if not source:
        raise ValueError("Source not found")
        
    # 2. Fetch Readings (Mocking latest a few)
    readings = get_table("readings")
    recent_readings = readings[-5:] if readings else []
    
    # 3. Harm Score (from Lakshita's module)
    harm_data = {"score": 85, "people_exposed": 12000, "zones_affected": ["School A", "Hospital B"]}
    try:
        from harm_score import get_harm_score
        harm_data = get_harm_score(source_id)
    except ImportError:
        pass # fallback to mock data
        
    # Mock contribution for this example
    contribution_pct = 45.2
        
    notice_text = generate_legal_notice_text(source, contribution_pct, harm_data, recent_readings)
    
    # PDF Generation
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, height - 1 * inch, "VayuSetu — Pollution Control Intelligence Report")
    
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, height - 1.5 * inch, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    p.drawString(1 * inch, height - 1.8 * inch, f"To: {source.get('name')}")
    p.drawString(1 * inch, height - 2.0 * inch, f"Address: {source.get('address')}")
    
    # Body
    textobject = p.beginText(1 * inch, height - 2.5 * inch)
    textobject.setFont("Helvetica", 10)
    
    for line in notice_text.split('\n'):
        # simple text wrapping
        max_chars = 90
        while len(line) > max_chars:
            split_idx = line.rfind(' ', 0, max_chars)
            if split_idx == -1:
                split_idx = max_chars
            textobject.textLine(line[:split_idx])
            line = line[split_idx:].strip()
        textobject.textLine(line)

    p.drawText(textobject)
    
    # Footer
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(1 * inch, 0.5 * inch, f"Generated automatically by VayuSetu at {datetime.datetime.now().isoformat()}")
    
    p.showPage()
    p.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    # Log notice issued (Lakshita's module)
    try:
        from violation_tracker import log_notice_issued
        log_notice_issued(
            source_id=source_id, 
            generated_at=datetime.datetime.now().isoformat(), 
            contribution_pct=contribution_pct, 
            people_exposed=harm_data.get("people_exposed", 0)
        )
    except ImportError:
        print("Violation tracker not found, skipping logging.")
    except Exception as e:
        print(f"Could not log notice: {e}")
        
    return pdf_bytes
