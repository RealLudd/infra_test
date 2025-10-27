import pytest
from app import add, app as flask_app


# Original tests for the add function
def test_add_positive_numbers():
    """Test adding two positive numbers."""
    assert add(2, 3) == 5
    assert add(10, 20) == 30


def test_add_negative_numbers():
    """Test adding negative numbers."""
    assert add(-5, -3) == -8
    assert add(-10, 5) == -5


def test_add_zero():
    """Test adding with zero."""
    assert add(0, 0) == 0
    assert add(5, 0) == 5
    assert add(0, 10) == 10


def test_add_floats():
    """Test adding floating point numbers."""
    assert add(2.5, 3.5) == 6.0
    assert add(1.1, 2.2) == pytest.approx(3.3)


def test_add_mixed_types():
    """Test adding integers and floats."""
    assert add(5, 2.5) == 7.5
    assert add(3.7, 2) == 5.7


# New tests for the Flask dashboard
@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def test_dashboard_route(client):
    """Test that the dashboard route returns 200."""
    response = client.get('/')
    assert response.status_code == 200


def test_sales_data_api(client):
    """Test the sales data API endpoint."""
    response = client.get('/api/sales-data')
    assert response.status_code == 200
    data = response.get_json()
    assert 'labels' in data
    assert 'sales' in data
    assert 'expenses' in data
    assert len(data['labels']) == len(data['sales'])


def test_user_stats_api(client):
    """Test the user stats API endpoint."""
    response = client.get('/api/user-stats')
    assert response.status_code == 200
    data = response.get_json()
    assert 'total_users' in data
    assert 'active_users' in data
    assert 'new_users' in data
    assert 'premium_users' in data


def test_performance_data_api(client):
    """Test the performance data API endpoint."""
    response = client.get('/api/performance-data')
    assert response.status_code == 200
    data = response.get_json()
    assert 'labels' in data
    assert 'cpu' in data
    assert 'memory' in data


def test_category_distribution_api(client):
    """Test the category distribution API endpoint."""
    response = client.get('/api/category-distribution')
    assert response.status_code == 200
    data = response.get_json()
    assert 'labels' in data
    assert 'data' in data
    assert len(data['labels']) == len(data['data'])
