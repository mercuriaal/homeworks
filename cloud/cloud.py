import requests
import time
import json
from tqdm import tqdm

with open("vk_token.txt", encoding="utf-8") as f1:
    vk_token = f1.read()


def save_photos(social_media_id, cloud_token):
    headers = {"Authorization": cloud_token}
    offset = 0
    likes_list = []
    list_for_json = []
    requests.put("https://cloud-api.yandex.net/v1/disk/resources", headers=headers, params={"path": "VK_Photos"})
    while True:
        response = requests.get("https://api.vk.com/method/" + "photos.getAll",
                                params={"owner_id": social_media_id, "extended": "1",
                                        "count": "200", "offset": offset, "access_token": vk_token, "v": "5.126"})
        response.raise_for_status()
        time.sleep(0.5)
        offset += 200
        if len(response.json()["response"]["items"]) == 0:
            break
        photos_info = response.json()["response"]["items"]
        for photo in tqdm(photos_info):
            photo_url = photo["sizes"][-1]["url"]
            likes = photo["likes"]["count"]
            likes_list.append(likes)
            if likes_list.count(likes) > 1:
                file_name = str(likes) + "-" + str(photo["date"]) + ".jpg"
            else:
                file_name = str(likes) + ".jpg"
            photo_upload = requests.post("https://cloud-api.yandex.net/v1/disk/resources/upload", headers=headers,
                                         params={"url": photo_url, "path": "disk:/VK_Photos/" + file_name})
            photo_upload.raise_for_status()
            size = photo["sizes"][-1]["type"]
            photo_info_dict = dict(file_name=file_name, size=size)
            list_for_json.append(photo_info_dict)
    with open("photo_info.json", "w") as f:
        json.dump(list_for_json, f, ensure_ascii=False, indent=4)
    return "Файлы успешно загружены"
