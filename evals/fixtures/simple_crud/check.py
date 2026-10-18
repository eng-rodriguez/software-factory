import unittest
from service import rename_item
class Rename(unittest.TestCase):
    def test_name(self):
        self.assertEqual(rename_item({"name": "old"}, "new")["name"], "new")
if __name__ == "__main__":
    unittest.main()
