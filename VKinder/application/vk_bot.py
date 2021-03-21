from random import randrange
import time
import json

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.execute import VkFunction
from application.database import Session, AppUser, Results


class Bot:

    def __init__(self, bot_key, vk_login, vk_password):

        self.vk_bot = vk_api.VkApi(token=bot_key)
        self.vk_user = vk_api.VkApi(login=vk_login, password=vk_password)
        self.vk_user.auth()
        self.session = Session()

        self.searching_key = VkKeyboard(one_time=True)
        self.searching_key.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
        self.searching_key.add_line()
        self.searching_key.add_button('Посмотреть избранное')

        self.main_keys = VkKeyboard()
        self.main_keys.add_button('Далее', color=VkKeyboardColor.PRIMARY)
        self.main_keys.add_button('Стоп', color=VkKeyboardColor.PRIMARY)
        self.main_keys.add_line()
        self.main_keys.add_button('В избранное')
        self.main_keys.add_button('В черный список')
        self.main_keys.add_line()
        self.main_keys.add_button('Лайк первому фото', color=VkKeyboardColor.POSITIVE)
        self.main_keys.add_button('Дизлайк первому фото', color=VkKeyboardColor.NEGATIVE)
        self.main_keys.add_line()
        self.main_keys.add_button('Лайк второму фото', color=VkKeyboardColor.POSITIVE)
        self.main_keys.add_button('Дизлайк второму фото', color=VkKeyboardColor.NEGATIVE)
        self.main_keys.add_line()
        self.main_keys.add_button('Лайк третьему фото', color=VkKeyboardColor.POSITIVE)
        self.main_keys.add_button('Дизлайк третьему фото', color=VkKeyboardColor.NEGATIVE)

    def check_data(self, user_id):

        existence = self.session.query(AppUser.id).filter(AppUser.vk_id == user_id).scalar() is not None
        if not existence:
            raw_data = self.vk_user.method('users.get', {'user_ids': user_id, 'fields': ['bdate, sex, city']})
            data = raw_data[0]
            if data.get('city') is not None:
                user = AppUser(vk_id=user_id, birth_year=int(data['bdate'].split('.')[2]), gender=data['sex'],
                               city_id=data['city']['id'])
            else:
                user = AppUser(vk_id=user_id, birth_year=int(data['bdate'].split('.')[2]), gender=data['sex'])
            self.session.add(user)
            self.session.commit()

        city_existence = self.session.query(AppUser.city_id).filter(AppUser.vk_id == user_id).scalar() is not None
        if not city_existence:
            warning = 'Для успешного поиска людей мне необходимо знать город, в котором Вы проживаете.\n' \
                      'Для этого напишите сообщение в формате:\n "Город - [ваш город]"'
            self.send_text_msg(user_id, warning)

        return city_existence

    def add_city(self, user_text, user_id):

        country_response = self.vk_user.method('database.getCountries', {'count': '1'})
        country_id = country_response['items'][0]['id']

        line = user_text.split(' ')
        city_response = self.vk_user.method('database.getCities', {'country_id': country_id, 'count': '1', 'q': line})
        city_id = city_response['items'][0]['id']

        self.session.query(AppUser).filter(AppUser.vk_id == user_id).update({"city_id": city_id})
        self.session.commit()

    def send_text_msg(self, user_id, message):

        params = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}
        self.vk_bot.method('messages.send', params)

    def send_keyboard(self, user_id, message, keyboard):

        params = {'user_id': user_id, 'message': message, 'keyboard': keyboard,
                  'random_id': randrange(10 ** 7)}
        self.vk_bot.method('messages.send', params)

    def search_people(self, user_id):

        if self.check_data(user_id):
            age = int(time.ctime().split(' ')[4]) - \
                  self.session.query(AppUser.birth_year).filter(AppUser.vk_id == user_id).scalar()

            if self.session.query(AppUser.gender).filter(AppUser.vk_id == user_id).scalar() == 1:
                gender = 2
            else:
                gender = 1

            city_id = self.session.query(AppUser.city_id).filter(AppUser.vk_id == user_id).scalar()
            age_from = age - 2
            age_to = age + 2

            massive_search = VkFunction(args=('city_id', 'gender', 'age_from', 'age_to'), code=''' 
            var birth_month = 1;
            var relation = 1;
            var people = API.users.search({'city': (%(city_id)s), 'sex': (%(gender)s), 'age_from': (%(age_from)s), 
            'age_to': (%(age_to)s), 'count': 1000, 'birth_month': birth_month, 'status': relation,
            'fields': ['interests', 'music', 'tv', 'books', 'games', 'common_count', 'bdate']}).items;
            while (birth_month < 12) {
            birth_month = birth_month + 1;
            people = people + API.users.search({'city': (%(city_id)s), 'sex': (%(gender)s), 'age_from': (%(age_from)s), 
            'age_to': (%(age_to)s), 'count': 1000, 'birth_month': birth_month, 'status': relation,
            'fields': ['interests', 'music', 'tv', 'books', 'games', 'common_count', 'bdate']}).items;
            };
            relation = 6;
            birth_month = 1;
            while (birth_month < 12) {
            birth_month = birth_month + 1;
            people = people + API.users.search({'city': (%(city_id)s), 'sex': (%(gender)s), 'age_from': (%(age_from)s), 
            'age_to': (%(age_to)s), 'count': 1000, 'birth_month': birth_month, 'status': relation,
            'fields': ['interests', 'music', 'tv', 'books', 'games', 'common_count', 'bdate']}).items;
            };
            return people;
            ''')

            response = self.vk_user.method('users.get', {'user_ids': user_id, 'fields':
                                           ['interests, music, tv, books, games, bdate']})
            user_data = response[0]
            user_interests = user_data.get('interests')
            user_music = user_data.get('music')
            user_tv = user_data.get('tv')
            user_books = user_data.get('books')
            user_games = user_data.get('games')
            user_birth_year = user_data.get('bdate')

            data = massive_search(self.vk_user, city_id, gender, age_from, age_to)
            for result in data:
                result['value'] = 0

                interests = result.get('interests')
                music = result.get('music')
                tv = result.get('tv')
                books = result.get('books')
                games = result.get('games')
                birth_year = result.get('bdate')

                if result['common_count'] > 0:
                    result['value'] += 5

                if birth_year is not None and len(birth_year.split('.')) == 3 \
                        and user_birth_year is not None and len(user_birth_year.split('.')) == 3:
                    if user_birth_year == birth_year:
                        result['value'] += 3

                if interests is not None and interests != '' and user_interests is not None and user_interests != '':
                    for interest in user_interests.lower().split(','):
                        if interest in interests.lower().split(','):
                            result['value'] += 3

                if music is not None and music != '' and user_music is not None and user_music != '':
                    for instance in user_music.lower().split(','):
                        if instance in music.lower().split(','):
                            result['value'] += 1

                if tv is not None and tv != '' and user_tv is not None and user_tv != '':
                    for instance in user_tv.lower().split(','):
                        if instance in tv.lower().split(','):
                            result['value'] += 1

                if books is not None and books != '' and user_books is not None and user_books != '':
                    for book in user_books.lower().split(','):
                        if book in books.lower().split(','):
                            result['value'] += 1

                if games is not None and games != '' and user_games is not None and user_games != '':
                    for game in user_games.lower().split(','):
                        if game in games.lower().split(','):
                            result['value'] += 1

            sorted_data = sorted(data, key=lambda x: x['value'], reverse=True)

            return sorted_data

    def pick(self, user_id):

        raw_data = self.search_people(user_id)
        final_result = []

        user_db_id = self.session.query(AppUser.id).filter(AppUser.vk_id == user_id).scalar()
        user = self.session.query(AppUser).get(user_db_id)

        for person in raw_data:

            if not person['is_closed']:
                db_presence = self.session.query(Results.id).join(Results.users).\
                    filter(AppUser.vk_id == user_id, Results.result_vk_id == int(person['id'])).scalar()

                db_black_list = self.session.query(Results.black_list).join(Results.users).\
                    filter(AppUser.vk_id == user_id, Results.result_vk_id == int(person['id'])).scalar()

                if db_presence is None and db_black_list is not True:

                    person_info = {}
                    offset = 0
                    all_photos = []

                    while True:
                        photos = self.vk_user.method('photos.get', {'owner_id': person['id'], 'album_id': 'profile',
                                                                    'extended': '1', 'count': '1000',
                                                                    'offset': offset, 'v': '5.130'})
                        offset += 1000
                        if len(photos["items"]) == 0:
                            break
                        for photo in photos['items']:
                            all_photos.append(photo)

                    sorted_photos = sorted(all_photos,
                                           key=lambda x: x['likes']['count'] + x['comments']['count'], reverse=True)
                    person_info['url'] = 'https://vk.com/id' + str(person['id'])
                    if len(sorted_photos) >= 3:
                        person_info['1'] = sorted_photos[0]['id']
                        person_info['2'] = sorted_photos[1]['id']
                        person_info['3'] = sorted_photos[2]['id']
                    elif len(sorted_photos) == 2:
                        person_info['1'] = sorted_photos[0]['id']
                        person_info['2'] = sorted_photos[1]['id']
                    elif len(sorted_photos) == 1:
                        person_info['1'] = sorted_photos[0]['id']
                    final_result.append(person_info)

                    if person_info.get('1') is not None:
                        result = Results(result_vk_id=int(person['id']), url=person_info['url'],
                                         photo_id=sorted_photos[0]['id'])
                        self.session.add(result)
                        result.users.append(user)
                        self.session.commit()
                    else:
                        result = Results(result_vk_id=int(person['id']), url=person_info['url'])
                        self.session.add(result)
                        result.users.append(user)
                        self.session.commit()
                    if len(final_result) == 10:
                        break

        with open("application/created files/pairs.json", "w", encoding='UTF-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=4)

    def send_result(self, user_id):

        with open("application/created files/pairs.json", "r", encoding='UTF-8') as f:
            results = json.load(f)

        if len(results) == 0:
            self.send_text_msg(user_id, 'Результаты закончились, нажмите "Стоп"')

            return

        result = results.pop(0)
        with open("application/created files/pairs.json", "w", encoding='UTF-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        with open("application/created files/last_result.json", "w", encoding='UTF-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        page_id = result.get('url')[17:]
        first_photo = 'photo' + page_id + '_' + str(result.get("1"))
        second_photo = 'photo' + page_id + '_' + str(result.get("2"))
        third_photo = 'photo' + page_id + '_' + str(result.get("3"))
        url = result["url"]

        params = {'user_id': user_id, 'message': url, 'attachment': f'{first_photo},{second_photo},{third_photo},',
                  'random_id': randrange(10 ** 7)}
        self.vk_bot.method('messages.send', params)

    def like(self, user_id, photo_number: str, remove=False):

        with open("application/created files/last_result.json", "r", encoding='UTF-8') as f:
            info = json.load(f)

        photo_id = info.get(photo_number)
        page_id = info.get('url')[17:]
        if not remove:
            if photo_id is not None:
                self.vk_user.method('likes.add', {'type': 'photo', 'owner_id': page_id, 'item_id': photo_id})
            else:
                self.send_text_msg(user_id, 'Фотографии не существует')
                self.main_keys.get_keyboard()
        else:
            if photo_id is not None:
                self.vk_user.method('likes.delete', {'type': 'photo', 'owner_id': page_id, 'item_id': photo_id})
            else:
                self.send_text_msg(user_id, 'Фотографии не существует')
                self.main_keys.get_keyboard()

    def set_result(self, user_id, favorite=None, black_list=None):

        with open("application/created files/last_result.json", "r", encoding='UTF-8') as f:
            info = json.load(f)

        favorite_url = info.get('url')
        favorite_id = self.session.query(Results.id).join(Results.users). \
            filter(AppUser.vk_id == user_id, Results.url == favorite_url).scalar()

        if favorite:
            self.session.query(Results).filter(Results.id == favorite_id).update({'favorite': True})
            self.session.commit()
            self.send_text_msg(user_id, 'Страница добавлена в избранные')
            self.main_keys.get_keyboard()

        if black_list:
            self.session.query(Results).filter(Results.id == favorite_id).update({'black_list': True})
            self.session.commit()
            self.send_text_msg(user_id, 'Страница добавлена в черный список')
            self.main_keys.get_keyboard()

    def show_favorites(self, user_id):

        favorites = self.session.query(Results).join(Results.users). \
                                            filter(AppUser.vk_id == user_id, Results.favorite == True).all()

        if favorites is not None:
            for favorite in favorites:

                photo = 'photo' + favorite.url[17:] + '_' + str(favorite.photo_id)
                params = {'user_id': user_id, 'message': favorite.url, 'attachment': f'{photo}',
                          'random_id': randrange(10 ** 7)}
                self.vk_bot.method('messages.send', params)
                self.searching_key.get_keyboard()
        else:
            self.send_text_msg(user_id, 'Список пуст')
            self.searching_key.get_keyboard()

    def run(self):

        longpoll = VkLongPoll(self.vk_bot)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text

                    if "Город - " in request:
                        self.add_city(request, event.user_id)
                        self.send_keyboard(event.user_id, 'Сделано! Город изменён.', self.searching_key.get_keyboard())

                    elif request == "Поиск":
                        self.send_text_msg(event.user_id, 'Секундочку...')
                        self.check_data(event.user_id)
                        self.pick(event.user_id)
                        self.send_keyboard(event.user_id, 'Вот что я нашёл:', self.main_keys.get_keyboard())
                        self.send_result(event.user_id)

                    elif request == 'Далее':
                        self.send_result(event.user_id)

                    elif request == 'Стоп':
                        self.send_keyboard(event.user_id, 'Текущий поиск завершен', VkKeyboard.get_empty_keyboard())
                        self.send_keyboard(event.user_id, 'Продолжим', self.searching_key.get_keyboard())

                    elif request == 'В избранное':
                        self.set_result(event.user_id, favorite=True)

                    elif request == 'В черный список':
                        self.set_result(event.user_id, black_list=True)

                    elif request == 'Посмотреть избранное':
                        self.show_favorites(event.user_id)

                    elif request == 'Лайк первому фото':
                        self.like(event.user_id, '1')
                        self.send_text_msg(event.user_id, 'Поставлен лайк первой фотографии')

                    elif request == 'Лайк второму фото':
                        self.like(event.user_id, '2')
                        self.send_text_msg(event.user_id, 'Поставлен лайк второй фотографии')

                    elif request == 'Лайк третьему фото':
                        self.like(event.user_id, '3')
                        self.send_text_msg(event.user_id, 'Поставлен лайк третьей фотографии')

                    elif request == 'Дизлайк первому фото':
                        self.like(event.user_id, '1', remove=True)
                        self.send_text_msg(event.user_id, 'Убран лайк первой фотографии')

                    elif request == 'Дизлайк второму фото':
                        self.like(event.user_id, '2', remove=True)
                        self.send_text_msg(event.user_id, 'Убран лайк второй фотографии')

                    elif request == 'Дизлайк третьему фото':
                        self.like(event.user_id, '3', remove=True)
                        self.send_text_msg(event.user_id, 'Убран лайк третьё фотографии')

                    else:
                        self.send_keyboard(event.user_id, 'Для начала поиска людей жмите кнопку "Поиск".\n'
                                                          'Бот пришлёт вам результат из 10 или менее человек.\n'
                                                          'Также боту можно уточнить город, в котором вы хотите найти'
                                                          'пару командой "Город - [Ваш город]"',
                                                          self.searching_key.get_keyboard())
