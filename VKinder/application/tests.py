from application.vk_bot import Bot

import unittest
import json


class TestBot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = input('Ключ от бота')
        login = input('Мобильный телефон, привязанный к логину ВК')
        password = input('Пароль ВК')
        cls.user_id = input('id vk, с которым общается бот')
        cls.VKinder = Bot(token, login, password)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_info_check_function(self):
        self.assertIsInstance(self.VKinder.check_data(self.user_id), bool)

    def test_search_function(self):
        self.assertIsInstance(self.VKinder.search_people(self.user_id), list)

    def test_json_file(self):
        self.VKinder.search_people(self.user_id)
        self.VKinder.pick(self.user_id)
        with open("application/created files/pairs.json", "r", encoding='UTF-8') as f:
            results = json.load(f)
        self.assertLessEqual(len(results), 10)
        if len(results) > 0:
            for result in results:
                self.assertIsNotNone(result.get('url'))
                self.assertIsNotNone(result.get('top1_photo'))


if __name__ == '__main__':
    unittest.main()
