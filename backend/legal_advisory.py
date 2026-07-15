from typing import Optional
from fastapi import FastAPI
from db import supabase


def get_legal_advisory(lat: float, lng: float, source_id: str = None) -> dict:
    """
    Provides citizens with information on their rights, how to file a complaint,
    and whether the targeted source has already been issued a notice.

    NOTE: Gemini call was removed from this function. The citizen_rights_text and
    complaint_guidance_text are static legal boilerplate — they never varied
    meaningfully between Gemini calls. Using high-quality hardcoded strings saves
    one API call per station panel open with identical output quality.
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
            notice_status = "pending"

        # 2. Determine relevant authority based on source type
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

    citizen_rights_text = (
        "Under the Air (Prevention and Control of Pollution) Act 1981 and the Environment "
        "Protection Act 1986, every citizen has a constitutionally protected right to a clean "
        "and healthy environment. You are legally empowered to demand accountability from any "
        "industrial, commercial, or governmental entity whose emissions violate prescribed "
        "ambient air quality standards and adversely affect your health or locality."
    )
    complaint_guidance_text = (
        "File a formal complaint via the CPCB SAMEER app (available on Android & iOS) or directly "
        "through your State Pollution Control Board's online grievance portal. Keep records of "
        "sensor readings, dates, and health impacts as supporting evidence. If the issue remains "
        "unresolved after 60 days, you may petition the National Green Tribunal (NGT) under "
        "Section 14 of the NGT Act 2010 — no court fee is required for environmental cases."
    )

    return {
        "citizen_rights_text": citizen_rights_text,
        "complaint_guidance_text": complaint_guidance_text,
        "notice_status": notice_status,
        "relevant_authority": relevant_authority,
        "disclaimer": "This is general informational guidance only and does not constitute legal advice.",
    }


def add_legal_advisory_routes(app: FastAPI):
    @app.get("/api/legal-advisory")
    def api_get_legal_advisory(lat: float, lng: float, source_id: Optional[str] = None):
        return get_legal_advisory(lat, lng, source_id)
