import ai_core
import json

def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    key = config.get("GOOGLE_API_KEY")
    print(f"Testing API key: {key}")
    try:
        res = ai_core.run_lightweight_test(key)
        print(f"Success! Response: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
