# file: menu_manager.py

from typing import Any, Dict, Union
import json
from difflib import get_close_matches

class MenuManager:
    def __init__(self, menu_path):
        with open(menu_path, 'r') as f:
            self.menu = json.load(f)

        self.item_index = self._build_index()
        self.category_to_flavors = self._build_flavor_index()

    def _build_index(self) -> Dict[str, Union[str, tuple]]:
        index = {}

        def recurse(category: str, subtree: Any):
            if isinstance(subtree, dict):
                for k, v in subtree.items():
                    if isinstance(v, (int, float)):
                        index[k.lower()] = (category, k)
                    elif isinstance(v, dict):
                        recurse(category, v)
                    elif isinstance(v, str):
                        # This handles descriptive strings, e.g., Acai Bowl flavors
                        continue  # don't index
            elif isinstance(subtree, list):
                for item in subtree:
                    index[item.lower()] = (category, item)

        for category, content in self.menu.items():
            recurse(category, content)

        return index

    def _build_flavor_index(self):
        category_to_flavors = {}

        for category, items in self.menu.items():
            flavors = []

            def collect_flavors(subtree):
                if isinstance(subtree, dict):
                    for k, v in subtree.items():
                        if isinstance(v, str):  # flavor descriptions
                            flavors.append(k)
                        elif isinstance(v, dict):
                            collect_flavors(v)

            collect_flavors(items)
            if flavors:
                category_to_flavors[category.lower()] = flavors

        return category_to_flavors


    def get_price(self, item_name: str) -> Union[str, float, Dict[str, float]]:
        key = item_name.lower()
        if key not in self.item_index:
            return "❌ Not found"

        category, item = self.item_index[key]
        cat_data = self.menu[category]

        if isinstance(cat_data, dict):
            price = cat_data.get(item)
            if isinstance(price, (int, float)):
                return price
            elif isinstance(price, str):
                # price is description -> look for "Small" and "Large"
                sizes = {k: v for k, v in cat_data.items() if isinstance(v, (int, float))}
                if sizes:
                    return sizes
        return "❌ Price not found"

    def list_items(self):
        return list(self.item_index.keys())

    def list_flavors(self, category: str):
        return self.category_to_flavors.get(category.lower(), [])

    def is_available(self, item_name: str) -> bool:
        if not item_name:
            return False
        return item_name.lower() in self.item_index

    def has_flavors(self, category: str) -> bool:
        if not category:
            return False
        return category.lower() in self.category_to_flavors

    def get_price_for_flavor(self, category: str, flavor: str) -> Union[float, str]:
        if category not in self.menu:
            return "❌ Category not found"

        items = self.menu[category]
        if flavor not in items:
            return "❌ Flavor not found"

        return "Please specify a size (Small or Large)"

    def validate_flavor(self, category: str, flavor: str) -> bool:
        return flavor in self.menu.get(category, {})

    def validate_size_for_flavor(self, category: str, flavor: str, size: str) -> bool:
        cat = self.menu.get(category)
        return isinstance(cat, dict) and size in cat and isinstance(cat[size], (int, float))
    

    def find_closest_item(self, item_name: str, cutoff: float = 0.8):
        item_name = item_name.lower()
        matches = get_close_matches(item_name, self.item_index.keys(), n=1, cutoff=cutoff)
        return matches[0] if matches else None

# import json
# from typing import Optional


# class MenuManager:
#    def __init__(self, path="data/enhanced_menu.json"):
#        with open(path, "r", encoding="utf-8") as f:
#            self.menu = json.load(f)
#        print("🍕 Menu categories loaded:", list(self.menu.keys()))


#    def list_categories(self) -> list:
#        return list(self.menu.keys())


#    def get_item(self, item_name: str) -> Optional[dict]:
#        item_name_lower = item_name.strip().lower()


#        for category, subcategories in self.menu.items():
#            if category.lower() == item_name_lower:
#                return {"name": category, "category": category, "price": None}


#            if isinstance(subcategories, dict):
#                for subcat, items in subcategories.items():
#                    if isinstance(items, dict):
#                        for dish, price in items.items():
#                            if dish.lower() == item_name_lower:
#                                return {"name": dish, "category": category, "price": price}
#                    elif isinstance(items, (int, float, str)):
#                        if subcat.lower() == item_name_lower:
#                            return {"name": subcat, "category": category, "price": items}
#        return None




#    def get_items_in_category(self, category_name: str) -> Optional[list]:
#        cat = self.menu.get(category_name)
#        if isinstance(cat, dict):
#            items = []
#            for sub in cat.values():
#                if isinstance(sub, dict):
#                    items.extend(sub.keys())
#                elif isinstance(sub, str):  # for Acai Bowl flavor descriptions
#                    continue
#                else:
#                    items.append(sub)
#            return items
#        elif isinstance(cat, list):
#            return cat
#        return None
                      


#    def is_available(self, item_name: str) -> bool:
#        return self.get_item(item_name) is not None


#    def get_price(self, item_name: str) -> Optional[float]:
#        item = self.get_item(item_name)
#        return item["price"] if item else None


#    def get_category(self, item_name: str) -> Optional[str]:
#        item = self.get_item(item_name)
#        return item["category"] if item else None


#    def list_items(self) -> list:
#        items = []


#        def recurse_menu(section):
#            if isinstance(section, dict):
#                for key, val in section.items():
#                    if isinstance(val, (int, float)):  # It's a dish with a price
#                        items.append(key)
#                    else:  # Go deeper
#                        recurse_menu(val)
#            elif isinstance(section, list):  # Example: sauces
#                items.extend(section)


#        recurse_menu(self.menu)
#        return items





