import os
import requests

from pprint import pprint
from dotenv import load_dotenv


def predict_salary(salary_from, salary_to):
    return (salary_from + salary_to) / 2


def predict_rub_salary_for_hh(vacancy):
    salary = vacancy["salary"]
    if not salary:
        return None
    elif "RUR" not in salary["currency"]:
        return None
    elif salary["from"] and salary["to"]:
        return predict_salary(salary["from"], salary["to"])
    elif salary["from"] and not salary["to"]:
        return salary["from"] * 1.2
    elif not salary["from"] and salary["to"]:
        return salary["to"] * 0.8


def predict_rub_salary_for_sj(vacancy):
    if "rub" not in vacancy["currency"]:
        return None
    elif vacancy["payment_from"] and vacancy["payment_to"]:
        return predict_salary(vacancy["payment_from"], vacancy["payment_to"])
    elif vacancy["payment_from"] and not vacancy["payment_to"]:
        return vacancy["payment_from"] * 1.2
    elif not vacancy["payment_from"] and vacancy["payment_to"]:
        return vacancy["payment_to"] * 0.8


def get_hh_vacancies_stats(language, hh_vacancies_stats):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": f"программист {language}",
        "area": 1
    }
    vacancies = []
    hh_vacancies_stats[language] = {}
    page = 0
    pages = 1
    while page < pages:
        params["page"] = page
        response = requests.get(url, params=params)
        response.raise_for_status
        api_response = response.json()
        vacancies.extend(api_response["items"])
        page += 1
        pages = api_response["pages"]
    rub_salaries = [
        s for s in [
            predict_rub_salary_for_hh(vacancy)
            for vacancy in vacancies
            ]
        if s is not None
    ]
    hh_vacancies_stats[language]["vacancies_found"] = api_response["found"]
    hh_vacancies_stats[language]["vacancies_processed"] = len(rub_salaries)
    hh_vacancies_stats[language]["average_salary"] = int(
        sum(s for s in rub_salaries) /
        hh_vacancies_stats[language]["vacancies_processed"]
    )
    return hh_vacancies_stats


def get_sj_vacancies_stats(secret_key, language, sj_vacancies_stats):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": secret_key,
    }
    vacancies = []
    sj_vacancies_stats[language] = {}
    page = 0
    more = True
    while more:
        params = {
            "town": 4,
            "catalogues": 48,
            "keyword": language,
            "page": page,
            "count": 100,
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status
        api_response = response.json()
        more = api_response["more"]
        vacancies.extend(api_response["objects"])
        page += 1
    sj_vacancies_stats[language]["vacancies_found"] = len(vacancies)
    vacancies = [v for v in vacancies if language in v["profession"]]
    rub_salaries = [
        s for s in [
            predict_rub_salary_for_sj(vacancy)
            for vacancy in vacancies
        ]
        if s is not None
    ]
    sj_vacancies_stats[language]["vacancies_processed"] = len(rub_salaries)
    if not sj_vacancies_stats[language]["vacancies_processed"]:
        sj_vacancies_stats[language]["average_salary"] = None 
    else:
        sj_vacancies_stats[language]["average_salary"] = int(
            sum(s for s in rub_salaries) /
            sj_vacancies_stats[language]["vacancies_processed"]
        )
    return sj_vacancies_stats


def main():
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
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
    hh_vacancies_stats = {}
    sj_vacancies_stats = {}
    for language in languages:
        hh_vacancies_stats = get_hh_vacancies_stats(language, hh_vacancies_stats)
        sj_vacancies_stats = get_sj_vacancies_stats(secret_key, language, sj_vacancies_stats)
    pprint(hh_vacancies_stats)
    pprint(sj_vacancies_stats)


if __name__ == "__main__":
    main()
