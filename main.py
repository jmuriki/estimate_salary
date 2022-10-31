import requests

from pprint import pprint


def main():
    url = "https://api.hh.ru/vacancies"
    languages = ["Java Script", "Java", "Python", "Ruby", "PHP", "C++", "C#", "C", "Go"]
    number_of_vacancies = {}
    for language in languages:
        params = {
            "text": f"программист {language}",
            "area": "1",
            "search_period": ""
        }
        response = requests.get(url, params=params)
        response.raise_for_status
        api_response = response.json()
        number_of_vacancies[language] = api_response["found"]
    pprint(number_of_vacancies)


if __name__ == "__main__":
    main()
