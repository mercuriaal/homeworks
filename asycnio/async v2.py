import asyncio
import aiohttp
from models import async_session, Character

BASE_URL = 'https://swapi.dev/api/people/'


async def request(url: str):
    session = aiohttp.ClientSession()
    response = await session.get(url)
    response_json = await response.json(content_type='application/json')
    await session.close()
    return response_json


async def get_homeworld(json: dict):
    response = await request(json['homeworld'])
    return response['name']


async def get_names(json: dict, key: str, name_key: str):
    responses = await asyncio.gather(*[request(url) for url in json[key]])
    names = [response[name_key] for response in responses]
    return ', '.join(names)


async def main():

    session = async_session()

    character_tasks = [asyncio.create_task(request(f'{BASE_URL}/{i}')) for i in range(100)]
    raw_characters = await asyncio.gather(*character_tasks)

    characters = [character for character in raw_characters if character.get('detail') is None]

    film_tasks = [asyncio.create_task(get_names(character, 'films', 'title')) for character in characters]
    films = await asyncio.gather(*film_tasks)

    homeworld_tasks = [asyncio.create_task(get_homeworld(character)) for character in characters]
    homeworld = await asyncio.gather(*homeworld_tasks)

    species_tasks = [asyncio.create_task(get_names(character, 'species', 'name')) for character in characters]
    species = await asyncio.gather(*species_tasks)

    starships_tasks = [asyncio.create_task(get_names(character, 'starships', 'name')) for character in characters]
    starships = await asyncio.gather(*starships_tasks)

    vehicles_tasks = [asyncio.create_task(get_names(character, 'vehicles', 'name')) for character in characters]
    vehicles = await asyncio.gather(*vehicles_tasks)

    n = 0
    while n < len(characters):
        commit_tasks = []
        model = Character(char_id=int(characters[n]['url'].split('/')[-2]), birth_year=characters[n]['birth_year'],
                          eye_color=characters[n]['eye_color'], films=films[n], gender=characters[n]['gender'],
                          hair_color=characters[n]['hair_color'], height=characters[n]['height'],
                          homeworld=homeworld[n], mass=characters[n]['mass'], name=characters[n]['name'],
                          skin_color=characters[n]['skin_color'], species=species[n], starships=starships[n],
                          vehicles=vehicles[n])

        n += 1
        session.add(model)
        commit = asyncio.create_task(session.commit())
        commit_tasks.append(commit)
        await asyncio.gather(*commit_tasks)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
