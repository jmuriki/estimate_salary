import requests

from pprint import pprint


def main():
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": "программист"

    }
    response = requests.get(url, params=params)
    response.raise_for_status
    pprint(response.json())


if __name__ == "__main__":
    main()
