
import requests
import json
import time

def test_sse_connection():
    url = "http://127.0.0.1:8000/sse"
    print(f"Testing connection to {url}...")
    
    try:
        # 1. Start the SSE session with a GET request
        response = requests.get(url, stream=True, timeout=5)
        
        if response.status_code == 200:
            print("✅ Connection Successful (200 OK)")
            print("Client connected via SSE.")
            
            # Read a few lines to see if we get the initial handshake
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    print(f"Received: {decoded}")
                    if "endpoint" in decoded:
                        print("✅ Received Endpoint URL in handshake.")
                        break
        else:
            print(f"❌ Connection Failed with Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_sse_connection()
