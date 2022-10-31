import requests

from pprint import pprint


def predict_rub_salary(vacancy):
    salary = vacancy["salary"]
    if salary and salary["currency"] == "RUR":
        if salary["from"] and salary["to"]:
            return (salary["from"] + salary["to"]) / 2
        elif salary["from"] and not salary["to"]:
            return salary["from"] * 1.2
        elif not salary["from"] and salary["to"]:
            return salary["to"] * 0.8
    else:
        return None


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
        params = {
            "text": f"программист {language}",
            "area": "1",
            "search_period": ""
        }
        response = requests.get(url, params=params)
        response.raise_for_status
        api_response = response.json()
        rub_salaries = [
            i for i in [predict_rub_salary(item)
            for item in api_response["items"]]
            if i is not None
        ]
        vacancies_stats[language] = {}
        # pprint(vacancies_stats)
        vacancies_stats[language]["vacancies_found"] = api_response["found"]
        vacancies_stats[language]["vacancies_processed"] = len(rub_salaries)
        vacancies_stats[language]["average_salary"] = int(
            sum(s for s in rub_salaries) /
            vacancies_stats[language]["vacancies_processed"]
            )        

    pprint(vacancies_stats)


if __name__ == "__main__":
    main()
