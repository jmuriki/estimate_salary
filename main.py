import os
import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable


def print_as_table(title, headings, stats):
    table_data = [headings]
    for key, value in stats.items():
        table_data.append([
            key,
            value["vacancies_found"],
            value["vacancies_processed"],
            value["average_salary"]
        ])
    ascii_table = AsciiTable(table_data, title)
    print(ascii_table.table)
    print()


def calculate_average_salary(salaries, divisor):
    if not divisor:
        return 0
    else:
        average_salary = int(
            sum(s for s in salaries) / divisor
        )
        return average_salary


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


def get_vacancies_stats_from_hh(lang, stats):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": f"программист {lang}",
        "area": 1,
    }
    stats[lang] = {}
    vacancies = []
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
    stats[lang]["vacancies_found"] = api_response["found"]
    stats[lang]["vacancies_processed"] = len(rub_salaries)
    stats[lang]["average_salary"] = calculate_average_salary(
        rub_salaries,
        stats[lang]["vacancies_processed"],
    )
    return stats


def get_vacancies_stats_from_sj(key, lang, stats):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": key,
    }
    stats[lang] = {}
    vacancies = []
    page = 0
    more_pages = True
    while more_pages:
        params = {
            "town": 4,
            "catalogues": 48,
            "keyword": lang,
            "page": page,
            "count": 100,
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status
        api_response = response.json()
        vacancies.extend(api_response["objects"])
        page += 1
        more_pages = api_response["more"]
    rub_salaries = [
        s for s in [
            predict_rub_salary_for_sj(vacancy)
            for vacancy in vacancies
        ]
        if s is not None
    ]
    stats[lang]["vacancies_found"] = len(vacancies)
    stats[lang]["vacancies_processed"] = len(rub_salaries)
    stats[lang]["average_salary"] = calculate_average_salary(
        rub_salaries,
        stats[lang]["vacancies_processed"],
    )
    return stats


def main():
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    headings = [
        "Язык программирования",
        "Вакансий найдено",
        "Ваканcий обработано",
        "Средняя зарплата",
    ]
    languages = [
        "Java Script",
        "Java",
        "Python",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "C",
        "Go",
    ]
    hh_stats = {}
    sj_stats = {}
    for language in languages:
        get_vacancies_stats_from_hh(language, hh_stats)
        get_vacancies_stats_from_sj(secret_key, language, sj_stats)
    print_as_table("HeadHunter Moscow", headings, hh_stats)
    print_as_table("SuperJob Moscow", headings, sj_stats)


if __name__ == "__main__":
    main()
