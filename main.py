import requests

from pprint import pprint


def main():
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": "программист",
        "area": "1",
        "search_period": 30
    }
    response = requests.get(url, params=params)
    response.raise_for_status
    api_response = response.json()
    # pprint(response.url)
    # pprint(api_response.keys())
    pprint(api_response["found"])


if __name__ == "__main__":
    main()
