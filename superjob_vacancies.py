import os
import requests

from dotenv import load_dotenv


def get_vacancies(secret_key):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": secret_key,
    }
    params = {
        "keyword": "программист",
        "t": 4,
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status
    api_response = response.json()
    for object_ in api_response["objects"]:
        print(object_["profession"], object_["town"]["title"])


def main():
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    get_vacancies(secret_key)


if __name__ == "__main__":
    main()