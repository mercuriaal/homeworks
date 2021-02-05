from application.people import get_employees
from application.salary import calculate_salary
from datetime import datetime


def run_app():
    print(datetime.now())
    calculate_salary()
    get_employees()


if __name__ == '__main__':
    run_app()