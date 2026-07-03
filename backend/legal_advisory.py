import json
import math
from typing import Optional
from google import genai
from config import GEMINI_API_KEY
from db import get_table
from violation_tracker import get_violation_history

# Initialize Gemini Client if key is available
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Computes the great-circle distance between two points in kilometers.
    """
    R = 6371.0  # Earth's radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(d_lat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _get_authority_for_type(source_type: str) -> str:
    """
    Maps source type to the responsible regulatory authority.
    """
    authority_map = {
        "thermal_plant": "Central Pollution Control Board (CPCB)",
        "industrial": "State Pollution Control Board (SPCB)",
        "construction": "Municipal Corporation / Local Authority",
        "traffic_corridor": "Traffic Police and Municipal Authority"
    }
    return authority_map.get(source_type.lower(), "Local Pollution Control Authority")


def get_legal_advisory(
    lat: float,
    lng: float,
    source_id: Optional[str] = None
) -> dict:
    """
    Provides a citizen-facing legal guidance service.
    
    Return:
        {
            "citizen_rights_text": str,
            "complaint_guidance_text": str,
            "notice_status": str,
            "relevant_authority": str
        }
    """
    # Standard Fallbacks
    rights_fallback = (
        "Under the Air (Prevention and Control of Pollution) Act, 1981, citizens have a general right to "
        "clean air and a healthy environment. Please note that this information is provided for general "
        "guidance and educational purposes only, and does not constitute formal legal advice."
    )
    guidance_fallback = (
        "Citizens can report pollution violations by filing complaints through the CPCB SAMEER mobile app, "
        "the local State Pollution Control Board, or municipal authorities. We encourage gathering photographic "
        "or environmental evidence to support your report, though specific enforcement outcomes cannot be guaranteed."
    )

    result = {
        "citizen_rights_text": rights_fallback,
        "complaint_guidance_text": guidance_fallback,
        "notice_status": "Unknown",
        "relevant_authority": "Local Pollution Control Authority"
    }

    try:
        # 1. Determine Notice Status
        if source_id:
            try:
                history = get_violation_history(source_id)
                if history and history.get("total_notices", 0) > 0:
                    result["notice_status"] = "Official notices have previously been issued against this source."
                else:
                    result["notice_status"] = "No previous notices have been recorded."
            except Exception as e:
                result["notice_status"] = "No previous notices have been recorded."
        else:
            result["notice_status"] = "Unknown"

        # 2. Determine Relevant Authority
        source_type = "Unknown"
        sources = get_table("sources") or []
        
        if source_id:
            source = next((s for s in sources if s.get("id") == source_id), None)
            if source:
                source_type = source.get("type", "Unknown")
        else:
            # Look up the closest source within a 5km radius to infer the type
            closest_source = None
            min_dist = float("inf")
            for s in sources:
                s_lat = s.get("lat")
                s_lng = s.get("lng")
                if s_lat is not None and s_lng is not None:
                    dist = _haversine_distance(lat, lng, float(s_lat), float(s_lng))
                    if dist < min_dist:
                        min_dist = dist
                        closest_source = s
            
            if closest_source and min_dist <= 5.0:
                source_type = closest_source.get("type", "Unknown")

        result["relevant_authority"] = _get_authority_for_type(source_type)

        # 3. Fetch Narrative Texts using Gemini 2.5 Flash
        if client:
            prompt = """
            You are a public environmental advisor drafting educational legal materials for citizens in India.
            Draft exactly two short text blocks.
            
            Block 1: Citizen Rights
            - Write exactly 2-3 sentences.
            - Explain the right to clean air under the Air (Prevention and Control of Pollution) Act, 1981.
            - Explicitly state that this is for general guidance and does NOT constitute formal legal advice.
            
            Block 2: Complaint Guidance
            - Write exactly 2-3 sentences.
            - Explain that citizens can report violations through the CPCB SAMEER app, State Pollution Control Board, or local municipal helplines.
            - Encourage collecting evidence, and state that outcomes cannot be guaranteed.
            
            Return the response as a strict JSON object with exactly two keys: "citizen_rights_text" and "complaint_guidance_text".
            Do not include markdown code block fences (like ```json or ```).
            """
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.3,
                        response_mime_type="application/json"
                    )
                )
                
                # Strip markdown code blocks if returned
                response_text = response.text.strip()
                if response_text.startswith("```"):
                    lines = response_text.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    response_text = "\n".join(lines).strip()

                narrative_data = json.loads(response_text)
                
                rights_txt = narrative_data.get("citizen_rights_text")
                guidance_txt = narrative_data.get("complaint_guidance_text")
                
                if rights_txt:
                    result["citizen_rights_text"] = str(rights_txt)
                if guidance_txt:
                    result["complaint_guidance_text"] = str(guidance_txt)

            except Exception as e:
                # Log Gemini failure internally and keep high-quality fallbacks
                pass

    except Exception as e:
        # Outer try-catch ensures no uncaught exceptions are thrown to FastAPI routes
        pass

    return result
