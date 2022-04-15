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
    return soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a")["title"].replace('%20', ' ').replace('&amp;', '&')

def get_weeks(soup) -> list:
    """get weeks from url

        Parameters:
            url (str): url of the page
            headers (dict): headers for the request

        Returns:
            list: html for each week
    """
    return soup.find("div", {"class": "course-content"}).find_all("li", class_="section")

def get_file_list(soup) -> list:
    """get file list from url

        Parameters:
            url (str): url of the page
            headers (dict): headers for the request

        Returns:
            list: list of file urls
    """
    file_names = []
    files = []
    file_pages = soup.findAll("a", "aalink", href=re.compile("(resource|folder)"))
    for page in file_pages:
        page_url = page["href"]
        page_soup = get_page(page_url, headers)
        file_html = get_files_on_page(page_soup)
        for file in file_html:
            files.append(file["href"].split('?')[0])
            file_names.append(file["href"].split('?')[0].split('/')[-1].replace('%20', ' ').replace('&amp;', '&').replace('%28', '(').replace('%29', ')'))

    files_on_page = get_files_in_section(soup)
    for file in files_on_page:
        if file["href"].split('?')[0].split('/')[-1].replace('%20', ' ').replace('&amp;', '&').replace('%28', '(').replace('%29', ')') not in file_names:
            files.append(file["href"].split('?')[0])
    return files


def get_files_on_page(soup) -> list:
    """get file list from current page

        Parameters:
            soup (BeautifulSoup): soup of the page

        Returns:
            list: list of file urls
    """
    files = soup.find("div", {"role": "main"}).findAll("a", href=re.compile(
        "(.pdf|.ppt|.pptx|.zip|.rar|.doc|.docx|.xls|.xlsx|.txt)"))
    return files

def get_files_in_section(soup) -> list:
    """get file list from current page

        Parameters:
            soup (BeautifulSoup): soup of the page

        Returns:
            list: list of file urls
    """
    files = soup.findAll("a", href=re.compile(
        "(.pdf|.ppt|.pptx|.zip|.rar|.doc|.docx|.xls|.xlsx|.txt)"))
    return files


def download_file(url, headers, path):
    """download file from url

        Parameters:
            url (str): url of the file
            headers (dict): headers for the request
            path (str): path to save the file
    """
    file_name = url.split('/')[-1].replace('%20', ' ').replace('&amp;', '&').replace('%28', '(').replace('%29', ')')
    file_path = os.path.join(path, file_name)
    i = 0
    while i < 3:
        try:
            if "kcl.ac.uk" in url:
                if not os.path.exists(file_path):
                    r = requests.get(url, headers=headers, timeout=10)
                    with open(file_path, 'wb') as file:
                        file.write(r.content)
                        i = 3
                elif os.path.exists(file_path):
                    i = 3
            else:
                if not os.path.exists(file_path):
                    r = requests.get(url, timeout=10)
                    with open(file_path, 'wb') as file:
                        file.write(r.content)
                        i = 3
                elif os.path.exists(file_path):
                    i = 3
        except Exception as e:
            print(e)
            i += 1
    time.sleep(1)

def download_files_in_one_folder(course_page, headers, course_title):
    """download files from url in one folder

        Parameters:
            url (str): url of the page
            headers (dict): headers for the request
            path (str): path to save the files
    """
    
    file_list = get_file_list(course_page)
    file_log = tqdm(total=0, position=1, bar_format="{desc}")
    for file in tqdm(file_list, unit="file", position=0, colour="CYAN"):
        file_log.set_description_str(
            f"Downloading {file.split('/')[-1].replace('%20', ' ')}")
        download_file(file, headers, course_title)


def download_files_by_week(course_page, headers, course_title):
    """download files from url by week

        Parameters:
            url (str): url of the page
            headers (dict): headers for the request
            path (str): path to save the files
    """
    files_dict = {}
    weeks = get_weeks(course_page)
    for week in weeks:
        sectioname = week.find("h3")
        if sectioname is not None:
            dir_name = sectioname.text
        files = get_file_list(week)
        if files and dir_name:
            if dir_name in files_dict.keys():
                files_dict[dir_name] += files
            else:
                files_dict[dir_name] = files

    progress_bar = tqdm(total=sum((len(v) for v in files_dict.values())), position=0, unit="file", colour="CYAN")
    progress_log = tqdm(total=0, position=1, bar_format="{desc}")
    for dir_name, files in files_dict.items():
        dir_path = os.path.join(course_title, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for file in files:
            progress_log.set_description_str(
                f"Downloading {file.split('/')[-1].replace('%20', ' ')}")
            download_file(file, headers, dir_path)
            progress_bar.update(1)



def yes_or_no(content):
    """Determine if the input is yes or no

        Parameters:
            input (str): input from user

        Returns:
            bool: True if yes, False if no
    """
    
    choice = input("{} (y/n): ".format(content)).lower()
    if choice.lower() == 'y' or choice == '是' or choice.lower() == 'yes' or choice.lower() == 'true' or choice.lower() == 't' or choice.lower() == '1' or choice.lower() == 'да' or choice.lower() == 'д' :
        return True
    elif choice.lower() == 'n' or choice == '否' or choice.lower() == 'no' or choice.lower() == 'false' or choice.lower() == 'f' or choice.lower() == '0' or choice.lower() == 'нет' or choice.lower() == 'н' :
        return False
    else:
        print("Wrong input, try again")
        return yes_or_no(content)
    


if __name__ == '__main__':
    course_id = input("Enter your course address: ")
    cookie = input("Enter your cookie here: ")
    week = yes_or_no("Do you want to seperate files by week?")
    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
        "Cookie": cookie, }

    print("Fetching course details...")

    course_page = get_page(course_id, headers)
    course_title = get_course_title(course_page)

    if not os.path.exists(course_title):
        os.mkdir(course_title)

    if not week:
        download_files_in_one_folder(course_page, headers, course_title)
    else:
        download_files_by_week(course_page, headers, course_title)

    print("Done!")

    

