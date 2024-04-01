from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime


def post_elements(post, thumbs):
    links = []
    id = post.attrs['data-defid']
    title = post.find('a', attrs={'id': id}).text
    meaning = post.find('div', class_='meaning')
    meaning_links = meaning.find_all('a')
    if meaning_links:
        links += list(meaning_links)
    example = post.find('div', class_='example')
    example_links = example.find_all('a')
    if example_links:
        links += list(example_links)
    author_link = post.find('div', class_='contributor').a
    author = author_link.text
    if author:
        date = author_link.next.next.strip()
    else:
        date = author_link.next.strip()
    date_obj = datetime.strptime(date, "%B %d, %Y")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    likes = thumbs[int(id)]['up']
    dislikes = thumbs[int(id)]['down']
    if links:
        links = [link.text for link in links]
    return {
        'id': id,
        'title': title,
        'meaning': meaning.text,
        'example': example.text,
        'date': formatted_date,
        'likes': likes,
        'dislikes': dislikes,
        'links': links,
    }


def get_definitions(name):
    raw_html = requests.get(
        f'https://www.urbandictionary.com/define.php?term={name}',
    ).text
    ids = []
    thumbs = {}
    posts = []
    objects = []
    soup = BeautifulSoup(raw_html, features="html.parser")
    posts.append(soup.find_all('div', class_='definition'))
    pagination = soup.find('div', class_='pagination')
    if pagination:
        last = pagination.find('a', attrs={'aria-label':'Last page'})
        href = last.attrs['href']
        pages = int(re.search('(?<=page=)[0-9]+', href).group())
        for page in range(2, pages+1):
            raw_html = requests.get(
            f'https://www.urbandictionary.com/define.php?term={name}&page={page}',
            )
            if raw_html.status_code == 200:
                soup = BeautifulSoup(raw_html.text, features="html.parser")
                posts.append(soup.find_all('div', class_='definition'))

    posts = [item for row in posts for item in row]

    for post in posts:
        id = post.attrs['data-defid']
        ids.append(id)

    raw_json = requests.get(
        f'https://api.urbandictionary.com/v0/uncacheable?ids={",".join(ids)}'
    ).json()
    for dic in raw_json['thumbs']:
        thumbs[dic['defid']] = {'up': dic['up'], 'down': dic['down']}
    for post in posts:
        objects.append(post_elements(post, thumbs))
    return objects

if __name__ == '__main__':
    definitions = get_definitions('207')
    print(len(definitions))
