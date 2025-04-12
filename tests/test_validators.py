import pytest
from rest_framework.exceptions import ValidationError
from utils.validators import validate_no_html


def test_validate_no_html_valid_input():
    value = "This is a safe string"
    assert validate_no_html(value) == value


def test_validate_no_html_with_angle_brackets():
    with pytest.raises(ValidationError) as exc_info:
        validate_no_html("This string contains <html> tags")
    assert "No HTML tag < allowed." in str(exc_info.value)
    assert "No HTML tag > allowed." in str(exc_info.value)


def test_validate_no_html_with_only_less_than():
    with pytest.raises(ValidationError) as exc_info:
        validate_no_html("This string contains < only")
    assert "No HTML tag < allowed." in str(exc_info.value)


def test_validate_no_html_with_only_greater_than():
    with pytest.raises(ValidationError) as exc_info:
        validate_no_html("This string contains > only")
    assert "No HTML tag > allowed." in str(exc_info.value)
