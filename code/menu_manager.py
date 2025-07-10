# file: menu_manager.py


import json
from typing import Optional


class MenuManager:
   def __init__(self, path="data/enhanced_menu.json"):
       with open(path, "r", encoding="utf-8") as f:
           self.menu = json.load(f)
       print("🍕 Menu categories loaded:", list(self.menu.keys()))


   def list_categories(self) -> list:
       return list(self.menu.keys())


   def get_item(self, item_name: str) -> Optional[dict]:
       item_name_lower = item_name.strip().lower()


       for category, subcategories in self.menu.items():
           if category.lower() == item_name_lower:
               return {"name": category, "category": category, "price": None}


           if isinstance(subcategories, dict):
               for subcat, items in subcategories.items():
                   if isinstance(items, dict):
                       for dish, price in items.items():
                           if dish.lower() == item_name_lower:
                               return {"name": dish, "category": category, "price": price}
                   elif isinstance(items, (int, float, str)):
                       if subcat.lower() == item_name_lower:
                           return {"name": subcat, "category": category, "price": items}
       return None




   def get_items_in_category(self, category_name: str) -> Optional[list]:
       cat = self.menu.get(category_name)
       if isinstance(cat, dict):
           items = []
           for sub in cat.values():
               if isinstance(sub, dict):
                   items.extend(sub.keys())
               elif isinstance(sub, str):  # for Acai Bowl flavor descriptions
                   continue
               else:
                   items.append(sub)
           return items
       elif isinstance(cat, list):
           return cat
       return None
                      


   def is_available(self, item_name: str) -> bool:
       return self.get_item(item_name) is not None


   def get_price(self, item_name: str) -> Optional[float]:
       item = self.get_item(item_name)
       return item["price"] if item else None


   def get_category(self, item_name: str) -> Optional[str]:
       item = self.get_item(item_name)
       return item["category"] if item else None


   def list_items(self) -> list:
       items = []


       def recurse_menu(section):
           if isinstance(section, dict):
               for key, val in section.items():
                   if isinstance(val, (int, float)):  # It's a dish with a price
                       items.append(key)
                   else:  # Go deeper
                       recurse_menu(val)
           elif isinstance(section, list):  # Example: sauces
               items.extend(section)


       recurse_menu(self.menu)
       return items





