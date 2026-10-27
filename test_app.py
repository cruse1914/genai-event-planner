import pytest
from app import validate_inputs

def test_validate_inputs():
    assert validate_inputs(100, 50000) == True
    assert validate_inputs(0, 50000) == False
    assert validate_inputs(100, -500) == False
