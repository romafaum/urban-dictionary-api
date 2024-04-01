import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from django.http import Http404, HttpResponseServerError


def post_elements(post, thumbs):
    """ Function for assemble definition object"""
    links = []
    id = post.attrs['data-defid']
    title = post.find('a', attrs={'id': id})
    if title:
        title = title.text
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
        'author': author,
        'date': formatted_date,
        'likes': likes,
        'dislikes': dislikes,
        'links': links,
    }


def get_thumbs(posts):
    """ Function for get likes and dislikes for all definitions"""
    ids = []
    thumbs = {}
    for post in posts:
        id = post.attrs['data-defid']
        ids.append(id)

    raw_json = requests.get(
        f'https://api.urbandictionary.com/v0/uncacheable?ids={",".join(ids)}'
    ).json()
    for dic in raw_json['thumbs']:
        thumbs[dic['defid']] = {'up': dic['up'], 'down': dic['down']}
    return thumbs


def get_posts_from_pagination(pagination, link):
    """ Funcion for get definitions objects from all pages"""
    posts = []
    last = pagination.find('a', attrs={'aria-label':'Last page'})
    href = last.attrs['href']
    pages = int(re.search('(?<=page=)[0-9]+', href).group())
    for page in range(2, pages+1):
        raw_html = requests.get(f'{link}&page={page}')
        if raw_html.status_code == 200:
            soup = BeautifulSoup(raw_html.text, features="html.parser")
            posts.append(soup.find_all('div', class_='definition'))
    return posts



def check_error(status_code):
    """ Helper function for throw an error"""
    if status_code == 404:
        raise Http404(f"Page not found")
    elif not status_code == 200:
        raise HttpResponseServerError("Server don't response")


def get_objects(link):
    """Main function to collect all definition together"""
    raw_html = requests.get(link)
    check_error(raw_html.status_code)
    posts = []
    objects = []
    soup = BeautifulSoup(raw_html.text, features="html.parser")
    html_posts = soup.find_all('div', class_='definition')
    posts.append(html_posts)
    pagination = soup.find('div', class_='pagination')
    if pagination:
        posts += get_posts_from_pagination(pagination, link)
    posts = [item for row in posts for item in row]

    thumbs = get_thumbs(posts)
    for post in posts:
        objects.append(post_elements(post, thumbs))
    return objects


def get_definitions(name):
    """Function for defenition view. Looking for deffinition by it's name"""
    link = f'https://www.urbandictionary.com/define.php?term={name}'
    definitions = get_objects(link)
    return definitions

def get_author_definitions(name):
    """Function for author view. Looking for author by they name"""
    link = f'https://www.urbandictionary.com/author.php?author={name}'
    author_definitions = get_objects(link)
    return author_definitions

def get_random_definitions():
    """Function for random view. Get 7 random defenition"""
    link = 'https://www.urbandictionary.com/random.php'
    raw_html = requests.get(link)
    check_error(raw_html.status_code)
    objects = []
    soup = BeautifulSoup(raw_html.text, features="html.parser")
    posts = soup.find_all('div', class_='definition')
    thumbs = get_thumbs(posts)
    for post in posts:
        objects.append(post_elements(post, thumbs))
    return objects