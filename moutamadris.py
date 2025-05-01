from bs4 import BeautifulSoup
import requests
import time

main_page_url = 'https://moutamadris.ma/%D8%A7%D9%84%D8%B3%D8%A7%D8%AF%D8%B3-%D8%A7%D8%A8%D8%AA%D8%AF%D8%A7%D8%A6%D9%8A/'
main_page_html = requests.get(main_page_url).text
main_page_soup = BeautifulSoup(main_page_html, 'lxml')
subject_elements = main_page_soup.find_all('li', 'mada')

for subject_index, subject_element in enumerate(subject_elements):
    try:
        print(f"Processing subject {subject_index + 1}/{len(subject_elements)}")
        subject_link_element = subject_element.find('a')
        if not subject_link_element:
            print("No link found for this subject, skipping...")
            continue
            
        subject_page_url = subject_link_element['href']
        try:
            subject_page_html = requests.get(subject_page_url).text
            subject_page_soup  = BeautifulSoup(subject_page_html, 'lxml')
            content_container = subject_page_soup .find('li', 'medium-8 column')
            
            if not content_container:
                print("Could not find content container element, skipping this subject...")
                continue
                
            content_link_element = content_container.find('a')
            if not content_link_element:
                print("No content link found, skipping...")
                continue
                
            content_page_url = content_link_element['href']
            
            try:
                content_page_html = requests.get(content_page_url).text
                content_page_soup = BeautifulSoup(content_page_html, 'lxml')
                article_content = content_page_soup.find('div', class_="entry-content")
                
                
                if not article_content:
                    print("No article content found, skipping...")
                    continue
                    
                download_link_element = article_content.find('a')
                if not download_link_element:
                    print("No download link found in entry content, skipping...")
                    continue
                    
                pdf_download_url = download_link_element['href']
                print(f"Found download link: {pdf_download_url}")
                
                try:
                    pdf_response = requests.get(pdf_download_url)
                    
                    # Use simple numbered filenames
                    pdf_filename = f"file_{subject_index + 1}.pdf"
                    
                    try:
                        with open(pdf_filename, 'wb') as f:
                            f.write(pdf_filename.content)
                        print(f"File downloaded: {pdf_filename}")
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

print("Scraping completed!")