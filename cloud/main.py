import time
import json
import os
from tqdm import tqdm
import requests


class AccountVK:
    def __init__(self, account_id):
        self.account_id = account_id

    def download_photos(self):
        with open("vk_token.txt", encoding="utf-8") as f1:
            vk_token = f1.read()
        offset = 0
        list_of_likes = []
        list_for_json = []
        if not os.path.exists("Downloaded_Photos"):
            os.mkdir("Downloaded_Photos")
        while True:
            overall_response = requests.get("https://api.vk.com/method/" + "photos.getAll",
                                            params={"owner_id": self.account_id, "extended": "1",
                                                    "count": "200", "offset": offset,
                                                    "access_token": vk_token, "v": "5.126"})
            overall_response.raise_for_status()
            offset += 200
            if len(overall_response.json()["response"]["items"]) == 0:
                break
            photos_info = overall_response.json()["response"]["items"]
            for photo in tqdm(photos_info):
                likes = photo["likes"]["count"]
                list_of_likes.append(likes)
                if list_of_likes.count(likes) > 1:
                    file_name = str(likes) + "-" + str(photo["date"]) + ".jpg"
                else:
                    file_name = str(likes) + ".jpg"

                size = photo["sizes"][-1]["type"]
                photo_info_dict = dict(file_name=file_name, size=size)
                list_for_json.append(photo_info_dict)

                photo_path = os.path.join("Downloaded_Photos", file_name)
                photo_url = photo["sizes"][-1]["url"]
                url_response = requests.get(photo_url)
                url_response.raise_for_status()
                time.sleep(0.5)
                with open(photo_path, "wb") as picture:
                    picture.write(url_response.content)
        with open("photo_info.json", "w") as f:
            json.dump(list_for_json, f, ensure_ascii=False, indent=4)
        return


class AccountYaDisk:
    def __init__(self, cloud_token):
        self.cloud_token = cloud_token

    def upload_photos(self, photos_lim: int):
        headers = {"Authorization": self.cloud_token}
        photos_count = 0
        requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                     headers=headers, params={"path": "Uploaded_Photos"})
        photos_list = os.listdir("Downloaded_Photos")
        for photo in tqdm(photos_list[0:photos_lim]):
            response = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload",
                                    params={"path": "/Uploaded_Photos/" + photo, "overwrite": "true"},
                                    headers=headers)
            data = response.json()
            href = data["href"]
            with open("Downloaded_Photos/" + photo, "rb") as f:
                upload = requests.put(href, files={"file": f})
                upload.raise_for_status()
                photos_count += 1
        return


if __name__ == '__main__':
    vk = AccountVK()
    yadisk = AccountYaDisk()
    vk.download_photos()
    yadisk.upload_photos(5)
