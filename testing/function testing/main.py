from data import documents, directories, new_type, new_owner, new_number, new_shelf_number, old_number


def operations():
    while True:
        command = input('Введите команду')
        if command == 'p':
            print(get_a_person(documents))
        elif command == 's':
            print(get_a_shelf(directories))
        elif command == 'l':
            print(get_all_lists(documents))
        elif command == 'a':
            print(add_a_doc(documents, directories, new_type, new_number, new_owner, new_shelf_number))
            print(documents)
            print(directories)
        elif command == 'd':
            print(del_a_doc(documents, directories, old_number))
            print(documents)
            print(directories)
        elif command == 'm':
            print(move_a_doc(directories))
            print(documents)
            print(directories)
        elif command == 'as':
            print(add_a_shielf(directories))
            print(documents)
            print(directories)
        elif command == 'q':
            return 'Работа с документами завершена'


def get_a_person(docs_dicts_in_list):
    doc_number = input('Введите номер документа')

    for doc in docs_dicts_in_list:
        if doc_number == doc["number"]:
            return f'Владелец документа: {doc["name"]}'
    return 'Документ не найден'


def get_a_shelf(shielf_dict):
    doc_number = input('Введите номер документа')

    for shielf, docs in shielf_dict.items():
        if doc_number in docs:
            return f'Документ находится в полке № {shielf}'
    return 'Документ не найден'


def get_all_lists(docs_dicts_in_list):
    doc_info = ''
    for doc in docs_dicts_in_list:
        doc_info += f'{doc["type"]} "{doc["number"]}" "{doc["name"]}" \n'
    return doc_info


def add_a_doc(docs_dicts_in_list, shielf_dict, doc_type, doc_number, doc_owner, shielf_number):
    new_dict = {}
    new_dict["type"] = doc_type
    new_dict["number"] = doc_number
    new_dict["name"] = doc_owner.capitalize()

    for shielf, docs in shielf_dict.items():
        if shielf_number in shielf:
            docs.append(doc_number)
            shielf_dict[shielf_number] = docs
            docs_dicts_in_list.append(new_dict)
            return 'Документ успешно добавлен!'
    return 'Указанной полки не существует'


def del_a_doc(docs_dicts_in_list, shielf_dict, doc_number):

    for shielf, docs in shielf_dict.items():
        if doc_number in docs:
            docs.remove(doc_number)
            shielf_dict[shielf] = docs
    for docs in docs_dicts_in_list:
        if doc_number in docs["number"]:
            docs_dicts_in_list.remove(docs)
            return 'Документ успешно удалён!'
    return 'Введённого номера не существует в базе данных'


def move_a_doc(shielf_dict):
    doc_number = input('Введите номер документа')
    old_shielf = input('В какой полке лежал документ?')
    new_shielf = input('В какую полку переместить документ?')

    old_list = shielf_dict[old_shielf]
    new_list = shielf_dict[new_shielf]

    if doc_number not in old_list:
        return f'Документа № {doc_number} не существует в папке {old_shielf}!'

    old_list.remove(doc_number)
    new_list.append(doc_number)
    return f'Документ № {doc_number} успешно перемешён в папку {new_shielf}!'


def add_a_shielf(shielf_dict):
    new_shielf = input('Введите номер для новой полки')

    if new_shielf not in shielf_dict:
        shielf_dict[new_shielf] = []
        return 'Полка успешно добавлена!'
    return 'Полка с таким номером уже существует'


if __name__ == '__main__':
    operations()
