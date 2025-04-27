from bs4 import BeautifulSoup
import requests 

html_text = requests.get('https://moutamadris.ma/%d8%a7%d9%84%d8%b2%d9%85%d8%a7%d9%86-%d8%a7%d9%84%d9%85%d8%b3%d8%aa%d9%88%d9%89-%d8%a7%d9%84%d8%a7%d9%88%d9%84/').text
soup = BeautifulSoup(html_text,'lxml')
file = soup.find('div', class_="entry-content")
cours = file.find('a')
link = cours['href']
download = requests.get(link)
filename = link.split('/')[-1]
with open(filename, 'wb') as f:
    f.write(download.content)

print(f"File downloaded: {filename}")