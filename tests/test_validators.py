import pytest
from rest_framework.exceptions import ValidationError
from utils.validators import validate_no_html


def test_validate_no_html_valid_input():
    """
    Test that validate_no_html() does not raise ValidationError when given a
    string without any HTML tags.

    The function should return the input string unmodified.
    """
    value = "This is a safe string"
    assert validate_no_html(value) == value


def test_validate_no_html_with_angle_brackets():
    """
    Test that validate_no_html() raises ValidationError when given a
    string containing HTML tags with angle brackets.

    The function should raise an error indicating that both '<' and '>'
    are not allowed in the input string.
    """

    with pytest.raises(ValidationError) as exc_info:
        validate_no_html("This string contains <html> tags")
    assert "No HTML tag < allowed." in str(exc_info.value)
    assert "No HTML tag > allowed." in str(exc_info.value)


def test_validate_no_html_with_only_less_than():
    """
    Test that validate_no_html() raises ValidationError when given a
    string containing a '<' character but no '>' character.

    The function should raise an error indicating that '<' is not allowed
    in the input string.
    """
    with pytest.raises(ValidationError) as exc_info:
        validate_no_html("This string contains < only")
    assert "No HTML tag < allowed." in str(exc_info.value)


def test_validate_no_html_with_only_greater_than():
    """
    Test that validate_no_html() raises ValidationError when given a
    string containing a '>' character but no '<' character.

    The function should raise an error indicating that '>' is not allowed
    in the input string.
    """

    with pytest.raises(ValidationError) as exc_info:
        validate_no_html("This string contains > only")
    assert "No HTML tag > allowed." in str(exc_info.value)
