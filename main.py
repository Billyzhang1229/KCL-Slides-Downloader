# import python modules
import re
import os
import time

# import download module
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

def get_page(url, headers) -> BeautifulSoup:
    """get page from url

        Parameters:
            url (str): url of the page
            headers (dict): headers for the request

        Returns:
            BeautifulSoup: soup of the page
    """
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features="lxml")
    return soup

def get_course_title(soup) -> str:
    """get course title from soup

        Parameters:
            soup (BeautifulSoup): soup of the page

        Returns:
            str: course title
    """
    return soup.find("div", {"class":"hero-box"}).find("h1").text


def get_file_list(soup) -> list:
    """get file list from url

        Parameters:
            url (str): url of the page
            headers (dict): headers for the request

        Returns:
            list: list of file urls
    """
    files = []
    file_pages = soup.find("section",{"id":"region-main"}).findAll("a", "aalink", href=re.compile("(resource|folder)"))
    for page in file_pages:
        page_url = page["href"]
        page_soup = get_page(page_url, headers)
        file_html = get_files_on_page(page_soup)
        for file in file_html:
            files.append(file["href"].split('?')[0])
    return files


def get_files_on_page(soup) -> list:
    """get file list from current page
    
        Parameters:
            soup (BeautifulSoup): soup of the page
        
        Returns:
            list: list of file urls
    """
    files = soup.find("div",{"role":"main"}).findAll("a", href=re.compile("(.pdf|.ppt|.pptx|.zip|.rar|.doc|.docx|.xls|.xlsx|.txt)"))
    return files


def download_file(url, headers, path):
    """download file from url

        Parameters:
            url (str): url of the file
            headers (dict): headers for the request
            path (str): path to save the file
    """
    file_name = url.split('/')[-1].replace('%20', ' ')
    file_path = os.path.join(path, file_name)
    i = 0
    while i < 3:
        try:
            if not os.path.exists(file_path):
                r = requests.get(url, headers=headers, timeout=10)
                with open(file_path, 'wb') as file:
                    file.write(r.content)
                    i = 3
            elif os.path.exists(file_path):
                i = 3
        except Exception as e:
            print(e)
            i += 1
    time.sleep(1)

if __name__ == '__main__':
    course_id = input("Enter your course address ")
    cookie = input("Enter your cookie here ")
    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
        "Cookie": cookie,}

    print("Fetching course details...")

    course_page = get_page(course_id, headers)
    course_title = get_course_title(course_page)
    file_list = get_file_list(course_page)
    
    if not os.path.exists(course_title):
        os.mkdir(course_title)

    file_log = tqdm(total=0, position=1, bar_format="{desc}")
    for file in tqdm(file_list, unit="file", position=0):
        file_log.set_description(f"Downloading {file.split('/')[-1].replace('%20', ' ')}")
        download_file(file, headers, course_title)