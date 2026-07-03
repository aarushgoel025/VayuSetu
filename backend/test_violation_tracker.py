import pytest
from unittest.mock import patch, MagicMock
import datetime
from violation_tracker import (
    log_notice_issued,
    get_violation_history,
    get_repeat_offenders,
    ensure_notices_log_table_exists
)

# -----------------------------------------------------------------------------
# Mock Data
# -----------------------------------------------------------------------------
MOCK_SOURCES = [
    {"id": "s1", "name": "Sector 18 Construction"},
    {"id": "s2", "name": "Badarpur Power Plant"},
    {"id": "s3", "name": "Okhla Industrial Area"}
]

# -----------------------------------------------------------------------------
# Tests for log_notice_issued
# -----------------------------------------------------------------------------

@patch("violation_tracker.insert_row")
def test_log_notice_issued_success(mock_insert_row):
    """
    Validates that a notice is logged successfully and standard fields
    are inserted into the database.
    """
    log_notice_issued(
        source_id="s1",
        contribution_pct=35.5,
        people_exposed=5000
    )
    
    # Assert insert_row helper was called
    mock_insert_row.assert_called_once()
    args, kwargs = mock_insert_row.call_args
    table_name = args[0]
    data = args[1]
    
    assert table_name == "notices_log"
    assert data["source_id"] == "s1"
    assert data["contribution_pct"] == 35.5
    assert data["people_exposed"] == 5000
    assert "generated_at" in data


@patch("violation_tracker.insert_row")
def test_log_notice_issued_failure(mock_insert_row):
    """
    Validates that database exceptions during insertion are caught
    gracefully without crashing the application.
    """
    mock_insert_row.side_effect = Exception("Supabase insert write timeout")
    
    # This must run without throwing an exception
    log_notice_issued(
        source_id="s1",
        contribution_pct=25.0,
        people_exposed=200
    )
    
    mock_insert_row.assert_called_once()


# -----------------------------------------------------------------------------
# Tests for get_violation_history
# -----------------------------------------------------------------------------

@patch("violation_tracker.supabase", None) # Force fallback to get_table
@patch("violation_tracker.get_table")
def test_get_violation_history_single_notice(mock_get_table):
    """
    Validates violation history retrieval for a source with a single notice.
    Asserts repeat_offender = False.
    """
    def side_effect(table_name):
        if table_name == "sources":
            return MOCK_SOURCES
        elif table_name == "notices_log":
            return [
                {
                    "source_id": "s1",
                    "generated_at": "2026-07-01T12:00:00+00:00",
                    "contribution_pct": 20.0,
                    "people_exposed": 1000
                }
            ]
        return []
    
    mock_get_table.side_effect = side_effect
    
    history = get_violation_history("s1")
    
    assert history["source_id"] == "s1"
    assert history["source_name"] == "Sector 18 Construction"
    assert history["total_notices"] == 1
    assert history["repeat_offender"] is False
    assert len(history["notices"]) == 1
    assert history["notices"][0]["contribution_pct"] == 20.0


@patch("violation_tracker.supabase", None)
@patch("violation_tracker.get_table")
def test_get_violation_history_repeat_offender(mock_get_table):
    """
    Validates violation history for a source with multiple notices.
    Asserts repeat_offender = True and order is newest first.
    """
    def side_effect(table_name):
        if table_name == "sources":
            return MOCK_SOURCES
        elif table_name == "notices_log":
            # 2 notices: s1 (older), s1 (newer)
            return [
                {
                    "source_id": "s1",
                    "generated_at": "2026-07-01T12:00:00+00:00",
                    "contribution_pct": 20.0,
                    "people_exposed": 1000
                },
                {
                    "source_id": "s1",
                    "generated_at": "2026-07-02T12:00:00+00:00",
                    "contribution_pct": 45.0,
                    "people_exposed": 2500
                }
            ]
        return []
    
    mock_get_table.side_effect = side_effect
    
    history = get_violation_history("s1")
    
    assert history["total_notices"] == 2
    assert history["repeat_offender"] is True
    
    # Assert newest notice is first
    assert history["notices"][0]["generated_at"] == "2026-07-02T12:00:00+00:00"
    assert history["notices"][0]["contribution_pct"] == 45.0
    assert history["notices"][1]["generated_at"] == "2026-07-01T12:00:00+00:00"


@patch("violation_tracker.supabase", None)
@patch("violation_tracker.get_table")
def test_get_violation_history_invalid_source(mock_get_table):
    """
    Validates that querying a non-existent source returns an empty structure
    and falls back to "Unknown Source".
    """
    mock_get_table.return_value = []
    
    history = get_violation_history("unknown_id")
    
    assert history["source_id"] == "unknown_id"
    assert history["source_name"] == "Unknown Source"
    assert history["total_notices"] == 0
    assert history["notices"] == []
    assert history["repeat_offender"] is False


@patch("violation_tracker.supabase", None)
@patch("violation_tracker.get_table")
def test_get_violation_history_db_failure(mock_get_table):
    """
    Validates that database query failure is intercepted and returns a safe fallback.
    """
    mock_get_table.side_effect = Exception("Supabase server disconnected")
    
    history = get_violation_history("s1")
    
    assert history["source_id"] == "s1"
    assert history["source_name"] == "Unknown Source"
    assert history["total_notices"] == 0
    assert history["notices"] == []
    assert history["repeat_offender"] is False


# -----------------------------------------------------------------------------
# Tests for get_repeat_offenders
# -----------------------------------------------------------------------------

@patch("violation_tracker.get_table")
def test_get_repeat_offenders_sorting_and_leaderboard(mock_get_table):
    """
    Validates that:
    - Only sources with notice_count >= 2 are included.
    - Sorting is count descending.
    - Ties broken by last_notice_at descending.
    
    Mock notices configurations:
      - s1: 2 notices, latest = 2026-07-02
      - s2: 3 notices, latest = 2026-07-01
      - s3: 2 notices, latest = 2026-07-03
      - s4 (non-mock source): 1 notice -> must be excluded.
      
    Sorted Ranking Order Expected:
      1. s2 (count 3)
      2. s3 (count 2, latest 2026-07-03)
      3. s1 (count 2, latest 2026-07-02)
    """
    def side_effect(table_name):
        if table_name == "sources":
            return MOCK_SOURCES
        elif table_name == "notices_log":
            return [
                {"source_id": "s1", "generated_at": "2026-07-01T12:00:00"},
                {"source_id": "s1", "generated_at": "2026-07-02T12:00:00"},
                
                {"source_id": "s2", "generated_at": "2026-07-01T08:00:00"},
                {"source_id": "s2", "generated_at": "2026-07-01T10:00:00"},
                {"source_id": "s2", "generated_at": "2026-07-01T12:00:00"},
                
                {"source_id": "s3", "generated_at": "2026-07-01T12:00:00"},
                {"source_id": "s3", "generated_at": "2026-07-03T12:00:00"},
                
                {"source_id": "s4", "generated_at": "2026-07-01T12:00:00"}, # Excluded
            ]
        return []
        
    mock_get_table.side_effect = side_effect
    
    result = get_repeat_offenders()
    offenders = result.get("offenders", [])
    
    assert len(offenders) == 3
    
    # Check Rank 1: s2 (3 notices)
    assert offenders[0]["source_id"] == "s2"
    assert offenders[0]["notice_count"] == 3
    
    # Check Rank 2: s3 (2 notices, newer tie-breaker: 2026-07-03)
    assert offenders[1]["source_id"] == "s3"
    assert offenders[1]["notice_count"] == 2
    
    # Check Rank 3: s1 (2 notices, older tie-breaker: 2026-07-02)
    assert offenders[2]["source_id"] == "s1"
    assert offenders[2]["notice_count"] == 2


@patch("violation_tracker.get_table")
def test_get_repeat_offenders_empty_db(mock_get_table):
    """
    Validates that get_repeat_offenders returns an empty list if there are no repeat offenders.
    """
    def side_effect(table_name):
        if table_name == "sources":
            return MOCK_SOURCES
        elif table_name == "notices_log":
            return [
                {"source_id": "s1", "generated_at": "2026-07-01T12:00:00"}, # count 1
                {"source_id": "s2", "generated_at": "2026-07-01T12:00:00"}, # count 1
            ]
        return []
        
    mock_get_table.side_effect = side_effect
    
    result = get_repeat_offenders()
    assert result == {"offenders": []}


@patch("violation_tracker.get_table")
def test_get_repeat_offenders_db_failure(mock_get_table):
    """
    Validates that database failures do not crash the repeat offenders call.
    """
    mock_get_table.side_effect = Exception("Supabase connection timed out")
    
    result = get_repeat_offenders()
    assert result == {"offenders": []}


# -----------------------------------------------------------------------------
# Tests for table existence DDL helper
# -----------------------------------------------------------------------------

@patch("violation_tracker.supabase")
def test_ensure_table_exists_success(mock_supabase):
    """
    Tests that ensure_notices_log_table_exists returns True if the query succeeds.
    """
    # Mocking select query to return success
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock()
    
    assert ensure_notices_log_table_exists() is True


@patch("violation_tracker.supabase")
def test_ensure_table_exists_failure(mock_supabase):
    """
    Tests that ensure_notices_log_table_exists returns False if the query fails (relation does not exist).
    """
    # Mocking select query to throw exception
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("relation 'notices_log' does not exist")
    
    assert ensure_notices_log_table_exists() is False
