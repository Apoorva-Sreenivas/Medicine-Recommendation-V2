import requests

def query_colab_llm(prompt):
    url = "https://831c-34-19-27-184.ngrok-free.app/llm"  # Your actual endpoint
    try:
        response = requests.post(url, json={"prompt": prompt}, timeout=10)
        print("Status code:", response.status_code)
        print("Raw response:", response.text)
        return response.json().get("response")
    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", e)
        return None
    except ValueError as e:
        print("❌ JSON decode failed:", e)
        return None

if __name__ == "__main__":
    result = query_colab_llm("test from VS Code")
    print("✅ Response:", result)
