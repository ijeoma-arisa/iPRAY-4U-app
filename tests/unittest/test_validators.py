import unittest
from utils.validators import (
    parse_bool_default,
    parse_relationship,
    parse_str,
    validate_fields
)
from models import Relationship
from tests.sample_data_helpers import generate_sample_person

class TestParseBoolDefault(unittest.TestCase):
    """Test cases for parse_bool_default function."""
    
    def test_bool_default_false(self):
        self.assertFalse(parse_bool_default(False))
        self.assertFalse(parse_bool_default("hello"))
        self.assertFalse(parse_bool_default(None))
        
        self.assertFalse(parse_bool_default(123, False))
        self.assertFalse(parse_bool_default(None, False))
        self.assertFalse(parse_bool_default("yes", False))
    
    def test_bool_default_true(self):
        self.assertTrue(parse_bool_default(True))
        self.assertTrue(parse_bool_default("hello", True))
        self.assertTrue(parse_bool_default(None, True))
       
 
class TestParseStr(unittest.TestCase):
    """Test cases for parse_str function."""
    
    @classmethod
    def setUpClass(cls):
        cls.field = "name"
        cls.expected_errors_string = [f"'{cls.field}' must be a string."]
        cls.expected_errors_non_empty_string = [f"'{cls.field}' must be a non-empty string."]
        
    def setUp(self):
        self.actual_errors = []
        
    def test_valid_string(self):        
        self.assertEqual(parse_str(self.field, "Bob", self.actual_errors), "Bob")
        self.assertEqual(len(self.actual_errors), 0)
    
    def test_non_string(self):
        self.assertIsNone(parse_str(self.field, 123, self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_string)
        
    def test_empty_string(self):
        self.assertIsNone(parse_str(self.field, "", self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_non_empty_string)
        
    def test_whitespace_string(self):
        self.assertIsNone(parse_str(self.field, "\t   ", self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_non_empty_string)
    

class TestParseRelationship(unittest.TestCase):
    """Test cases for parse_relationship function."""
    
    @classmethod
    def setUpClass(cls):
        cls.field = "relationship"
        cls.expected_errors_string = [f"'{cls.field}' must be a string."]
        
        valid_relationships = [r.value for r in Relationship]
        cls.expected_errors_relationship = [f"'{cls.field}' must be one of {valid_relationships}"]
        
    def setUp(self):
        self.actual_errors = []
    
    def test_valid_relationship_lowercase(self):        
        self.assertEqual(parse_relationship(self.field, "friends", self.actual_errors), Relationship.FRIENDS)
        self.assertEqual(parse_relationship(self.field, "family", self.actual_errors), Relationship.FAMILY)
        self.assertEqual(parse_relationship(self.field, "people i know", self.actual_errors), Relationship.KNOWN)
        
        self.assertEqual(len(self.actual_errors), 0)
    
    def test_valid_relationship_uppercase(self):        
        self.assertEqual(parse_relationship(self.field, "FRIENDS", self.actual_errors), Relationship.FRIENDS)
        self.assertEqual(parse_relationship(self.field, "FAMILY", self.actual_errors), Relationship.FAMILY)
        self.assertEqual(parse_relationship(self.field, "PEOPLE I KNOW", self.actual_errors), Relationship.KNOWN)
        
        self.assertEqual(len(self.actual_errors), 0)

    def test_valid_relationship_mixed_case(self):        
        self.assertEqual(parse_relationship(self.field, "Friends", self.actual_errors), Relationship.FRIENDS)
        self.assertEqual(parse_relationship(self.field, "fAmILy", self.actual_errors), Relationship.FAMILY)
        self.assertEqual(parse_relationship(self.field, "pEoPle i KNOW", self.actual_errors), Relationship.KNOWN)
        
        self.assertEqual(len(self.actual_errors), 0)

    def test_invalid_integer_input(self):        
        self.assertIsNone(parse_relationship(self.field, 123, self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_string)
        
    def test_invalid_none_input(self):        
        self.assertIsNone(parse_relationship(self.field, None, self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_string)
       
    def test_invalid_list_input(self):        
        self.assertIsNone(parse_relationship(self.field, ["friends"], self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_string)
    
    def test_invalid_relationship_input_1(self):      
        self.assertIsNone(parse_relationship(self.field, "Customer", self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_relationship)
        
    def test_invalid_relationship_input_2(self):      
        self.assertIsNone(parse_relationship(self.field, "Friend", self.actual_errors),)
        self.assertListEqual(self.actual_errors, self.expected_errors_relationship)

    def test_invalid_relationship_input_3(self):      
        self.assertIsNone(parse_relationship(self.field, "Fam", self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_relationship)
    
    def test_invalid_whitespace_input(self):      
        self.assertIsNone(parse_relationship(self.field, "   ", self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_relationship)
        
    def test_invalid_empty_string_input(self):      
        self.assertIsNone(parse_relationship(self.field, "", self.actual_errors))
        self.assertListEqual(self.actual_errors, self.expected_errors_relationship)


class TestValidateFields(unittest.TestCase):
    """Test cases for require_fields function."""
    
    @classmethod
    def setUpClass(cls):
        cls.validators = {
            "name": parse_str,
            "relationship": parse_relationship,
            "prayer": parse_str
        }
        
        cls.required_fields = ["name", "relationship", "prayer"]
    
    def test_all_fields_present(self):
        """Test that all fields are parsed and no errors are listed."""
        
        data = generate_sample_person(name="Bob", relationship="Family", prayer="Strength")
        
        parsed, errors = validate_fields(data, self.required_fields)
        
        expected_data = data.copy()
        expected_data["relationship"] = Relationship.FAMILY
        
        self.assertDictEqual(parsed, expected_data)        
        self.assertEqual(len(errors), 0)
    
    def test_missing_one_field(self):
        """Test that an error is provided when one field is missing."""
        
        data = generate_sample_person(name=None, relationship="Family", prayer="Strength")
        
        parsed, errors = validate_fields(data, self.required_fields)
        
        expected_data = data.copy()
        expected_data["relationship"] = Relationship.FAMILY
        
        self.assertDictEqual(parsed, expected_data)
        self.assertListEqual(errors, ["'name' is required."])
    
    def test_missing_multiple_fields(self):
        """Test that multiple errors are provided when multiple fields are missing."""
        
        data = generate_sample_person(name=None, relationship="Family", prayer=None)
        
        parsed, errors = validate_fields(data, self.required_fields)
        
        expected_data = {}
        expected_data["relationship"] = Relationship.FAMILY
        
        self.assertDictEqual(parsed, expected_data)
        self.assertListEqual(errors, ["'name' is required.", "'prayer' is required."])
    
    def test_error_message_lists_missing_fields(self):
        data = generate_sample_person(name=None, relationship=None, prayer=None)
        
        parsed, errors = validate_fields(data, self.required_fields)
        
        self.assertEqual(len(parsed), 0)
        self.assertListEqual(errors, ["'name' is required.", "'relationship' is required.", "'prayer' is required."])

if __name__ == '__main__':
    unittest.main()
