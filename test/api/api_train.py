import requests
import yaml

url = 'http://localhost:5005/model/train'
params = {"save_to_default_model_directory": "true", "force_training": "true"}

if __name__ == "__main__":
    # load yaml
    with open('api/test.yml', 'r') as f:
        data = yaml.safe_load(f)
    response = requests.post(url=url, params=params, data=yaml.dump(data))

    # print response headers
    print(response.headers)

    # save model
    if response.status_code == 200:
        filename = response.headers['filename']

        with open(f'api/{filename}', 'wb') as f:
            f.write(response.content)
