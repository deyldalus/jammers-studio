95% of storage used … If you run out, you can't create, edit and upload files. Get 30 GB for ₱10 for 3 months ₱49.
test_app.py DATA.txt
import pytest
from app import app
import json

client = app.test_client()

def get_token():
    response = client.post('/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    data = json.loads(response.data)
    return data['access_token']

def test_home():
    response = client.get('/')
    assert response.status_code == 200

def test_get_bookings():
    # Updated to underscore
    response = client.get('/studio_bookings')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_search_band():
    # Updated to underscore
    response = client.get('/studio_bookings/search?band_name=Echoes')
    assert response.status_code == 200

def test_add_booking():
    token = get_token()
    # Updated to underscore
    response = client.post(
        '/studio_bookings',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'band_name': 'Test Band',
            'genre': 'Rock',
            'band_leader': 'Tester',
            'members_count': 4,
            'room_number': 1,
            'booking_date': '2026-02-01',
            'session_hours': 2
        }
    )
    assert response.status_code == 201

def test_delete_booking():
    token = get_token()
    # Updated to underscore
    response = client.delete(
        '/studio_bookings/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code in [200, 404]