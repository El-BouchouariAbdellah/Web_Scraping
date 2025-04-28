from bs4 import BeautifulSoup
import requests 

html_text = requests.get('https://moutamadris.ma/%d8%a7%d9%84%d8%a7%d9%88%d9%84-%d8%a7%d8%a8%d8%aa%d8%af%d8%a7%d8%a6%d9%8a/').text
soup = BeautifulSoup(html_text,'lxml')
subject = soup.find('li','mada')
lien = subject.find('a')
url = lien['href']
cours_html = requests.get(url).text
soup1 = BeautifulSoup(cours_html,'lxml')
mat = soup1.find('li','medium-8 column')
down_link = mat.find('a')
down_pg_link = down_link['href']
print(down_pg_link)
edu_html = requests.get(down_pg_link).text
soup2 = BeautifulSoup(edu_html,'lxml')
file = soup2.find('div', class_="entry-content")
cours = file.find('a')
link = cours['href']
download = requests.get(link)
filename = link.split('/')[-1]
with open(filename, 'wb') as f:
    f.write(download.content)

print(f"File downloaded: {filename}")


