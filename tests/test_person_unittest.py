import unittest

from models import Person

class TestPerson(unittest.TestCase):
  def setUp(self):
    self.p = Person("1", "Alice", "Family")
    
  def test_initial_state(self):
    self.assertEqual(self.p.get_id(), "1")
    self.assertEqual(self.p.get_name(), "Alice")
    self.assertEqual(self.p.get_relationship(), "Family")
    
  def test_id(self):
    self.p.set_id("2")
    self.assertEqual(self.p.get_id(), "2")
    
  def test_name(self):
    self.p.set_name("Alice")
    self.assertEqual(self.p.get_name(), "Alice")
  
if __name__ == "__main__":
  unittest.main()