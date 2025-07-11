from fastapi import FastAPI, Request
import re
import ast
from typing import Optional
from word2number import w2n
from difflib import get_close_matches
# from functions import check_availability as legacy_check_availability
from menu_manager import MenuManager
from speech_pipeline_manager import call_llm

menu = MenuManager("data/enhanced_menu.json")
app = FastAPI()

# Shared order state
order_session = {
    "items": [],
    "nyu_id": None,
    "building": None,
    "phone": None,
    "dietary": None,
    "pending_category": None

}

VALID_BUILDINGS = {
    "A1A", "A1B", "A1C", "A2A", "A2B", "A2C", "A3", "A4",
    "A5A", "A5B", "A5C", "A6A", "A6B", "A6C", "C1", "C2", "C3"
}

def normalize_building_input(text: str) -> str:
    spoken_to_letter = {
        "a": "A", "b": "B", "c": "C", "bee": "B", "see": "C", "dee": "D"
    }
    spoken_to_digit = {
        "zero": "0", "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6", "seven": "7",
        "eight": "8", "nine": "9"
    }

    cleaned = re.sub(r"[^\w]", "", text).upper()
    if cleaned in VALID_BUILDINGS:
        return cleaned

    words = text.lower().split()
    result = ""
    for word in words:
        if word in spoken_to_letter:
            result += spoken_to_letter[word]
        elif word in spoken_to_digit:
            result += spoken_to_digit[word]
        elif len(word) == 1 and word.isalpha():
            result += word.upper()
        elif word.isdigit():
            result += word

    return result if result in VALID_BUILDINGS else ""
def clarify_category(category: str) -> str:
    if not category:
        return "❌ I didn't catch the category."

    category = category.lower().rstrip('s')  # normalize plural to singular
    matched_category = None

    for cat in menu.menu.keys():
        if category in cat.lower() or cat.lower() in category:
            matched_category = cat
            break

    if not matched_category:
        return f"❌ Sorry, we don't have anything listed under {category}."

    options = menu.list_flavors(matched_category)
    if not options:
        return f"❌ No flavors available under {matched_category}."

    return f"✅ Yes, we have {matched_category}. What would you like? Options include: {', '.join(options)}"


def check_availability(item: str) -> str:
    if not item or item.strip().lower() == "unknown":
        return "❌ Sorry, that item wasn't understood."

    item = item.strip().lower()

    # Direct check using internal index
    if menu.is_available(item):
        canonical = menu.item_index[item][1]  # get original item name
        return f"✅ Yes, we have {canonical} available."

    # Fuzzy match as fallback
    close = get_close_matches(item, menu.item_index.keys(), n=1, cutoff=0.8)
    if close:
        suggestion = menu.item_index[close[0]][1]
        return f"✅ Yes, did you mean: {suggestion}?"

    # Deep recursive search as last resort (handles nested structure)
    def recursive_search(menu_section):
        if isinstance(menu_section, dict):
            for key, val in menu_section.items():
                if item in key.lower():
                    return key
                result = recursive_search(val)
                if result:
                    return result
        elif isinstance(menu_section, list):
            for val in menu_section:
                if item in val.lower():
                    return val
        elif isinstance(menu_section, str):
            if item in menu_section.lower():
                return menu_section
        return None

    match = recursive_search(menu.menu)
    if match:
        return f"✅ Yes, we have {match} available."

    return f"❌ Sorry, {item} is not on the menu."

# def place_order(query: str = "", item: str = "", quantity: int = 1) -> str:
#     global order_session
#     item = item or ""
#     query = query or ""

#     clean_query = re.sub(r'[^\w\s#]', '', (query or "").lower())
#     item = (item or "").strip()
#     print(f"[DEBUG] Checking item: {item} | Cleaned: {clean_query}")
#     # fuzzy match to correct item name if slightly off
#     matched = menu.find_closest_item(item)
#     if not matched:
#         return f"❌ Sorry, {item} is not on the menu."
#     item = matched

#     # 🔐 Guard: make sure item is not empty
#     if not item:
#         return "❌ Sorry, I didn’t understand the item you'd like to order."

#     # 🍧 Step 1: Flavor selection continuation
#         # First order step
#     elif not order_session["items"]:
#         # First check if the item is directly available (a specific dish/flavor)
#         if menu.is_available(item):
#             order_session["items"].append((item, quantity))

#         # Then check if it's a category (like "Pizza" or "Acai Bowls")
#         elif menu.has_flavors(item):
#             order_session["pending_category"] = item
#             order_session["pending_qty"] = quantity
#             return f"❓ Which {item} would you like? Options include: {', '.join(menu.list_flavors(item))}"
#         else:
#             return f"❌ Sorry, {item} is not on the menu."

#     # 🥡 Step 2: First item ordering
#     elif not order_session["items"]:
#         if menu.has_flavors(item):
#             order_session["pending_category"] = item
#             order_session["pending_qty"] = quantity
#             return f"❓ Which {item} would you like? Options include: {', '.join(menu.list_flavors(item))}"
#         elif menu.is_available(item):
#             order_session["items"].append((item, quantity))
#         else:
#             return f"❌ Sorry, {item} is not on the menu."

#     # 🆔 Step 3: NYU ID
#     if not order_session["nyu_id"]:
#         digits = "".join(re.findall(r'\d+', clean_query))
#         if len(digits) == 8:
#             order_session["nyu_id"] = "N" + digits
#         else:
#             return "📎 Please say the 8 digits of your NYU ID after the letter N."

#     # 🏢 Step 4: Building number
#     if not order_session["building"]:
#         building = normalize_building_input(clean_query)
#         if building in VALID_BUILDINGS:
#             order_session["building"] = building
#         else:
#             return "🏢 Please mention your building number."

#     # 📱 Step 5: Phone number
#     if not order_session["phone"]:
#         digits = "".join(re.findall(r'\d+', clean_query))
#         if len(digits) >= 9:
#             order_session["phone"] = digits
#             return "📝 Do you have any allergy info or special requests?"
#         else:
#             return "📱 Please provide your phone number."

#     # 🍽️ Step 6: Dietary notes
#     if not order_session["dietary"]:
#         keywords = ["no", "without", "allergy", "allergies", "nuts", "gluten", "lactose", "vegan", "extra", "spicy"]
#         if any(word in clean_query for word in keywords):
#             order_session["dietary"] = query
#         else:
#             return "📝 Do you have any allergy info or special requests?"

#     # ✅ Final confirmation
#     items_str = ", ".join(f"{qty} x {item}" for item, qty in order_session["items"])
#     confirmed = (
#         f"✅ Order confirmed for: {items_str}!\n"
#         f"🤚 NYU ID: {order_session['nyu_id']}, 🏢 Building: {order_session['building']}, 📱 Phone: {order_session['phone']}.\n"
#     )
#     if order_session["dietary"]:
#         confirmed += f"📝 Note: {order_session['dietary']}"

#     # 🔄 Reset session
#     order_session = {
#         "items": [],
#         "nyu_id": None,
#         "building": None,
#         "phone": None,
#         "dietary": None
#     }

#     return confirmed

def place_order(query: str = "", item: str = "", quantity: int = 1) -> str:
    global order_session
    item = item or ""
    query = query or ""
    clean_query = re.sub(r'[^\w\s#]', '', (query or "").lower())
    item = (item or "").strip()
    print(f"[DEBUG] Checking item: {item} | Cleaned: {clean_query}")

    # ✅ Case 1: If it's a known category like "Pizza"
    if menu.has_flavors(item):
        order_session["pending_category"] = item
        order_session["pending_qty"] = quantity
        return f"❓ Which {item} would you like? Options include: {', '.join(menu.list_flavors(item))}"

    # ✅ Case 2: Try fuzzy match for exact dish
    matched = menu.find_closest_item(item)
    if not matched:
        return f"❌ Sorry, {item} is not on the menu."
    item = matched

    if not order_session["items"]:
        order_session["items"].append((item, quantity))


    # 🆔 Step 2: NYU ID
    if not order_session["nyu_id"]:
        digits = "".join(re.findall(r'\d+', clean_query))
        if len(digits) == 8:
            order_session["nyu_id"] = "N" + digits
        else:
            return "📎 Please say the 8 digits of your NYU ID after the letter N."

    # 🏢 Step 3: Building number
    if not order_session["building"]:
        building = normalize_building_input(clean_query)
        if building in VALID_BUILDINGS:
            order_session["building"] = building
        else:
            return "🏢 Please mention your building number."

    # 📱 Step 4: Phone number
    if not order_session["phone"]:
        digits = "".join(re.findall(r'\d+', clean_query))
        if len(digits) >= 9:
            order_session["phone"] = digits
            return "📝 Do you have any allergy info or special requests?"
        else:
            return "📱 Please provide your phone number."

    # 📝 Step 5: Dietary notes
    if not order_session["dietary"]:
        keywords = ["no", "without", "allergy", "allergies", "nuts", "gluten", "lactose", "vegan", "extra", "spicy"]
        if any(word in clean_query for word in keywords):
            order_session["dietary"] = query
        else:
            return "📝 Do you have any allergy info or special requests?"

    # ✅ Final confirmation
    items_str = ", ".join(f"{qty} x {item}" for item, qty in order_session["items"])
    confirmed = (
        f"✅ Order confirmed for: {items_str}!\n"
        f"🤚 NYU ID: {order_session['nyu_id']}, 🏢 Building: {order_session['building']}, 📱 Phone: {order_session['phone']}.\n"
    )
    if order_session["dietary"]:
        confirmed += f"📝 Note: {order_session['dietary']}"

    # 🔄 Reset session
    order_session = {
        "items": [],
        "nyu_id": None,
        "building": None,
        "phone": None,
        "dietary": None
    }

    return confirmed


def get_price(item: str) -> str:
    if not item or item == "unknown":
        return "❌ Sorry, I couldn't understand the item you're asking about."

    item = item.strip().lower()

    # Check if item directly matches any leaf-level item with price
    for category, content in menu.menu.items():
        if isinstance(content, dict):
            for subkey, subcontent in content.items():
                # Nested items
                if isinstance(subcontent, dict):
                    for leaf_item, price in subcontent.items():
                        if item in leaf_item.lower():
                            return f"💵 {leaf_item} costs {price:.2f} dirhams."
                # Direct item:price map
                elif isinstance(subcontent, (int, float)):
                    if item in subkey.lower():
                        return f"💵 {subkey} costs {subcontent:.2f} dirhams."
                # Description (skip)
                elif isinstance(subcontent, str):
                    continue

        elif isinstance(content, (int, float)):
            if item in category.lower():
                return f"💵 {category} costs {content:.2f} dirhams."

        elif isinstance(content, list):
            for list_item in content:
                if item in list_item.lower():
                    return f"🧂 {list_item} is available. Please ask for more details."

    # If user queried a whole category (e.g. "acai bowl", "pizza")
    for category, content in menu.menu.items():
        if item in category.lower():
            # Collect all priced entries under this category
            priced_items = []

            if isinstance(content, dict):
                for k, v in content.items():
                    if isinstance(v, (int, float)):
                        priced_items.append((k, v))
                    elif isinstance(v, dict):
                        for subk, subv in v.items():
                            if isinstance(subv, (int, float)):
                                priced_items.append((subk, subv))

            if priced_items:
                msg = f"🧾 Here are some {category} options with prices:\n"
                for name, price in priced_items:
                    msg += f"• {name}: {price:.2f} AED\n"
                return msg.strip()

            return f"📦 {category} is available. Some items may not have prices listed."

    return f"❌ Sorry, {item} is not found in our menu."



# Function dispatcher
FUNCTIONS = {
    "place_order": place_order,
    "check_availability": check_availability,
    "get_price": get_price,
    "clarify_category": clarify_category

}


def parse_args(args_str):
    try:
        tree = ast.parse(f"f({args_str})", mode='eval')
        call = tree.body
        return {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
    except Exception as e:
        raise ValueError(f"❌ Failed to parse arguments: {args_str} → {e}")

def parse_function_call(llm_output: str):
    match = re.match(r'CALL\s+(\w+)\((.*)\)', llm_output.strip(), re.DOTALL)
    if not match:
        raise ValueError(f"Invalid function call format: {llm_output}")
    func_name = match.group(1)
    args_str = match.group(2)
    args = parse_args(args_str)
    return func_name, args

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"📥 {request.method} {request.url}")
    response = await call_next(request)
    print(f"📤 Response status: {response.status_code}")
    return response

@app.post("/mcp")
async def mcp(request: Request):
    data = await request.json()
    prompt = data.get("query", "")
    try:
        func_name, args = parse_function_call(prompt)
        print("🛠️ Parsed function name:", func_name)
        print("🧪 Parsed args:", args)
        print("🧪 Arg types:", {k: type(v) for k, v in args.items()})
        if func_name in FUNCTIONS:
            response = FUNCTIONS[func_name](**args)
            return {"response": response}
        return {"response": f"⚠️ Unknown function: {func_name}"}
    except Exception as e:
        return {"response": f"⚠️ MCP Error: {str(e)}"}

@app.get("/ping")
async def ping():
    return {"status": "MCP server is up"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 MCP server running on http://0.0.0.0:9000")
    uvicorn.run("app:app", host="0.0.0.0", port=9000, reload=True)
