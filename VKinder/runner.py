from application.vk_bot import Bot

token = ''  # ключ для бота
login = ''  # мобильный телефон, привязанный к логину ВК
password = ''  # пароль ВК

# инициализация и создание базы данных - в database.py

if __name__ == '__main__':

    VKinder = Bot(token, login, password)
    VKinder.run()
