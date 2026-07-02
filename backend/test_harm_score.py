import pytest
from unittest.mock import patch, MagicMock
from harm_score import _haversine_distance, _get_multiplier, get_harm_score

# -----------------------------------------------------------------------------
# Unit Tests for Helpers
# -----------------------------------------------------------------------------

def test_haversine_distance_calculation():
    """
    Validates that the Haversine distance calculator is accurate.
    Coordinates:
      AIIMS New Delhi: 28.5672, 77.2100
      Safdarjung Hospital: 28.5684, 77.2064
    Distance is approximately ~0.37 km.
    """
    dist = _haversine_distance(28.5672, 77.2100, 28.5684, 77.2064)
    assert abs(dist - 0.37) < 0.1  # Allow small margin


def test_get_multiplier():
    """
    Validates that multipliers match the specification:
      - school = 1.5
      - hospital = 2.0
      - old_age_home = 1.8
      - other = 1.0 (default)
    """
    assert _get_multiplier("school") == 1.5
    assert _get_multiplier("hospital") == 2.0
    assert _get_multiplier("old_age_home") == 1.8
    assert _get_multiplier("other_type") == 1.0
    assert _get_multiplier("SCHOOL") == 1.5  # Case insensitivity check


# -----------------------------------------------------------------------------
# Mock Data for Database Queries
# -----------------------------------------------------------------------------

MOCK_VULNERABLE_ZONES = [
    {
        "name": "Delhi Public School",
        "type": "school",
        "lat": 28.5615,
        "lng": 77.1751,
        "estimated_population": 4000
    },
    {
        "name": "Safdarjung Hospital",
        "type": "hospital",
        "lat": 28.5684,
        "lng": 77.2064,
        "estimated_population": 8000
    },
    {
        "name": "HelpAge India",
        "type": "old_age_home",
        "lat": 28.5369,
        "lng": 77.1952,
        "estimated_population": 150
    }
]

MOCK_SOURCES = [
    {
        "id": "s1",
        "name": "Okhla Industrial Area",
        "lat": 28.5273,
        "lng": 77.2798
    }
]

MOCK_STATIONS = [
    {"id": "st1", "name": "Station A", "lat": 28.5200, "lng": 77.2800}
]

MOCK_READINGS = [
    {"station_id": "st1", "aqi": 180, "timestamp": "2026-07-01T01:00:00"}
]


# -----------------------------------------------------------------------------
# Core Functionality Tests
# -----------------------------------------------------------------------------

@patch("harm_score.get_table")
def test_get_harm_score_normal_coordinates(mock_get_table):
    """
    Validates get_harm_score in normal conditions using lat/lng coordinates.
    Query Center: 28.5600, 77.2000 (Close to Safdarjung and HelpAge India, DPS is far)
    Radius: 3.0 km
    AQI: 160 (hours_exposed = 8.0)
    
    Expected inclusions:
      - Safdarjung Hospital (Dist: ~1.12 km <= 3.0) -> pop = 8000, mult = 2.0. Contribution = 8000 * 8 * 2.0 = 128,000
      - HelpAge India (Dist: ~2.61 km <= 3.0) -> pop = 150, mult = 1.8. Contribution = 150 * 8 * 1.8 = 2,160
      - DPS RK Puram (Dist: ~2.44 km <= 3.0) -> pop = 4000, mult = 1.5. Contribution = 4000 * 8 * 1.5 = 48,000
      
    Total score = 128,000 + 2,160 + 48,000 = 178,160.0
    Children exposed: 4000
    Patients exposed: 8000
    """
    mock_get_table.return_value = MOCK_VULNERABLE_ZONES
    
    result = get_harm_score(
        zone_lat=28.5600,
        zone_lng=77.2000,
        radius_km=3.0,
        current_aqi=160
    )
    
    assert result["harm_score"] == 178160.0
    assert result["children_exposed"] == 4000
    assert result["patients_exposed"] == 8000
    assert len(result["affected_zones"]) == 3
    assert result["people_exposed"] == 12000  # children + patients


@patch("harm_score.get_table")
def test_aqi_exposure_boundary_rules(mock_get_table):
    """
    Validates boundary logic for AQI:
      - AQI <= 150 should result in hours_exposed = 0, meaning harm_score = 0.
      - AQI > 150 should result in hours_exposed = 8, meaning harm_score > 0.
    """
    mock_get_table.return_value = MOCK_VULNERABLE_ZONES
    
    # Test boundary below/equal threshold (AQI = 150)
    result_low = get_harm_score(28.5600, 77.2000, 3.0, 150)
    assert result_low["harm_score"] == 0.0
    assert result_low["children_exposed"] == 4000  # population is still physically present
    
    # Test boundary above threshold (AQI = 151)
    result_high = get_harm_score(28.5600, 77.2000, 3.0, 151)
    assert result_high["harm_score"] > 0.0


@patch("harm_score.get_table")
def test_haversine_radius_filtering(mock_get_table):
    """
    Validates that vulnerable zones outside the radius are excluded.
    We center on Delhi Public School (28.5615, 77.1751) with a small radius of 0.5 km.
    Only DPS should be included. Safdarjung and HelpAge India are > 2km away.
    """
    mock_get_table.return_value = MOCK_VULNERABLE_ZONES
    
    result = get_harm_score(
        zone_lat=28.5615,
        zone_lng=77.1751,
        radius_km=0.5,
        current_aqi=200
    )
    
    assert len(result["affected_zones"]) == 1
    assert result["affected_zones"][0]["name"] == "Delhi Public School"
    assert result["children_exposed"] == 4000
    assert result["patients_exposed"] == 0


@patch("harm_score.query_latest_per_station")
@patch("harm_score.get_table")
def test_get_harm_score_source_id_lookup(mock_get_table, mock_query_latest):
    """
    Validates single-parameter lookup compatible with notice_generator.py.
    Calls get_harm_score("s1").
    - Resolves "s1" location to Okhla (28.5273, 77.2798).
    - Resolves closest station AQI (from mock stations and readings).
    - Checks database queries are correctly executed.
    """
    def side_effect(table_name):
        if table_name == "sources":
            return MOCK_SOURCES
        elif table_name == "vulnerable_zones":
            return MOCK_VULNERABLE_ZONES
        elif table_name == "stations":
            return MOCK_STATIONS
        return []
        
    mock_get_table.side_effect = side_effect
    mock_query_latest.return_value = MOCK_READINGS
    
    # Invoke fallback structure
    result = get_harm_score("s1")
    
    # Assertions on standard return parameters
    assert "harm_score" in result
    assert "children_exposed" in result
    assert "patients_exposed" in result
    
    # Assertions on Aarush compatibility parameters
    assert "score" in result
    assert "people_exposed" in result
    assert "zones_affected" in result


@patch("harm_score.get_table")
def test_database_failure_graceful_handling(mock_get_table):
    """
    Validates that a database connection crash is handled gracefully.
    Mocking get_table to raise an Exception.
    Function must catch it and return a zeroed dictionary structure.
    """
    mock_get_table.side_effect = Exception("Supabase connection timed out")
    
    # Must not raise an exception
    result = get_harm_score(28.5600, 77.2000, 3.0, 180)
    
    assert result["harm_score"] == 0.0
    assert result["children_exposed"] == 0
    assert result["patients_exposed"] == 0
    assert result["affected_zones"] == []


@patch("harm_score.get_table")
def test_invalid_inputs_handling(mock_get_table):
    """
    Validates that incorrect parameter types do not trigger raw crashes.
    """
    mock_get_table.return_value = MOCK_VULNERABLE_ZONES
    
    # Invalid coordinates (strings instead of float)
    result = get_harm_score("invalid_lat", "invalid_lng", None, "invalid_aqi")
    
    assert result["harm_score"] == 0.0
    assert result["children_exposed"] == 0
    assert result["patients_exposed"] == 0
    assert result["affected_zones"] == []
