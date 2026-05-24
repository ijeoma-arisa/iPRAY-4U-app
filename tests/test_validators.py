import unittest
from utils.validators import (
    parse_bool_default,
    parse_relationship,
    parse_str,
    validate_fields
)
from utils.error_messages import (
    required_error,
    string_error,
    non_empty_string_error,
    valid_relationship_error,
)

from models import Relationship
from helpers.sample_data import generate_person_json

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
        
    def setUp(self):
        self.actual_errors = []
        
    def test_valid_string(self):        
        self.assertEqual(parse_str(self.field, "Bob", self.actual_errors), "Bob")
        self.assertEqual(len(self.actual_errors), 0)
    
    def test_non_string(self):
        self.assertIsNone(parse_str(self.field, 123, self.actual_errors))
        self.assertListEqual(self.actual_errors, string_error(self.field, as_list=True))
        
    def test_empty_string(self):
        self.assertIsNone(parse_str(self.field, "", self.actual_errors))
        self.assertListEqual(self.actual_errors, non_empty_string_error(self.field, as_list=True))
        
    def test_whitespace_string(self):
        self.assertIsNone(parse_str(self.field, "\t   ", self.actual_errors))
        self.assertListEqual(self.actual_errors, non_empty_string_error(self.field, as_list=True))
    

class TestParseRelationship(unittest.TestCase):
    """Test cases for parse_relationship function."""
    @classmethod
    def setUpClass(cls):
        cls.field = "relationship"
        
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
        
    def test_valid_relationship_whitespace(self):
        self.assertEqual(parse_relationship(self.field, "Friends   ", self.actual_errors), Relationship.FRIENDS)
        self.assertEqual(parse_relationship(self.field, "\tFamily", self.actual_errors), Relationship.FAMILY)
        self.assertEqual(parse_relationship(self.field, "People I Know\n\n", self.actual_errors), Relationship.KNOWN)
        
        self.assertEqual(len(self.actual_errors), 0)

    def test_invalid_integer_input(self):        
        self.assertIsNone(parse_relationship(self.field, 123, self.actual_errors))
        self.assertListEqual(self.actual_errors, string_error(self.field, as_list=True))
        
    def test_invalid_none_input(self):        
        self.assertIsNone(parse_relationship(self.field, None, self.actual_errors))
        self.assertListEqual(self.actual_errors, string_error(self.field, as_list=True))
       
    def test_invalid_list_input(self):        
        self.assertIsNone(parse_relationship(self.field, ["friends"], self.actual_errors))
        self.assertListEqual(self.actual_errors, string_error(self.field, as_list=True))
    
    def test_invalid_relationship_input_different(self):      
        self.assertIsNone(parse_relationship(self.field, "Customer", self.actual_errors))
        self.assertListEqual(self.actual_errors, valid_relationship_error(self.field, as_list=True))
        
    def test_invalid_relationship_input_similar(self):      
        self.assertIsNone(parse_relationship(self.field, "Friend", self.actual_errors),)
        self.assertListEqual(self.actual_errors, valid_relationship_error(self.field, as_list=True))
    
    def test_invalid_whitespace_input(self):      
        self.assertIsNone(parse_relationship(self.field, "   ", self.actual_errors))
        self.assertListEqual(self.actual_errors, valid_relationship_error(self.field, as_list=True))
        
    def test_invalid_empty_string_input(self):      
        self.assertIsNone(parse_relationship(self.field, "", self.actual_errors))
        self.assertListEqual(self.actual_errors, valid_relationship_error(self.field, as_list=True))

class TestValidateFields(unittest.TestCase):
    """Test cases for validate_fields function."""
    
    @classmethod
    def setUpClass(cls):
        cls.validators = {
            "name": parse_str,
            "relationship": parse_relationship,
            "prayer": parse_str
        }
        
        cls.name_field = "name"
        cls.relationship_field = "relationship"
        cls.prayer_field = "prayer"
        
        cls.required_fields = ["name", "relationship", "prayer"]
    
    def test_all_fields_valid(self):
        """Test that all fields are parsed and no errors are listed."""
        
        data = generate_person_json(name="Bob", relationship="Family", prayer="Strength")
        
        parsed, errors = validate_fields(data, self.required_fields)
        
        expected_data = data.copy()
        expected_data["relationship"] = Relationship.FAMILY
        
        self.assertDictEqual(parsed, expected_data)        
        self.assertEqual(len(errors), 0)
    
    def test_missing_fields(self):
        """Test that missing fields are shown with errors."""
        
        missing_name_json = generate_person_json(name=None, relationship="Family", prayer="Strength")
        missing_relationship_json =  generate_person_json(name="Bob", relationship=None, prayer="Strength")
        missing_prayer_json =  generate_person_json(name="Bob", relationship="Family", prayer=None)
        missing_all_fields_empty_json = generate_person_json(name=None, relationship=None, prayer=None)
        missing_all_fields_invalid_json = {"field1": "Bob", "field2": "Family", "field3": "Safety"}
        
        missing_field_cases = [
            ("missing name", missing_name_json, required_error(self.name_field, as_list=True)),
            ("missing relationship", missing_relationship_json, required_error(self.relationship_field, as_list=True)),
            ("missing prayer", missing_prayer_json, required_error(self.prayer_field, as_list=True)),
            ("missing all fields (empty)", missing_all_fields_empty_json, required_error(self.required_fields, as_list=True)),
            ("missing all fields (invalid)", missing_all_fields_invalid_json, required_error(self.required_fields, as_list=True))
        ]
        
        for title, data, expected_errors in missing_field_cases:
            with self.subTest(case=title):
                parsed, errors = validate_fields(data, self.required_fields)
                
                expected_parsed = {field:value for field, value in data.items() if field in self.required_fields}
                
                if expected_parsed.get("relationship") is not None:
                    expected_parsed["relationship"] = Relationship.FAMILY
                                
                self.assertDictEqual(parsed, expected_parsed)
                self.assertListEqual(errors, expected_errors)

    def test_invalid_name(self):
        """Test that an error is provided when name is invalid."""
        
        null_name_json = generate_person_json(allow_null=True, name=None, relationship="Family", prayer="Strength")
        non_string_name_json = generate_person_json(name=123, relationship="Family", prayer="Strength")
        empty_string_name_json = generate_person_json(name="", relationship="Family", prayer="Strength")
        whitespace_name_json = generate_person_json(name="\t \n   ", relationship="Family", prayer="Strength")
        
        invalid_name_cases = [
            ("null name", null_name_json, string_error(self.name_field, as_list=True)),
            ("non-string name", non_string_name_json, string_error(self.name_field, as_list=True)),
            ("empty string name", empty_string_name_json, non_empty_string_error(self.name_field, as_list=True)),
            ("whitespace name", whitespace_name_json, non_empty_string_error(self.name_field, as_list=True))
        ]
        
        expected_parsed = {"relationship": Relationship.FAMILY, "prayer": "Strength"}
        
        for title, data, expected_errors in invalid_name_cases:
            with self.subTest(case=title):
                parsed, errors = validate_fields(data, self.required_fields)
                
                self.assertDictEqual(parsed, expected_parsed)
                self.assertListEqual(errors, expected_errors)
                
    def test_invalid_relationship(self):
        """Test that an error is provided when relationship is invalid."""
        
        null_relationship_json = generate_person_json(allow_null=True, name="Chris", relationship=None, prayer="Peace")
        non_string_relationship = generate_person_json(name="Chris", relationship=tuple("Friends"), prayer="Peace")
        invalid_relationship_type_json = generate_person_json(name="Chris", relationship="Stranger", prayer="Peace")
        whitespace_invalid_relationship_type_json = generate_person_json(name="Chris", relationship="Classmate\t   ", prayer="Peace")
        
        invalid_relationship_cases = [
            ("null relationship", null_relationship_json, string_error(self.relationship_field, as_list=True)),
            ("non-string relationship", non_string_relationship, string_error(self.relationship_field, as_list=True)),
            ("invalid relationship type", invalid_relationship_type_json, valid_relationship_error(self.relationship_field, as_list=True)),
            ("whitespace invalid relationship type", whitespace_invalid_relationship_type_json, valid_relationship_error(self.relationship_field, as_list=True))
        ]
        
        expected_parsed = {"name": "Chris", "prayer": "Peace"}
        
        for title, data, expected_errors in invalid_relationship_cases:
            with self.subTest(case=title):
                parsed, errors = validate_fields(data, self.required_fields)
                                
                self.assertDictEqual(parsed, expected_parsed)
                self.assertListEqual(errors, expected_errors)
        

    def test_invalid_prayer(self):
        """Test that an error is provided when prayer is invalid."""

        null_prayer_json = generate_person_json(allow_null=True, name="Sarah", relationship="People I Know", prayer=None)
        non_string_prayer_json = generate_person_json(name="Sarah", relationship="People I Know", prayer=["Strength"])
        empty_string_prayer_json = generate_person_json(name="Sarah", relationship="People I Know", prayer="")
        whitespace_prayer_json = generate_person_json(name="Sarah", relationship="People I Know", prayer="\n   \n")
        
        invalid_prayer_cases = [
            ("null prayer", null_prayer_json, string_error(self.prayer_field, as_list=True)),
            ("non-string prayer", non_string_prayer_json, string_error(self.prayer_field, as_list=True)),
            ("empty string prayer", empty_string_prayer_json, non_empty_string_error(self.prayer_field, as_list=True)),
            ("whitespace prayer", whitespace_prayer_json, non_empty_string_error(self.prayer_field, as_list=True))
        ]
        
        expected_parsed = {"name": "Sarah", "relationship": Relationship.KNOWN}
        
        for title, data, expected_errors in invalid_prayer_cases:
            with self.subTest(case=title):
                parsed, errors = validate_fields(data, self.required_fields)

                self.assertDictEqual(parsed, expected_parsed)
                self.assertListEqual(errors, expected_errors)

if __name__ == '__main__':
    unittest.main()
