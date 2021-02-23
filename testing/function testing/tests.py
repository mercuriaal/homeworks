import unittest
from main import get_all_lists, add_a_doc, del_a_doc
from data import documents, directories, new_type, new_owner, new_number, new_shelf_number, old_number


class TestFunctions(unittest.TestCase):

    def test_list_existence(self):
        self.assertIsNotNone(get_all_lists(documents))

    def test_list_type(self):
        self.assertIsInstance(get_all_lists(documents), str)

    def test_existence_in_documents(self):
        add_a_doc(documents, directories, new_type, new_number, new_owner, new_shelf_number)
        self.assertIn(new_number, [document['number'] for document in documents])

    def test_existence_in_directories(self):
        add_a_doc(documents, directories, new_type, new_number, new_owner, new_shelf_number)
        values_list = [directories.get(key) for key in directories.keys()]
        new_values_list = []
        for values in values_list:
            new_values_list.extend(values)
        self.assertIn(new_number, new_values_list)

    def test_absence_in_documents(self):
        del_a_doc(documents, directories, old_number)
        self.assertNotIn(old_number, [document['number'] for document in documents])

    def test_absence_in_directories(self):
        del_a_doc(documents, directories, old_number)
        values_list = [directories.get(key) for key in directories.keys()]
        new_values_list = []
        for values in values_list:
            new_values_list.extend(values)
        self.assertNotIn(old_number, new_values_list)


if __name__ == '__main__':
    unittest.main()
