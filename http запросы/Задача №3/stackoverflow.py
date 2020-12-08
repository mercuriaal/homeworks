import requests
import time
from datetime import datetime


def get_questions(fromdate, tag="python"):
    from_date = int(datetime.strptime(fromdate, '%d.%m.%Y').timestamp())
    to_date = int(time.time())
    questions_string = ''

    while True:
        response = requests.get("https://api.stackexchange.com/2.2/questions",
                            params={"pagesize": 100, "fromdate": from_date, "todate": to_date, "order": "desc",
                                     "sort": "creation",
                                     "tagged": tag, "site": "stackoverflow"})
        response.raise_for_status()
        time.sleep(0.05)
        questions = response.json()["items"]
        for question in questions:
            to_date = 0
            to_date += question["creation_date"]
            questions_string += question["title"] + '\n'
        if len(questions) == 0:
            break
    return questions_string


print(get_questions('07.12.2020'))