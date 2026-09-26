import time
import pytest
from backend.app.services.session_manager import SessionManager, AssistantSession
from backend.app.schemas.assistant import PropertySlots

def test_session_creation_and_bounds():
    mgr = SessionManager(ttl_minutes=30)
    session = mgr.get_or_create_session()
    assert session.session_id is not None
    assert len(session.messages) == 0

    # Test bounded message history (max 10)
    for i in range(15):
        session.add_message("user", f"Message {i}")
    
    assert len(session.messages) == 10
    assert session.messages[-1]["content"] == "Message 14"
    assert session.messages[0]["content"] == "Message 5"

def test_slot_accumulation():
    session = AssistantSession(session_id="test-session-1")
    
    # Turn 1: User gives area and city
    session.merge_slots(PropertySlots(area_sqft=1200.0, city="mumbai"))
    assert session.accumulated_slots.area_sqft == 1200.0
    assert session.accumulated_slots.city == "mumbai"
    assert session.accumulated_slots.bhk is None

    # Turn 2: User provides BHK and RERA
    session.merge_slots(PropertySlots(bhk=2, rera=1))
    assert session.accumulated_slots.area_sqft == 1200.0
    assert session.accumulated_slots.city == "mumbai"
    assert session.accumulated_slots.bhk == 2
    assert session.accumulated_slots.rera == 1

def test_session_reset():
    session = AssistantSession(session_id="test-reset")
    session.add_message("user", "Hello")
    session.merge_slots(PropertySlots(area_sqft=1500.0, city="bangalore", bhk=3))
    
    assert len(session.messages) == 1
    assert session.accumulated_slots.area_sqft == 1500.0

    session.reset()
    assert len(session.messages) == 0
    assert session.accumulated_slots.area_sqft is None
    assert session.accumulated_slots.city is None

def test_session_ttl_expiration():
    # Manager with 0.001 minutes (0.06 seconds) TTL
    mgr = SessionManager(ttl_minutes=0.001)
    s1 = mgr.get_or_create_session("expire-me")
    sid = s1.session_id

    assert mgr.get_active_sessions_count() == 1
    time.sleep(0.1) # Wait for TTL to pass

    # Retrieving expired session should create a fresh session
    s2 = mgr.get_or_create_session(sid)
    assert len(s2.messages) == 0
