import requests
import json
import re
import ast

# --- STEP 1: Call LLM via Ollama running on localhost ---


def call_llm(prompt):
    import json
    import requests

    system_prompt = """
You are a backend agent that can only respond with function calls.

Available functions:
- place_order(item, quantity): Place a food order
- check_availability(item): Check if an item is available

❗Rules:
- ONLY respond in this format:
  CALL <function_name>(param1=value1, param2=value2)
- NEVER explain or say anything else.
- If you're unsure, guess.
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
                "stream": True  # explicitly ask for streamed chunks
            },
            stream=True  # tell requests to handle stream
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
        print("🧠 LLM Output:", full_content)
        return full_content

    except Exception as e:
        return f"⚠️ Ollama Error: {e}"



# --- STEP 2: Send LLM result to MCP backend ---
def call_mcp(prompt):
    try:
        res = requests.post("http://localhost:9000/mcp", json={"query": prompt})
        data = res.json()
        return data.get("response", "⚠️ No 'response' key in MCP output.")
    except json.JSONDecodeError:
        return f"⚠️ MCP Error: Invalid JSON response: {res.text}"
    except Exception as e:
        return f"⚠️ MCP Error: {str(e)}"

# --- Run test flow ---
if __name__ == "__main__":
    user_input = input("🧑 You: ")
    
    llm_output = call_llm(user_input)
    if not llm_output:
        exit(1)

    result = call_mcp(llm_output)
    print("🤖 Final response:", result)
