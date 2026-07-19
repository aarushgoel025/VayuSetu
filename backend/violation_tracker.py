from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from db import supabase
from auth import get_current_user


def log_notice_issued(source_id: str, contribution_pct: float, people_exposed: int) -> None:
    """
    Logs a newly generated legal notice into the notices_log table.
    """
    try:
        if supabase:
            row = {
                "source_id": source_id,
                "contribution_pct": contribution_pct,
                "people_exposed": people_exposed,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            supabase.table("notices_log").insert(row).execute()
    except Exception as e:
        print(f"Error logging notice for source {source_id}: {e}")
        return None

def get_violation_history(source_id: str) -> dict:
    """
    Retrieves the complete violation history for a single source.
    """
    try:
        source_name = "Unknown"
        notices = []
        
        if supabase:
            # 1. Fetch source name
            src_resp = supabase.table("sources").select("name").eq("id", source_id).execute()
            if src_resp.data and len(src_resp.data) > 0:
                source_name = src_resp.data[0].get("name", "Unknown")
                
            # 2. Fetch notices
            notices_resp = supabase.table("notices_log") \
                .select("generated_at, contribution_pct, people_exposed") \
                .eq("source_id", source_id) \
                .order("generated_at", desc=True) \
                .execute()
                
            if notices_resp.data:
                notices = notices_resp.data
                
        total_notices = len(notices)
        repeat_offender = total_notices >= 2
        
        return {
            "source_id": source_id,
            "source_name": source_name,
            "total_notices": total_notices,
            "notices": notices,
            "repeat_offender": repeat_offender
        }
        
    except Exception as e:
        print(f"Error fetching violation history for {source_id}: {e}")
        return {
            "source_id": source_id,
            "source_name": "Unknown",
            "total_notices": 0,
            "notices": [],
            "repeat_offender": False
        }

def get_repeat_offenders() -> dict:
    """
    Aggregates notices_log data to find sources with 2 or more violations.
    """
    try:
        offenders_list = []
        
        if supabase:
            # Fetch all notices to aggregate in memory
            # (Supabase doesn't natively support GROUP BY without creating a DB view or RPC)
            notices_resp = supabase.table("notices_log").select("source_id, generated_at").execute()
            
            if notices_resp.data:
                # Aggregate counts and track the latest notice timestamp
                counts = {}
                last_notice = {}
                
                for n in notices_resp.data:
                    sid = n["source_id"]
                    counts[sid] = counts.get(sid, 0) + 1
                    
                    n_time = n["generated_at"]
                    if sid not in last_notice or n_time > last_notice[sid]:
                        last_notice[sid] = n_time
                        
                # Identify offenders with >= 2 notices
                offender_ids = [sid for sid, count in counts.items() if count >= 2]
                
                if offender_ids:
                    # Fetch names for these specific sources
                    sources_resp = supabase.table("sources").select("id, name").in_("id", offender_ids).execute()
                    name_map = {s["id"]: s["name"] for s in sources_resp.data} if sources_resp.data else {}
                    
                    # Build the final list
                    for sid in offender_ids:
                        offenders_list.append({
                            "source_id": sid,
                            "source_name": name_map.get(sid, "Unknown"),
                            "notice_count": counts[sid],
                            "last_notice_at": last_notice[sid]
                        })
                        
                    # Sort descending by notice_count
                    offenders_list.sort(key=lambda x: x["notice_count"], reverse=True)
                    
        return {"offenders": offenders_list}
        
    except Exception as e:
        print(f"Error fetching repeat offenders: {e}")
        return {"offenders": []}

def add_violation_tracker_routes(app: FastAPI):
    """
    Registers the violation tracker endpoints to the FastAPI application.
    """
    @app.get("/api/violation-history")
    def api_get_violation_history(source_id: str, user: dict = Depends(get_current_user)):
        return get_violation_history(source_id)
        
    @app.get("/api/repeat-offenders")
    def api_get_repeat_offenders(user: dict = Depends(get_current_user)):
        return get_repeat_offenders()
