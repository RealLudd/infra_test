"""
Unit tests for CashWeb application
"""
import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test the main index page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'CashWeb'

def test_get_summary(client):
    """Test getting cash flow summary"""
    response = client.get('/api/summary')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_income' in data
    assert 'total_expenses' in data
    assert 'net_cash' in data
    assert data['total_income'] > 0

def test_get_transactions(client):
    """Test getting all transactions"""
    response = client.get('/api/transactions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_add_transaction(client):
    """Test adding a new transaction"""
    new_transaction = {
        'date': '2025-11-06',
        'description': 'Test Transaction',
        'amount': 500,
        'type': 'income'
    }
    response = client.post('/api/transactions',
                          data=json.dumps(new_transaction),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['description'] == 'Test Transaction'
    assert data['amount'] == 500

