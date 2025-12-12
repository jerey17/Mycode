# See Lecture Jupyter Notebook to run inline.
from testmod.math_utils import add_numbers
import unittest
import math

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

# Add a pytest-compatible function
def test_add_missing():
    '''
    Note:
    The IEEE 754 standard specifies that NaN 
    is not equal to any value, including itself.
    '''
    assert math.isnan(add_numbers(float('NaN'), 6))

if __name__ == '__main__':
    unittest.main()
