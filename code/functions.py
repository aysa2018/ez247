import json
from menu_manager import MenuManager
menu = MenuManager("data/enhanced_menu.json")


def check_availability(item: str) -> str:
   from menu_manager import MenuManager
   menu = MenuManager("data/enhanced_menu.json")


   if item in menu.menu:
       return f"✅ Yes, we have {item}. Please ask for specific options."


   if menu.is_available(item):
       price = menu.get_price(item)
       return f"✅ Yes, {item} is available at ${price:.2f}."


   return f"❌ Sorry, {item} is not on the menu."


def place_order(item_name: str) -> str:
   with open("orders.txt", "a") as f:
       f.write(item_name + "\n")
   return f"🧾 Order placed for {item_name}."



