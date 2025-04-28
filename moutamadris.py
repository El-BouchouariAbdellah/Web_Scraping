from bs4 import BeautifulSoup
import requests
import urllib.parse
import time

html_text = requests.get('https://moutamadris.ma/%D8%A7%D9%84%D8%B3%D8%A7%D8%AF%D8%B3-%D8%A7%D8%A8%D8%AA%D8%AF%D8%A7%D8%A6%D9%8A/').text
soup = BeautifulSoup(html_text, 'lxml')
subjects = soup.find_all('li', 'mada')

for index, subject in enumerate(subjects):
    try:
        print(f"Processing subject {index + 1}/{len(subjects)}")
        lien = subject.find('a')
        if not lien:
            print("No link found for this subject, skipping...")
            continue
            
        url = lien['href']
        try:
            cours_html = requests.get(url).text
            soup1 = BeautifulSoup(cours_html, 'lxml')
            mat = soup1.find('li', 'medium-8 column')
            
            if not mat:
                print("Could not find 'medium-8 column' element, skipping this subject...")
                continue
                
            down_link = mat.find('a')
            if not down_link:
                print("No download link found, skipping...")
                continue
                
            down_pg_link = down_link['href']
            
            try:
                edu_html = requests.get(down_pg_link).text
                soup2 = BeautifulSoup(edu_html, 'lxml')
                file = soup2.find('div', class_="entry-content")
                
                if not file:
                    print("No entry-content div found, skipping...")
                    continue
                    
                cours = file.find('a')
                if not cours:
                    print("No download link found in entry content, skipping...")
                    continue
                    
                link = cours['href']
                print(f"Found download link: {link}")
                
                try:
                    download = requests.get(link)
                    encoded_filename = link.split('/')[-1]
                    decoded_filename = urllib.parse.unquote(encoded_filename)
                    
                    # Create a safe filename
                    safe_filename = f"file_{index + 1}.pdf"
                    
                    try:
                        with open(safe_filename, 'wb') as f:
                            f.write(download.content)
                        print(f"File downloaded: {safe_filename}")
                    except Exception as e:
                        print(f"Error saving file: {e}, skipping...")
                        
                except Exception as e:
                    print(f"Error downloading file: {e}, skipping...")
            except Exception as e:
                print(f"Error processing education page: {e}, skipping...")
        except Exception as e:
            print(f"Error accessing course page: {e}, skipping...")
            
        # Add a small delay to avoid overwhelming the server
        time.sleep(1)
        
    except Exception as e:
        print(f"General error processing subject: {e}, moving to next subject...")
