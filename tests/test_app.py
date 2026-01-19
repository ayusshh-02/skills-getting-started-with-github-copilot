"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create a test client
client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""
    
    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Verify known activities exist
        assert "Basketball" in activities
        assert "Tennis Club" in activities
        assert "Drama Club" in activities
    
    def test_get_activities_structure(self):
        """Test that activities have the expected structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Test the signup endpoint"""
    
    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        email = "test@mergington.edu"
        activity_name = "Basketball"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_already_registered(self):
        """Test that a student can't sign up twice for the same activity"""
        email = "duplicate@mergington.edu"
        activity_name = "Tennis Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        email = "test@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_empty_email(self):
        """Test signing up with empty email"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": ""}
        )
        # The endpoint will accept empty string; API validation is minimal
        assert response.status_code == 200


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirect(self):
        """Test that root redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivityParticipants:
    """Test activity participant management"""
    
    def test_get_updated_participants(self):
        """Test that participants list is updated after signup"""
        email = "new_participant@mergington.edu"
        activity_name = "Drama Club"
        
        # Get initial participants count
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity_name]["participants"]
        count_before = len(participants_before)
        
        # Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get updated participants
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity_name]["participants"]
        count_after = len(participants_after)
        
        assert count_after == count_before + 1
        assert email in participants_after
