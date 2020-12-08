import requests


def find_the_smartest_hero(heroes):
    with open("token.txt", encoding='utf-8') as f:
        number = f.read()


    BASE_URL = 'https://superheroapi.com/api/' + number


    heroes_int = []
    for hero in heroes:
        id_response = requests.get(BASE_URL + '/search/' + hero)
        search_results = id_response.json()["results"]
        for result in search_results:
            if result["name"] == hero:
                heroes_int.append(result["powerstats"]["intelligence"])
                sorted_heroes_int = sorted(heroes_int)
                if result["powerstats"]["intelligence"] == sorted_heroes_int[0]:
                    max_int = sorted_heroes_int[0]
                    smartest_hero = result["name"]
    return f'Самый умный супергерой - {smartest_hero} с интеллектом {max_int}'


print(find_the_smartest_hero(['Hulk', 'Captain America', 'Thanos']))