import json
from typing import Optional
from fastapi import FastAPI
from google import genai
from config import GEMINI_API_KEY
from db import supabase

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

def get_legal_advisory(lat: float, lng: float, source_id: str = None) -> dict:
    """
    Provides citizens with information on their rights, how to file a complaint,
    and whether the targeted source has already been issued a notice.
    """
    notice_status = "none"
    relevant_authority = "State Pollution Control Board (SPCB)"
    
    if source_id:
        # 1. Check notices_log for this source
        try:
            if supabase:
                notices_resp = supabase.table("notices_log").select("id").eq("source_id", source_id).execute()
                if notices_resp.data and len(notices_resp.data) > 0:
                    notice_status = "issued"
                else:
                    notice_status = "pending"
        except Exception as e:
            print(f"Error querying notices_log: {e}")
            notice_status = "pending"  # fallback
            
        # 2. Determine relevant authority
        try:
            if supabase:
                sources_resp = supabase.table("sources").select("type").eq("id", source_id).execute()
                if sources_resp.data and len(sources_resp.data) > 0:
                    source_type = sources_resp.data[0].get("type")
                    if source_type == "thermal_plant":
                        relevant_authority = "Central Pollution Control Board (CPCB)"
                    elif source_type == "industrial":
                        relevant_authority = "State Pollution Control Board (SPCB)"
                    elif source_type == "construction":
                        relevant_authority = "Local Municipal Corporation"
                    elif source_type == "traffic_corridor":
                        relevant_authority = "Regional Transport Office (RTO)"
        except Exception as e:
            print(f"Error querying sources: {e}")

    # Fallback strings for Gemini failure
    citizen_rights_text = (
        "Under the Air (Prevention and Control of Pollution) Act 1981 and the Environment Protection Act 1986, "
        "citizens have a fundamental right to a clean environment. You are legally empowered to seek accountability "
        "for hazardous emissions affecting your health and locality."
    )
    complaint_guidance_text = (
        "You can officially register a complaint using the CPCB SAMEER application or through your "
        "State Pollution Control Board's grievance portal. If the issue persists without resolution, "
        "it can be escalated to the National Green Tribunal (NGT) for further intervention."
    )

    # 3. Gemini Call
    if client:
        try:
            prompt = """
            Generate TWO short text blocks explaining citizen rights regarding air pollution.
            Return ONLY a valid JSON object with exactly these two keys:
            "citizen_rights_text": "2-3 sentences on the citizen's right to clean air under Air (Prevention and Control of Pollution) Act 1981 and Environment Protection Act 1986. General, accurate, not legal advice."
            "complaint_guidance_text": "2-3 sentences guiding the citizen to file via CPCB SAMEER app, their State Pollution Control Board portal, or National Green Tribunal if unresolved. General guidance, not a guarantee."
            Do not include any markdown fences or explanation. Just raw JSON.
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            
            raw_json = response.text.strip()
            
            # Strip markdown fences if Gemini hallucinates them despite mime-type
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:]
            if raw_json.startswith("```"):
                raw_json = raw_json[3:]
            if raw_json.endswith("```"):
                raw_json = raw_json[:-3]
                
            parsed_data = json.loads(raw_json.strip())
            
            citizen_rights_text = parsed_data.get("citizen_rights_text", citizen_rights_text)
            complaint_guidance_text = parsed_data.get("complaint_guidance_text", complaint_guidance_text)
            
        except Exception as e:
            print(f"Error generating legal advisory text with Gemini: {e}")

    # 4. Return Dictionary
    return {
        "citizen_rights_text": citizen_rights_text,
        "complaint_guidance_text": complaint_guidance_text,
        "notice_status": notice_status,
        "relevant_authority": relevant_authority,
        "disclaimer": "This is general informational guidance only and does not constitute legal advice."
    }

def add_legal_advisory_routes(app: FastAPI):
    @app.get("/api/legal-advisory")
    def api_get_legal_advisory(lat: float, lng: float, source_id: Optional[str] = None):
        return get_legal_advisory(lat, lng, source_id)
