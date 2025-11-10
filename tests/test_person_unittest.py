import unittest

from models import Person, Relationship

class TestPerson(unittest.TestCase):
  def setUp(self):
    self.p = Person("1", "Alice", Relationship.FAMILY)
    
  def test_initial_state(self):
    self.assertEqual(self.p.get_id(), "1")
    self.assertEqual(self.p.get_name(), "Alice")
    self.assertEqual(self.p.get_relationship(), Relationship.FAMILY)
    self.assertEqual(len(self.p.get_prayer_requests()), 0)
    
  def test_id(self):
    self.p.set_id("2")
    self.assertEqual(self.p.get_id(), "2")
    
  def test_name(self):
    self.p.set_name("Bob")
    self.assertEqual(self.p.get_name(), "Bob")
    
  def test_relationship(self):
    self.p.set_relationship(Relationship.FRIENDS)
    self.assertEqual(self.p.get_relationship(), Relationship.FRIENDS)

  
if __name__ == "__main__":
  unittest.main()