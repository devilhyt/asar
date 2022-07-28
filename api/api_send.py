import requests
import json

url = 'http://localhost:5005/webhooks/rest/webhook'
data = {'sender': 'test_user', 'message' : 'Hi there!'}

if __name__ == "__main__":
    response = requests.post(url, data = json.dumps(data))
    print(response.text)