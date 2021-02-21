import requests
import hashlib
from decorator import logger


class Iterator:

    def __init__(self, url):
        self.url = url
        self.count = -1
        self.data = requests.get(self.url).json()

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        if len(self.data) == self.count:
            raise StopIteration
        return self.data[0 + self.count]

    @logger('logs.txt')
    def direct_to_wiki(self, file_name):
        for country in self:
            name = country['name']['common']
            if ' ' in name:
                split_name = name.split()
                new_name = '_'.join(split_name)
                with open(file_name, 'a', encoding='utf-8') as f:
                    f.write(name + ' ' + '-' + ' ' + 'https://en.wikipedia.org/wiki/' + new_name + '\n')
            else:
                with open(file_name, 'a', encoding='utf-8') as f:
                    f.write(name + ' ' + '-' + ' ' + 'https://en.wikipedia.org/wiki/' + name + '\n')


@logger('logs.txt')
def hashing(file_name):
    with open(file_name, 'rb') as f:
        text = f.readlines()
    for lines in text:
        hashed = hashlib.md5(lines)
        yield hashed.digest()


if __name__ == '__main__':
    countries = Iterator('https://raw.githubusercontent.com/mledoze/countries/master/countries.json')
    countries.direct_to_wiki('file.txt')
    for line in hashing('file.txt'):
        print(line)
