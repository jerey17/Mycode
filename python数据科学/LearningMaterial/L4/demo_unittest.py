# For demonstration in a Jupyter Notebook, 
# we have added the arguments to unittest.main().

import unittest

# The code we want to test:
def add_numbers(a, b):
    """Return the sum of a and b."""
    return a + b

class TestMathUtils(unittest.TestCase):
    """Tests for the add_numbers function."""

    def test_add_positive_values(self):
        self.assertEqual(add_numbers(2, 3), 5)
        self.assertEqual(add_numbers(10, 5), 15)
    
    def test_add_negative_values(self):
        self.assertEqual(add_numbers(-1, -2), -3)
        self.assertEqual(add_numbers(-10, -5), -15)
    
    def test_add_zero(self):
        self.assertEqual(add_numbers(0, 5), 5)
        self.assertEqual(add_numbers(5, 0), 5)

# The following block is necessary to run tests in a notebook:
if __name__ == '__main__':
    unittest.main()
