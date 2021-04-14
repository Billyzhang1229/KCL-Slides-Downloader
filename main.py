import requests
from bs4 import BeautifulSoup
import re
import os

def getPDF(url, headers):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features="lxml")
    pdf_pages = soup.findAll("a", "aalink", href=re.compile("resource"))
    for pdf_page in pdf_pages:
        pdf_page_content = requests.get(pdf_page.get("href"), headers=headers)
        soup2 = BeautifulSoup(pdf_page_content.content, features="lxml")
        pdf_files = soup2.findAll("a", href=re.compile("(.pdf|.ppt|.pptx)"))
        for pdf_file in pdf_files:
            download_pdf(pdf_file.get("href"), headers)

def download_pdf(url, headers):
    i = 0
    while i < 3:
        try:
            if not os.path.exists(url):
                print(url + ' is downloading...' )
                r = requests.get(url, headers=headers, timeout=10)
                with open(url[ url.rindex( '/' ) + 1 : len( url ) ].replace("%20", " ") , 'wb') as pdf_file:
                    pdf_file.write(r.content)
                    print(url + " is downloaded")
                    i = 3
            else:
                print("file exsist")
                i = 3
        except Exception as e:
            print(e)
            i += 1

if __name__ == '__main__':
    course_id = input("Enter your course address ")
    cookie = input("Enter your cookie here ")
    headers = {
        "Cookie": cookie
    }
    getPDF(course_id, headers)


