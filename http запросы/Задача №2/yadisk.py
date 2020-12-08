import requests


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def upload(self, file_path: str):
        self.file_path = file_path
        HEADERS = {"Authorization": self.token}

        response = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload", params={"path": file_path, "overwrite": "true"}, headers=HEADERS)
        data = response.json()
        href = data["href"]

        with open(self.file_path, "rb") as f:
            upload = requests.put(href, files={"file": f})
        if upload.status_code != 201:
            return f'Ошибка при загрузке файла - {upload.status_code}'
        return 'Файл успешно загружен'


if __name__ == '__main__':
    uploader = YaUploader()
    result = uploader.upload('/test.txt')