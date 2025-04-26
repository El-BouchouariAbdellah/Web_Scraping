from bs4 import BeautifulSoup
import requests 

html_text = requests.get('https://twinfragrance.shop/').text
soup = BeautifulSoup(html_text,"lxml")
fragrences = soup.find_all('div',class_ = "product-item-124")
print(fragrences)

# with open('index.html','r') as html_file: #With is used to close the file without using close() even if there is an error & open for file objects 
#     content = html_file.read() 
#     soup = BeautifulSoup(content,'lxml')
#     tags = soup.find_all('p')
    
#     for tag in tags:
#         print(tag.text)