import pytest
from pydantic import ValidationError
from app.models.profile import SearchRequest
from app.services.university_database import norm, acronym, suggest

def test_normalization():
    assert norm('University-of Tokyo!') == 'university of tokyo'

def test_query_validation():
    with pytest.raises(ValidationError):
        SearchRequest(query='')

def test_abbreviation():
    assert acronym('Massachusetts Institute of Technology') == 'MIT'
    assert suggest('MIT')[0].name == 'Massachusetts Institute of Technology'
