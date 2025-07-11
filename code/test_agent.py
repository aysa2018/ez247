import requests
import json

def call_llm(prompt):
    system_prompt = """
You are a backend API agent. You must ONLY respond with valid Python-style function calls using keyword arguments.

🛑 NEVER include emojis, extra words, or explanations in your output.
✅ Your output MUST look exactly like this:
CALL get_price(item="Chicken Teriyaki")

Available functions:

- place_order(item=..., quantity=...)
  → Place a food order.

- check_availability(item=...)
  → Check if a category or item is available.

- get_price(item=...)
  → Get the price of a specific item or flavor.

- clarify_category(category=...)
  → Ask the user what they want from a category like 'pizza' or 'acai bowl'.

Rules:
1. Respond with ONLY ONE function call:
    CALL function_name(param=value, ...)
    - Never return more than one function call.
    - Never add text, emojis, or explanation.
2. Always use `CALL function_name(param1=value1, param2=value2)` format.
3. All parameters must use keyword syntax.
4. Do not include ✔, ❌, ✅, or any sentence outside the function call.
5. If someone asks about a category like 'pizzas', call:
   CALL check_availability(item="pizza")
   Then: CALL clarify_category(category="pizza") if available.
6. Only call `place_order()` after the user specifies a **flavor or item**, not just a category.
7. Output must only be the function call. Nothing before or after.

❗You must output a SINGLE line that starts with `CALL` and contains no additional commentary.

"""

    try:
        res = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "mistral",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": True
            },
            stream=True
        )

        content_parts = []
        for line in res.iter_lines(decode_unicode=True):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    content_parts.append(data["message"]["content"])
            except json.JSONDecodeError:
                continue

        full_content = ''.join(content_parts).strip()
        # print("🧠 LLM Output:", full_content)
        return full_content

    except Exception as e:
        return f"⚠️ Ollama Error: {e}"

def call_mcp(prompt):
    try:
        res = requests.post("http://localhost:9000/mcp", json={"query": prompt})
        data = res.json()
        return data.get("response", "⚠️ No 'response' key in MCP output.")
    except Exception as e:
        return f"⚠️ MCP Error: {e}"

if __name__ == "__main__":
    user_input = input("🧑 You: ")
    llm_output = call_llm(user_input)
    print("🧠 LLM Output:", llm_output)
    
    if not llm_output:
        exit(1)

    result = call_mcp(llm_output)
    print("🤖 Final response:", result)
