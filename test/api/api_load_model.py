import requests
import json

url = 'http://localhost:5005/model'

if __name__ == "__main__":

    data = {
        "model_file": "/app/models/20220414-080557-noisy-panel.tar.gz"
    }
    response = requests.put(url=url, data=json.dumps(data))

    # print response headers
    print(response.headers)
    print(response.text)
