import unittest
from utils.validators import (
    is_valid_string,
    is_valid_int,
    is_valid_bool,
    require_str,
    require_fields,
    parse_relationship
)
from models import Relationship


class TestIsValidString(unittest.TestCase):
    """Test cases for is_valid_string function."""
    
    def test_valid_string(self):
        self.assertTrue(is_valid_string("Hello"))
    
    def test_empty_string(self):
        self.assertFalse(is_valid_string(""))
    
    def test_whitespace_only_string(self):
        self.assertFalse(is_valid_string("   "))
    
    def test_non_string_input(self):
        self.assertFalse(is_valid_string(123))
        self.assertFalse(is_valid_string(["hello"]))
        self.assertFalse(is_valid_string(None))

class TestIsValidInt(unittest.TestCase):
    """Test cases for is_valid_int function."""
    
    def test_positive_integer(self):
        self.assertTrue(is_valid_int(5))
    
    def test_zero(self):
        self.assertFalse(is_valid_int(0))
    
    def test_negative_integer(self):
        self.assertFalse(is_valid_int(-3))
    
    def test_non_integer_input(self):
        self.assertFalse(is_valid_int("10"))
        self.assertFalse(is_valid_int(4.5))
        self.assertFalse(is_valid_int(None))

class TestIsValidBool(unittest.TestCase):
    """Test cases for is_valid_bool function."""
    
    def test_true_value(self):
      self.assertTrue(is_valid_bool(True))        
    
    def test_false_value(self):
        self.assertTrue(is_valid_bool(False))        

    def test_non_bool_input(self):
        self.assertFalse(is_valid_bool(0))
        self.assertFalse(is_valid_bool(1))
        self.assertFalse(is_valid_bool("True"))
        self.assertFalse(is_valid_bool("False"))
        self.assertFalse(is_valid_bool(None))

class TestRequireStr(unittest.TestCase):
    """Test cases for require_str function."""
    
    def test_valid_string_passes(self):
        self.assertIsNone(require_str("Valid String", "test_field"))
    
    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            require_str("", "test_field")
    
    def test_non_string_raises(self):
        with self.assertRaises(ValueError):
          require_str(123, "test_field")
        
        with self.assertRaises(ValueError):
          require_str(None, "test_field")
    
    def test_error_message_contains_field_name(self):
        with self.assertRaisesRegex(ValueError, "name"):
            require_str("", "name")
    

class TestRequireFields(unittest.TestCase):
    """Test cases for require_fields function."""
    data = {
        "text": "Alice",
        "has_prayed": False
    }
    
    def test_all_fields_present(self):
        """Test that no exception is raised when all fields are present."""
        # TODO: Implement test
        pass
    
    def test_missing_one_field(self):
        """Test that ValueError is raised when a field is missing."""
        # TODO: Implement test
        pass
    
    def test_missing_multiple_fields(self):
        """Test that ValueError is raised when multiple fields are missing."""
        # TODO: Implement test
        pass
    
    def test_error_message_lists_missing_fields(self):
        """Test that the error message lists all missing fields."""
        # TODO: Implement test
        pass


class TestParseRelationship(unittest.TestCase):
    """Test cases for parse_relationship function."""
    
    def test_valid_relationship_lowercase(self):
        self.assertEqual(parse_relationship("friends"), Relationship.FRIENDS)
        self.assertEqual(parse_relationship("family"), Relationship.FAMILY)
        self.assertEqual(parse_relationship("ministry"), Relationship.MINISTRY)
        self.assertEqual(parse_relationship("custom"), Relationship.CUSTOM)
    
    def test_valid_relationship_uppercase(self):
        self.assertEqual(parse_relationship("FRIENDS"), Relationship.FRIENDS)
        self.assertEqual(parse_relationship("FAMILY"), Relationship.FAMILY)
        self.assertEqual(parse_relationship("MINISTRY"), Relationship.MINISTRY)
        self.assertEqual(parse_relationship("CUSTOM"), Relationship.CUSTOM)
    
    def test_valid_relationship_mixed_case(self):
        self.assertEqual(parse_relationship("Friends"), Relationship.FRIENDS)
        self.assertEqual(parse_relationship("fAmILy"), Relationship.FAMILY)
        self.assertEqual(parse_relationship("MiniStry"), Relationship.MINISTRY)
        self.assertEqual(parse_relationship("CuStOm"), Relationship.CUSTOM)
    
    def test_invalid_relationship_string(self):
        self.assertIsNone(parse_relationship("Customer"))
        self.assertIsNone(parse_relationship("Friend"))
        self.assertIsNone(parse_relationship("Fam"))        
    
    def test_empty_string_or_whitespace(self):
        self.assertIsNone(parse_relationship(""))
        self.assertIsNone(parse_relationship("   "))
        self.assertIsNone(parse_relationship("\n"))
    
    def test_non_string_input_returns_none(self):
        self.assertIsNone(parse_relationship(123))
        self.assertIsNone(parse_relationship(None))
        self.assertIsNone(parse_relationship([]))


if __name__ == '__main__':
    unittest.main()
