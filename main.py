from bs4 import BeautifulSoup
import requests 

html_text = requests.get('https://twinfragrance.shop/').text
soup = BeautifulSoup(html_text,"lxml")
fragrences = soup.find_all('a',class_ = "product-block")
for fragrence in fragrences:
    frag_name = fragrence.find('span',class_ = "product-title").text
    frag_price = fragrence.find('span',class_ = "product-price" ).text
    print(f'{frag_name} costs {frag_price}')

# with open('index.html','r') as html_file: #With is used to close the file without using close() even if there is an error & open for file objects 
#     content = html_file.read() 
#     soup = BeautifulSoup(content,'lxml')
#     tags = soup.find_all('p')
    
#     for tag in tags:
#         print(tag.text)