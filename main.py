import requests

from pprint import pprint


def predict_rub_salary(vacancy):
    salary = vacancy["salary"]
    if not salary:
        return None
    elif salary["currency"] != "RUR":
        return None
    elif salary["from"] and salary["to"]:
        return (salary["from"] + salary["to"]) / 2
    elif salary["from"] and not salary["to"]:
        return salary["from"] * 1.2
    elif not salary["from"] and salary["to"]:
        return salary["to"] * 0.8


def main():
    url = "https://api.hh.ru/vacancies"
    languages = [
        "Java Script",
        "Java",
        "Python",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "C",
        "Go"
    ]
    vacancies_stats = {}
    for language in languages:
        vacancies_stats[language] = {}
        params = {
            "text": f"программист {language}",
            "area": 1
        }
        page = 0
        pages = 1
        vacancies = []
        while page < pages:
            params["page"] = page
            response = requests.get(url, params=params)
            response.raise_for_status
            api_response = response.json()
            vacancies.extend(api_response["items"])
            page += 1
            pages = api_response["pages"]
        rub_salaries = [
            i for i in [
                predict_rub_salary(vacancy)
                for vacancy in vacancies
                ]
            if i is not None
        ]
        vacancies_stats[language]["vacancies_found"] = api_response["found"]
        vacancies_stats[language]["vacancies_processed"] = len(rub_salaries)
        vacancies_stats[language]["average_salary"] = int(
            sum(s for s in rub_salaries) /
            vacancies_stats[language]["vacancies_processed"]
        )
    pprint(vacancies_stats)


if __name__ == "__main__":
    main()
