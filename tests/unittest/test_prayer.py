import unittest

from models import Prayer

class TestPrayer(unittest.TestCase):
  def setUp(self):
    self.pr = Prayer()
  
  def test_initial_state(self):
    self.assertIsNone(self.pr.get_text())
    self.assertFalse(self.pr.has_prayed())
    
  def test_text(self):
    text = "Peace of mind"
    self.pr.set_text(text)
    self.assertEqual(self.pr.get_text(), text)
    
  def test_prayed(self):
    self.pr.set_prayed(True)
    self.assertTrue(self.pr.has_prayed())
    
    
if __name__ == "__main__":
  unittest.main()