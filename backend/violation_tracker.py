import datetime
from typing import Dict, List, Any, Optional
from db import supabase, get_table, insert_row

def ensure_notices_log_table_exists() -> bool:
    """
    Checks if the 'notices_log' table exists in Supabase.
    If it doesn't exist, logs a warning and provides the SQL DDL script 
    to be executed in the Supabase SQL Editor.
    """
    sql_script = """
    -- SQL Script to create the notices_log table in Supabase:
    CREATE TABLE IF NOT EXISTS notices_log (
        id SERIAL PRIMARY KEY,
        source_id TEXT NOT NULL,
        generated_at TIMESTAMPTZ DEFAULT NOW(),
        contribution_pct FLOAT NOT NULL,
        people_exposed INT NOT NULL
    );
    """
    if not supabase:
        print("Supabase client is offline. notices_log table check skipped.")
        return False
    try:
        # Check if notices_log table exists by running a simple select query
        supabase.table("notices_log").select("id").limit(1).execute()
        return True
    except Exception:
        print("\n" + "="*80)
        print("WARNING: 'notices_log' table does not exist in Supabase database.")
        print("Please execute the following SQL in your Supabase SQL Editor:")
        print(sql_script)
        print("="*80 + "\n")
        return False


def log_notice_issued(
    source_id: str,
    contribution_pct: float,
    people_exposed: int,
    generated_at: Optional[str] = None
) -> None:
    """
    Inserts a row into the notices_log table in Supabase.
    
    Includes the optional parameter `generated_at` to remain compatible 
    with Aarush's notice_generator.py call signature.
    """
    try:
        # Determine timestamp (use UTC now if not provided)
        if not generated_at:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        else:
            timestamp = generated_at

        data = {
            "source_id": source_id,
            "generated_at": timestamp,
            "contribution_pct": float(contribution_pct),
            "people_exposed": int(people_exposed)
        }

        # Reuse db.py insert_row helper
        insert_row("notices_log", data)
    except Exception as e:
        print(f"Error logging notice issued: {e}")


def get_violation_history(source_id: str) -> dict:
    """
    Queries all notices_log rows for the given source, ordered by generated_at desc.
    repeat_offender = True if total_notices >= 2.
    
    Return:
        {
            "source_id": str,
            "source_name": str,
            "total_notices": int,
            "notices": [{"generated_at": str, "contribution_pct": float, "people_exposed": int}],
            "repeat_offender": bool
        }
    """
    default_response = {
        "source_id": source_id,
        "source_name": "Unknown Source",
        "total_notices": 0,
        "notices": [],
        "repeat_offender": False
    }

    try:
        # 1. Fetch Source Name
        sources = get_table("sources") or []
        source = next((s for s in sources if s.get("id") == source_id), None)
        source_name = source.get("name", "Unknown Source") if source else "Unknown Source"
        default_response["source_name"] = source_name

        # 2. Query notices_log
        notices_data = []
        if supabase:
            response = supabase.table("notices_log").select("*").eq("source_id", source_id).execute()
            notices_data = response.data or []
        else:
            all_notices = get_table("notices_log") or []
            notices_data = [n for n in all_notices if n.get("source_id") == source_id]

        # 3. Sort chronologically descending (newest first)
        def parse_timestamp(n_dict):
            ts = n_dict.get("generated_at", "")
            try:
                return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                return datetime.datetime.min

        notices_sorted = sorted(notices_data, key=parse_timestamp, reverse=True)

        # 4. Format outputs
        formatted_notices = []
        for n in notices_sorted:
            formatted_notices.append({
                "generated_at": n.get("generated_at", ""),
                "contribution_pct": float(n.get("contribution_pct", 0.0)),
                "people_exposed": int(n.get("people_exposed", 0))
            })

        total_notices = len(formatted_notices)

        return {
            "source_id": source_id,
            "source_name": source_name,
            "total_notices": total_notices,
            "notices": formatted_notices,
            "repeat_offender": total_notices >= 2
        }

    except Exception as e:
        print(f"Error fetching violation history: {e}")
        return default_response


def get_repeat_offenders() -> dict:
    """
    Groups notices_log by source_id, counts notices per source.
    Returns only sources with notice_count >= 2, sorted descending by notice_count.
    Ties broken by last_notice_at descending.
    
    Return:
        {
            "offenders": [{"source_id": str, "source_name": str, "notice_count": int, "last_notice_at": str}]
        }
    """
    default_response = {"offenders": []}

    try:
        # 1. Fetch all notices and sources
        notices_data = get_table("notices_log") or []
        sources = get_table("sources") or []
        
        sources_map = {s.get("id"): s.get("name", "Unknown Source") for s in sources if s.get("id")}

        # 2. Group notices by source_id
        # Find count and latest timestamp for each source
        group_data: Dict[str, List[datetime.datetime]] = {}
        
        def parse_timestamp(ts):
            try:
                return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                return datetime.datetime.min

        for n in notices_data:
            s_id = n.get("source_id")
            g_at = n.get("generated_at", "")
            if s_id:
                if s_id not in group_data:
                    group_data[s_id] = []
                group_data[s_id].append(parse_timestamp(g_at))

        # 3. Filter repeat offenders (count >= 2)
        offenders_list = []
        for s_id, timestamps in group_data.items():
            count = len(timestamps)
            if count >= 2:
                latest_dt = max(timestamps) if timestamps else datetime.datetime.min
                offenders_list.append({
                    "source_id": s_id,
                    "source_name": sources_map.get(s_id, "Unknown Source"),
                    "notice_count": count,
                    "last_notice_at": latest_dt.isoformat() if latest_dt != datetime.datetime.min else ""
                })

        # 4. Sort: Primary = notice_count desc, Secondary = last_notice_at desc
        offenders_list.sort(key=lambda x: (x["notice_count"], x["last_notice_at"]), reverse=True)

        return {"offenders": offenders_list}

    except Exception as e:
        print(f"Error fetching repeat offenders: {e}")
        return default_response
