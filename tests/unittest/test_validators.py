import unittest
from utils.validators import (
    is_valid_string,
    is_valid_int,
    is_valid_int_as_bool,
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

class TestIsValidIntAsBool(unittest.TestCase):
    """Test cases for is_valid_int_as_bool function."""
    
    def test_true_value(self):
      self.assertTrue(is_valid_int_as_bool(1))        
    
    def test_false_value(self):
        self.assertTrue(is_valid_int_as_bool(0))        

    def test_non_int_input(self):
        self.assertFalse(is_valid_int_as_bool("0"))
        self.assertFalse(is_valid_int_as_bool("1"))
        self.assertFalse(is_valid_int_as_bool(None))

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
        pass
    
    def test_missing_one_field(self):
        """Test that ValueError is raised when a field is missing."""
        pass
    
    def test_missing_multiple_fields(self):
        """Test that ValueError is raised when multiple fields are missing."""
        pass
    
    def test_error_message_lists_missing_fields(self):
        """Test that the error message lists all missing fields."""
        pass


class TestParseRelationship(unittest.TestCase):
    """Test cases for parse_relationship function."""
    
    def test_valid_relationship_lowercase(self):
        self.assertEqual(parse_relationship("relationship", "friends"), Relationship.FRIENDS)
        self.assertEqual(parse_relationship("relationship", "family"), Relationship.FAMILY)
        self.assertEqual(parse_relationship("relationship", "people i know"), Relationship.KNOWN)
    
    def test_valid_relationship_uppercase(self):
        self.assertEqual(parse_relationship("relationship", "FRIENDS"), Relationship.FRIENDS)
        self.assertEqual(parse_relationship("relationship", "FAMILY"), Relationship.FAMILY)
        self.assertEqual(parse_relationship("relationship", "PEOPLE I KNOW"), Relationship.KNOWN)
    
    def test_valid_relationship_mixed_case(self):
        self.assertEqual(parse_relationship("relationship", "Friends"), Relationship.FRIENDS)
        self.assertEqual(parse_relationship("relationship", "fAmILy"), Relationship.FAMILY)
        self.assertEqual(parse_relationship("relationship", "pEoPle i KNOW"), Relationship.KNOWN)
    
    def test_invalid_relationship_string(self):
        def error_msg(rel):
            return f"Invalid relationship: Relationship '{rel}' does not exist." 

        self.assertEqual(parse_relationship("relationship", "Customer"), [error_msg("Customer")])
        self.assertEqual(parse_relationship("relationship", "Friend"), [error_msg("Friend")])
        self.assertEqual(parse_relationship("relationship", "Fam"), [error_msg("Fam")])        
    
    def test_empty_string_or_whitespace(self):
        error_msg = "Invalid string: 'relationship' must be a non-empty string." 
        
        self.assertEqual(parse_relationship("relationship", ""), [error_msg])
        self.assertEqual(parse_relationship("relationship", "   "), [error_msg])
        self.assertEqual(parse_relationship("relationship", "\n"), [error_msg])
    
    def test_non_string_input_returns_none(self):
        def error_msg(non_string_input):
            return f"Invalid type: 'relationship' must be a string. Received type {type(non_string_input)}."
         
        self.assertEqual(parse_relationship("relationship", 123), [error_msg(123)])
        self.assertEqual(parse_relationship("relationship", None), [error_msg(None)])
        self.assertEqual(parse_relationship("relationship", []), [error_msg([])])

if __name__ == '__main__':
    unittest.main()
