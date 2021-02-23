import requests
import unittest
from auth import headers


class TestFolderCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.response = requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                                    headers=headers, params={"path": "test_folder"})

    @classmethod
    def tearDownClass(cls):
        cls.response = requests.delete("https://cloud-api.yandex.net/v1/disk/resources",
                                       headers=headers, params={"path": "test_folder", "permanently": "true"})

    def test_response_status(self):
        self.assertEqual(self.response.status_code, 201)

    def test_folder_presence(self):
        self.files_list = requests.get("https://cloud-api.yandex.net/v1/disk/resources",
                                       headers=headers, params={"path": "/"})
        names = [x['name'] for x in self.files_list.json()['_embedded']['items']]
        self.assertIn("test_folder", names)

    def test_correct_type(self):
        self.folder_info = requests.get("https://cloud-api.yandex.net/v1/disk/resources",
                                        headers=headers, params={"path": "test_folder"})
        self.assertEqual(self.folder_info.json()['type'], 'dir')


if __name__ == '__main__':
    unittest.main()
