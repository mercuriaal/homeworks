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
    characters = await asyncio.gather(*character_tasks)

    for character in characters:
        if character.get('detail') is None:
            new_tasks = []
            char_id = int(character['url'].split('/')[-2])

            films = asyncio.create_task(get_names(character, 'films', 'title'))
            new_tasks.append(films)
            homeworld = asyncio.create_task(get_homeworld(character))
            new_tasks.append(homeworld)
            species = asyncio.create_task(get_names(character, 'species', 'name'))
            new_tasks.append(species)
            starships = asyncio.create_task(get_names(character, 'starships', 'name'))
            new_tasks.append(starships)
            vehicles = asyncio.create_task(get_names(character, 'vehicles', 'name'))
            new_tasks.append(vehicles)

            names = await asyncio.gather(*new_tasks)

            complete_character = Character(char_id=char_id, birth_year=character['birth_year'],
                                           eye_color=character['eye_color'], films=names[0], gender=character['gender'],
                                           hair_color=character['hair_color'], height=character['height'],
                                           homeworld=names[1], mass=character['mass'], name=character['name'],
                                           skin_color=character['skin_color'], species=names[2], starships=names[3],
                                           vehicles=names[4])

            session.add(complete_character)
            await session.commit()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
