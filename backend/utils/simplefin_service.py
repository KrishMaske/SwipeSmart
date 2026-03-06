import requests
import base64

def exchange_setup(setup_token):
    claim_url = base64.b64decode(setup_token).decode('utf-8')
    response = requests.post(claim_url)
    
    if response.status_code == 200:
        return response.text.strip()
    else:
        return {"error": f"Failed to claim setup: {response.status_code} - {response.text}"}

if __name__ == "__main__":
    # Example usage
    setup_token = input("Enter the setup token: ")
    result = exchange_setup(setup_token)
    print(f"access url: {result}")
    response = requests.get(f"{result}/accounts")
    print(response.json())