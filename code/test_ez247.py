import unittest
from menu_manager import MenuManager

menu = MenuManager("data/enhanced_menu.json")  # or your actual path

class TestMenuManagerCore(unittest.TestCase):

    def test_known_categories(self):
        self.assertTrue(menu.has_flavors("Pizza"))
        self.assertTrue(menu.has_flavors("Acai Bowls"))
        self.assertFalse(menu.has_flavors("Unknown Category"))

    def test_list_flavors_pizza(self):
        flavors = menu.list_flavors("Pizza")
        expected = {"OG Bowl", "Tropical Bowl", "Choco Bowl", "Berry Bowl"}
        self.assertIn("Margherita", menu.item_index)
        self.assertIn("Farm House", menu.item_index)
        self.assertIn("Chicken Alfredo", menu.item_index)

    def test_list_flavors_acai_bowl(self):
        flavors = menu.list_flavors("Acai Bowls")
        self.assertIn("OG Bowl", flavors)
        self.assertIn("Choco Bowl", flavors)
        self.assertNotIn("Pepperoni", flavors)

    def test_item_availability(self):
        self.assertTrue(menu.is_available("Chicken Teriyaki"))
        self.assertTrue(menu.is_available("Beef Supreme"))
        self.assertFalse(menu.is_available("Alien Pizza"))

    def test_get_price_float(self):
        price = menu.get_price("Chicken Tenders (6 pcs)")
        self.assertEqual(price, 23.0)

    def test_get_price_sizes(self):
        prices = menu.get_price("Small")
        self.assertEqual(prices, 39.0)  # From Acai Bowls

    def test_get_price_not_found(self):
        self.assertEqual(menu.get_price("Alien Burger"), "❌ Not found")

if __name__ == "__main__":
    unittest.main()
