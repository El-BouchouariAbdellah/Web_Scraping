from bs4 import BeautifulSoup
import requests

with open('table_fix.html','r', encoding='UTF-8') as html_file:
    html_code = html_file.read()

download_soup = BeautifulSoup(html_code,'lxml')
extract_tables = download_soup.find_all('table')
for table in extract_tables:
    trs = table.find_all('tr')
    print(trs)
    print('***'*20)
    for tr in trs:
        tds = tr.find_all('td')
        print(tds)
        print('***'*20)
        if tds:
            first_cell = tds[0]
            link = first_cell.find('a')
            if not link:
                print("first cell is empty continue to the next line")
                continue
            url_download = link['href']
            print(url_download)
            download = requests.get(url_download)
            with open('filetest', 'wb') as f:
                f.write(download.content)

            
        
