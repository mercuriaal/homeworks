import requests
from bs4 import BeautifulSoup


def parsing_articles(*keywords):

    keywords = [*keywords]

    response = requests.get('https://habr.com/ru/all/')
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('article', class_='post')

    for post in posts:
        hubs = post.find_all('a', class_='hub-link')
        article_url = post.find('a', class_='btn').attrs.get('href')
        article_response = requests.get(article_url)
        another_soup = BeautifulSoup(article_response.text, 'html.parser')
        article_text = another_soup.find('div', class_='post__body_full').text.lower()

        for hub in hubs:
            hub_lower = hub.text.lower()
            if any([hub_lower in desired for desired in keywords]):
                title_element = post.find('a', class_='post__title_link')
                time_element = post.find('span', class_='post__time')
                title_url = title_element.attrs.get('href')
                print(f'Дата публикации - {time_element.text}\n'
                      f'Оглавление - {title_element.text}\n'
                      f'Ссылка - {title_url}\n')
            break

        for keyword in keywords:
            if keyword in article_text.split(' '):
                title_element = post.find('a', class_='post__title_link')
                time_element = post.find('span', class_='post__time')
                title_url = title_element.attrs.get('href')
                print(f'Дата публикации - {time_element.text}\n'
                      f'Оглавление - {title_element.text}\n'
                      f'Ссылка - {title_url}\n')
            break


if __name__ == '__main__':
    parsing_articles('дизайн', 'фото', 'web', 'python')
