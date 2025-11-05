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

def test_get_overview(client):
    """Test the overview endpoint with different periods"""
    # Test default period (today)
    response = client.get('/api/overview')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_payments' in data
    assert 'automation_percentage' in data
    assert 'trend_chart' in data

    # Test different periods
    for period in ['today', 'week', 'month', 'quarter']:
        response = client.get(f'/api/overview?period={period}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['period'] == period
        assert isinstance(data['trend_chart'], list)

def test_automation_efficiency(client):
    """Test automation efficiency endpoint"""
    response = client.get('/api/automation-efficiency')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'automation_success_rate' in data
    assert 'manual_interventions_saved' in data
    assert 'time_saved_minutes' in data
    assert 'cost_saved_euros' in data
    assert 'rule_breakdown' in data
    assert isinstance(data['rule_breakdown'], dict)

def test_exceptions(client):
    """Test exceptions endpoint"""
    response = client.get('/api/exceptions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'top_problem_customers' in data
    assert 'high_value_unassigned' in data
    assert 'error_breakdown' in data
    assert isinstance(data['top_problem_customers'], list)
    assert isinstance(data['high_value_unassigned'], list)
    assert isinstance(data['error_breakdown'], dict)

def test_month_end_summary(client):
    """Test month-end summary endpoint"""
    response = client.get('/api/month-end-summary')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'current_month' in data
    assert 'previous_month' in data
    assert 'changes' in data
    assert 'top_performing_rules' in data
    assert 'automation_rate' in data['current_month']
    assert isinstance(data['top_performing_rules'], list)

def test_get_transactions(client):
    """Test getting all transactions"""
    response = client.get('/api/transactions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_add_transaction(client):
    """Test adding a new payment"""
    new_payment = {
        'date': '2025-11-06',
        'customer_name': 'Test Customer Inc',
        'customer_id': 'C9999',
        'amount': 5000,
        'status': 'auto_assigned',
        'assignment_method': 'bank_match',
        'processing_time': 1.5,
        'sap_posted': True,
        'remittance_received': True
    }
    response = client.post('/api/transactions',
                          data=json.dumps(new_payment),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['customer_name'] == 'Test Customer Inc'
    assert data['amount'] == 5000
    assert data['status'] == 'auto_assigned'

