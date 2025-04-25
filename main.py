from bs4 import BeautifulSoup

with open('index.html','r') as html_file: #With is used to close the file without using close() even if there is an error & open for file objects 
    content = html_file.read() 
    print(content) 