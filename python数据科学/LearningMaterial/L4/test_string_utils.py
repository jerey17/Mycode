# Module to demonstrate use of pytest.

def reverse_string(s):
    """Return the reverse of string s."""
    return s[::-1]

def test_reverse_string_simple():
    assert reverse_string("abc") == "cba"

def test_reverse_string_palindrome():
    assert reverse_string("racecar") == "racecar"
