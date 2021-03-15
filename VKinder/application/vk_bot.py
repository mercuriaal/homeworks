from random import randrange
import time
import json

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from application.database import Session, AppUser, Results


class Bot:

    def __init__(self, bot_key, vk_login, vk_password):
        self.keyboard = VkKeyboard(one_time=False)
        self.vk_bot = vk_api.VkApi(token=bot_key)
        self.vk_user = vk_api.VkApi(login=vk_login, password=vk_password)
        self.vk_user.auth()
        self.session = Session()

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

    def send_text_msg(self, user_id, message, keyboard=False):

        if keyboard:
            params = {'user_id': user_id, 'message': message, 'keyboard': self.add_keyboard(),
                      'random_id': randrange(10 ** 7)}
        else:
            params = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}
        self.vk_bot.method('messages.send', params)

    def add_keyboard(self):

        self.keyboard.add_button(label='Поиск', color=VkKeyboardColor.POSITIVE)
        return self.keyboard.get_keyboard()

    def search_people(self, user_id):

        if self.check_data(user_id):
            age = int(time.ctime().split(' ')[4]) - \
                  self.session.query(AppUser.birth_year).filter(AppUser.vk_id == user_id).scalar()

            if self.session.query(AppUser.gender).filter(AppUser.vk_id == user_id).scalar() == 1:
                gender = 2
            else:
                gender = 1

            city_id = self.session.query(AppUser.city_id).filter(AppUser.vk_id == user_id).scalar()

            search_result = self.vk_user.method('users.search',
                                                {'count': 1000, 'city': city_id, 'age_from': str(age - 2),
                                                 'age_to': str(age + 2), 'sex': gender, 'fields': ['relation']})

            people = [result for result in search_result['items'] if result.get('relation') == 1
                      or result.get('relation') == 6]
            return people

    def pick(self, user_id):

        raw_data = self.search_people(user_id)
        final_result = []

        user_db_id = self.session.query(AppUser.id).filter(AppUser.vk_id == user_id).scalar()
        user = self.session.query(AppUser).get(user_db_id)

        for person in raw_data:

            query = self.session.query(Results.id).join(Results.users).\
                filter(AppUser.vk_id == user_id, Results.result_vk_id == int(person['id'])).scalar()
            if query is None:

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
                    person_info['top1_photo'] = sorted_photos[0]['id']
                    person_info['top2_photo'] = sorted_photos[1]['id']
                    person_info['top3_photo'] = sorted_photos[2]['id']
                elif len(sorted_photos) == 2:
                    person_info['top1_photo'] = sorted_photos[0]['id']
                    person_info['top2_photo'] = sorted_photos[1]['id']
                elif len(sorted_photos) == 1:
                    person_info['top1_photo'] = sorted_photos[0]['id']
                final_result.append(person_info)

                result = Results(result_vk_id=int(person['id']))
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
            self.send_text_msg(user_id, 'В заданном городе больше не осталось подходящих результатов\n'
                                        'Чтобы изменить место поиска, введите команду:\n "Город - [ваш город]"')
            return

        for result in results:

            page_id = result.get('url')[17:]
            first_photo = 'photo' + page_id + '_' + str(result.get("top1_photo"))
            second_photo = 'photo' + page_id + '_' + str(result.get("top2_photo"))
            third_photo = 'photo' + page_id + '_' + str(result.get("top3_photo"))
            url = result["url"]

            params = {'user_id': user_id, 'message': url, 'attachment': f'{first_photo},{second_photo},{third_photo}',
                      'random_id': randrange(10 ** 7)}
            self.vk_bot.method('messages.send', params)

    def run(self):

        longpoll = VkLongPoll(self.vk_bot)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text

                    if request == "Начать":
                        self.send_text_msg(event.user_id,
                                           'Для начала работы людей жмите кнопку "Поиск".', keyboard=True)

                    if "Город - " in request:
                        self.add_city(request, event.user_id)
                        self.send_text_msg(event.user_id, f"Сделано! Город изменён.")

                    elif request == "Поиск":
                        self.send_text_msg(event.user_id, 'Секундочку...')
                        self.check_data(event.user_id)
                        self.pick(event.user_id)
                        self.send_result(event.user_id)
