from app import place_order, order_session

# STEP 1: Add item + quantity
print("\n🧑 You: I want to order 2 pizzas")
response = place_order("pizza", 2)
print("🤖", response)

# STEP 2: Add NYU ID
print("\n🧑 You: 12345678")
order_session["nyu_id"] = "12345678"
response = place_order("pizza", 2)
print("🤖", response)

# STEP 3: Add Building
print("\n🧑 You: I live in A1C")
order_session["building"] = "A1C"
response = place_order("pizza", 2)
print("🤖", response)

# STEP 4: Add Phone
print("\n🧑 You: My phone number is 0561234567")
order_session["phone"] = "0534567"
response = place_order("pizza", 2)
print("🤖", response)

# STEP 5: Add Dietary Notes
print("\n🧑 You: I'm allergic to nuts")
order_session["dietary"] = "I'm allergic to nuts"
response = place_order("pizza", 2)
print("🤖", response)
