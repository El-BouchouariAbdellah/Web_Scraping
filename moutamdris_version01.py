from bs4 import BeautifulSoup
import requests 

html_text = requests.get('https://moutamadris.ma/%D8%A7%D9%84%D8%B3%D8%A7%D8%AF%D8%B3-%D8%A7%D8%A8%D8%AA%D8%AF%D8%A7%D8%A6%D9%8A/').text
soup = BeautifulSoup(html_text,'lxml')
subjects = soup.find_all('li','mada')
for subject in subjects:
    lien = subject.find('a')
    url = lien['href']
    cours_html = requests.get(url).text
    soup1 = BeautifulSoup(cours_html,'lxml')
    mat = soup1.find('li','medium-8 column')
    down_link = mat.find('a')
    down_pg_link = down_link['href']
    #print(down_pg_link)
    edu_html = requests.get(down_pg_link).text
    soup2 = BeautifulSoup(edu_html,'lxml')
    file = soup2.find('div', class_="entry-content")
    cours = file.find('a')
    link = cours['href']
    print(link)
    download = requests.get(link)
    filename = link.split('/')[-1]
    with open(filename, 'wb') as f:
        f.write(download.content)

    print(f"File downloaded: {filename}")


