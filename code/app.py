from fastapi import FastAPI, Request
import re
from typing import Optional
from typing import Callable


import ast


from functions import check_availability as legacy_check_availability
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
   "dietary": None
}




# @app.post("/mcp")
# async def handle_mcp(request: Request):
#    data = await request.json()
#    query = data.get("query", "").lower().strip()


#    print(f"👉 [MCP Received] {query}")


#    if any(word in query for word in ["menu", "what do you have", "show"]):
#        items = menu.list_items()
#        return {"response": "📋 Our menu includes: " + ", ".join(items)}


#    if any(word in query for word in ["available", "have", "sell", "serve", "carry"]):
#        item = extract_item(query)
#        return {"response": check_availability(item)}


#    if order_session["items"] or any(word in query for word in ["order", "get", "want", "buy"]):
#        return {"response": place_order(query)}




#    return {"response": "❓ I didn't understand. Try asking about availability or placing an order."}


def extract_items_and_quantities(query: str) -> list[tuple[str, int]]:
   spoken_numbers = {
       "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
       "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9
   }


   menu_items = menu.list_items()
   words = query.lower().split()
   tokens = []
   i = 0
   while i < len(words):
       qty = 1
       if words[i] in spoken_numbers:
           qty = spoken_numbers[words[i]]
           i += 1


       name = []
       while i < len(words) and words[i] not in spoken_numbers:
           name.append(words[i])
           i += 1


       item_candidate = " ".join(name).strip()
       for menu_item in menu_items:
           if item_candidate in menu_item.lower():
               tokens.append((menu_item, qty))
               break


   return tokens


def extract_item(query: str) -> str:
   query = query.lower().replace("&", "and")
   query = re.sub(r'[^\w\s]', '', query)
   items = menu.list_items()
   for item in items:
       norm_item = re.sub(r'[^\w\s]', '', item.lower().replace("&", "and"))
       if norm_item in query:
           return item
   for category in menu.menu.keys():
       if category.lower() in query:
           return category
   return "unknown"


def check_availability(item: str) -> str:
   if not item or item == "unknown":
       return "❌ Sorry, that item wasn't understood."
   if menu.is_available(item):
       price = menu.get_price(item)
       return (
           f"✅ Yes, {item} is available at {price:.2f} dirhams."
           if price is not None else
           f"✅ Yes, we have {item}. Please ask for specific options."
       )
   return f"❌ Sorry, {item} is not on the menu."


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


   if result in VALID_BUILDINGS:
       return result
   return ""


VALID_BUILDINGS = {
   "A1A", "A1B", "A1C", "A2A", "A2B", "A2C", "A3", "A4",
   "A5A", "A5B", "A5C", "A6A", "A6B", "A6C", "C1", "C2", "C3"
}


# def place_order(query: str) -> str:
#    global order_session
#    clean_query = re.sub(r'[^\w\s#]', '', query.lower())


#    if not order_session["items"]:
#    # Extract everything after "i want to order" or similar
#        match = re.search(r"(?:i\s*want\s*to\s*order|order|get|buy)\s+(.*)", query)
#        item_text = match.group(1).strip() if match else query
#        matched_item = extract_item(item_text)
#        if menu.is_available(matched_item):
#            order_session["items"].append((matched_item, 1))
#            return "📎 Please say the 8 digits of your NYU ID after the letter N "
#        else:
#            return "🛒 What would you like to order?"




#    if not order_session["nyu_id"]:
#        digits = "".join(re.findall(r'\d+', clean_query))
#        if len(digits) == 8:
#            order_session["nyu_id"] = "N" + digits
#        else:
#            return "📎 Please say the 8 digits of your NYU ID after the letter N."


#    if not order_session["building"]:
#        building = normalize_building_input(clean_query)
#        if building in VALID_BUILDINGS:
#            order_session["building"] = building
#        else:
#            return "🏢 Please mention your building number."


#    if not order_session["phone"]:
#        digits = "".join(re.findall(r'\d+', clean_query))
#        if len(digits) >= 9:
#            order_session["phone"] = digits
#            return "📝 Do you have any allergy info or special requests?"
#        else:
#            return "📱 Please provide your phone number."


#    if not order_session["dietary"]:
#        keywords = ["no", "without", "allergy", "allergies", "nuts", "gluten", "lactose", "vegan", "extra", "spicy"]
#        if any(word in clean_query for word in keywords):
#            order_session["dietary"] = query
#        else:
#            return "📝 Do you have any allergy info or special requests?"


#    items_str = ", ".join(f"{qty} x {item}" for item, qty in order_session["items"])
#    confirmed = (
#        f"✅ Order confirmed for: {items_str}!\n"
#        f"🆔 NYU ID: {order_session['nyu_id']}, 🏢 Building: {order_session['building']}, 📱 Phone: {order_session['phone']}.\n"
#    )
#    if order_session["dietary"]:
#        confirmed += f"📝 Note: {order_session['dietary']}"


#    order_session = {
#        "items": [],
#        "nyu_id": None,
#        "building": None,
#        "phone": None,
#        "dietary": None
#    }
#    return confirmed
def place_order(item: str, quantity: int):
    return f"✅ Order placed: {quantity} x {item}"

FUNCTIONS = {
    "place_order": place_order,
    "check_availability": check_availability
}


def parse_function_call(prompt: str):
    match = re.match(r"CALL\s+(\w+)\((.*)\)", prompt.strip())
    if not match:
        return None, {}

    func_name = match.group(1)
    args_str = match.group(2)

    try:
        args = {}
        # Match key=value pairs, allowing quotes or integers
        arg_pattern = re.findall(r'(\w+)\s*=\s*(\".*?\"|\'.*?\'|\d+)', args_str)
        for key, value in arg_pattern:
            if value.startswith(("'", '"')):
                args[key] = value.strip('"\'')  # remove quotes
            else:
                args[key] = int(value)  # convert numbers
        return func_name, args
    except Exception as e:
        print("⚠️ Error parsing arguments:", e)
        return func_name, {}


@app.post("/mcp")
async def mcp(request: Request):
    data = await request.json()
    prompt = data.get("query", "")

    func_name, args = parse_function_call(prompt)
    print("🛠️ Parsed function name:", func_name)
    print("🧪 Parsed args:", args)
    print("🧪 Arg types:", {k: type(v) for k, v in args.items()})


    if func_name in FUNCTIONS:
        try:
            # ✅ Safely call with keyword arguments
            response = FUNCTIONS[func_name](**args)
            return {"response": response}
        except Exception as e:
            return {"response": f"⚠️ Error: {str(e)}"}
    
    # fallback if not a function call
    return {"response": f"🤖 Echo: {prompt}"}


@app.get("/ping")
async def ping():
   return {"status": "MCP server is up"}


if __name__ == "__main__":
   import uvicorn
   print("🚀 MCP server running on http://0.0.0.0:9000")
   uvicorn.run("app:app", host="0.0.0.0", port=9000, reload=True)
#    llm_output = call_llm("Can I get 2 tacos?")
#    print("🧠 LLM Output:", llm_output)
#    mcp_result = call_mcp(llm_output)
#    print("✅ Final result:", mcp_result)




