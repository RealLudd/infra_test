import pytest
from app import add


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
