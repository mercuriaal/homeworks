import requests

with open("token.txt", encoding='utf-8') as f:
    token = f.read()


class User:
    BASE_URL = "https://api.vk.com/method/"

    def __init__(self, user_id=None, version=5.126):
        self.token = token
        self.version = version
        self.params = {"access_token": self.token, "v": self.version}
        if user_id is None:
            self.user_id = requests.get(self.BASE_URL + 'users.get', params=self.params).json()["response"][0]["id"]
        else:
            self.user_id = user_id

    def __str__(self):
        return "https://vk.com/id" + str(self.user_id)

    def __and__(self, other):
        response = requests.get(self.BASE_URL + "friends.getMutual",
                                params={"source_uid": self.user_id, "target_uids": other.user_id,
                                        "access_token": self.token, "v": "5.126"})
        friends_id_list = response.json()["response"][0]["common_friends"]
        if len(friends_id_list) == 0:
            return 'Общих друзей не найдено'
        mutual_friends = []
        for id in friends_id_list:
            user_page = User(id)
            mutual_friends.append(str(user_page))
        return mutual_friends