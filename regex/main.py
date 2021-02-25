import re
import csv


def regex_phones_and_names(csv_file):
    with open(csv_file, encoding='utf-8') as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)

    phones_pattern = \
        re.compile(r"(\+7|8)\s?\(?(\d{3})\)?[\s-]?(\d{3})[\s-]?(\d{2})[\s-]?(\d{2})[\s]?\(?([доб.]*)[\s]?(\d*)\)?")

    full_text_pattern = re.compile(r"([А-Я]\w+)[\s,]([А-Я]\w*)[\s,](\w*)[,]+([А-Яа-я]*)[,]+([a-zа-яА-Я –]*)[,]+"
                                   r"(\+*[0-9]*\(?\d*\)?[0-9- доб\.]*)[,]([a-zA-Z0-9\.@]*)")

    text = ''
    for line in contacts_list:
        str_line = ",".join(line)
        if line != contacts_list[-1]:
            text += str_line + '\n'
        else:
            text += str_line

    fixed_phones_list = phones_pattern.sub(r"+7(\2)\3-\4-\5 \6\7", text)
    name_fixed_text = full_text_pattern.sub(r"\1,\2,\3,\4,\5,\6,\7", fixed_phones_list)
    new_contacts_list = [line.split(",") for line in name_fixed_text.split("\n")]

    unique_names = {line[0] + line[1] for line in new_contacts_list}
    doubles_list = []
    for line in new_contacts_list:
        if line[0] + line[1] in unique_names:
            unique_names.remove(line[0] + line[1])
        else:
            doubles_list.append(line)
    for line in new_contacts_list:
        for double in doubles_list:
            if double == line:
                new_contacts_list.remove(line)
            if double[0] + double[1] == line[0] + line[1]:
                element_index = 0
                for element in double:
                    if element == '':
                        element_index += 1
                    else:
                        line[element_index] = line[element_index].replace(line[element_index], element)
                        element_index += 1

    with open("phonebook.csv", "w", encoding='utf-8') as f:
        data_writer = csv.writer(f, delimiter=',')
        data_writer.writerows(new_contacts_list)


if __name__ == '__main__':
    regex_phones_and_names('phonebook_raw.csv')
