import os
import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable


def print_as_table(title, headings, stats):
    table_strings = [headings]
    for language, stats_figures in stats.items():
        table_strings.append([
            language,
            stats_figures["vacancies_found"],
            stats_figures["vacancies_processed"],
            stats_figures["average_salary"]
        ])
    ascii_table = AsciiTable(table_strings, title)
    print(ascii_table.table)
    print()


def calc_avg_salary(real_salaries, divisor):
    if divisor:
        average_salary = int(sum(real_salaries) / divisor)
        return average_salary
    else:
        return 0


def get_total_figures(vacancies, real_salaries):
    total_figures = {}
    total_figures["vacancies_found"] = len(vacancies)
    total_figures["vacancies_processed"] = len(real_salaries)
    total_figures["average_salary"] = calc_avg_salary(
        real_salaries,
        total_figures["vacancies_processed"],
    )
    return total_figures


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


def get_hh_vacancies(lang):
    url = "https://api.hh.ru/vacancies"
    moscow_code = 1
    params = {
        "text": f"программист {lang}",
        "area": moscow_code,
    }
    vacancies = []
    page = 0
    pages = 1
    while page < pages:
        params["page"] = page
        response = requests.get(url, params=params)
        response.raise_for_status()
        api_response = response.json()
        vacancies.extend(api_response["items"])
        page += 1
        pages = api_response["pages"]
    return vacancies


def get_sj_vacancies(lang, key):
    url = "https://api.superjob.ru/2.0/vacancies/"
    moscow_code = 4
    it_development_code = 48
    vacancies_per_page = 100
    headers = {
        "X-Api-App-Id": key,
    }
    vacancies = []
    page = 0
    more_pages = True
    while more_pages:
        params = {
            "town": moscow_code,
            "catalogues": it_development_code,
            "keyword": lang,
            "page": page,
            "count": vacancies_per_page,
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        api_response = response.json()
        vacancies.extend(api_response["objects"])
        page += 1
        more_pages = api_response["more"]
    return vacancies


def get_hh_stats(lang):
    vacancies = get_hh_vacancies(lang)
    rub_salaries = [
        predict_rub_salary_for_hh(vacancy)
        for vacancy in vacancies
    ]
    real_salaries = [salary for salary in rub_salaries if salary]
    total_figures = get_total_figures(vacancies, real_salaries)
    return total_figures


def get_sj_stats(lang, key):
    vacancies = get_sj_vacancies(lang, key)
    rub_salaries = [
        predict_rub_salary_for_sj(vacancy)
        for vacancy in vacancies
    ]
    real_salaries = [salary for salary in rub_salaries if salary]
    total_figures = get_total_figures(vacancies, real_salaries)
    return total_figures


def main():
    load_dotenv()
    sj_key = os.getenv("SJ_SECRET_KEY")
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
        "1С",
    ]
    hh_stats = {}
    sj_stats = {}
    for language in languages:
        hh_stats[language] = get_hh_stats(language)
        sj_stats[language] = get_sj_stats(language, sj_key)
    print_as_table("HeadHunter Moscow", headings, hh_stats)
    print_as_table("SuperJob Moscow", headings, sj_stats)


if __name__ == "__main__":
    main()
