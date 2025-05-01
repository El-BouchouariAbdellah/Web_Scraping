from bs4 import BeautifulSoup
import requests
import time

main_page_url = 'https://moutamadris.ma/%D8%A7%D9%84%D8%B3%D8%A7%D8%AF%D8%B3-%D8%A7%D8%A8%D8%AA%D8%AF%D8%A7%D8%A6%D9%8A/'
main_page_html = requests.get(main_page_url).text
main_page_soup = BeautifulSoup(main_page_html, 'lxml')
subject_elements = main_page_soup.find_all('li', 'mada')

file_counter = 1  # Global counter for unique filenames

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
            subject_page_soup = BeautifulSoup(subject_page_html, 'lxml')
            
            # Find all elements with class "medium-8 column"
            contents_containers = subject_page_soup.find_all('li', 'medium-8 column')
            
            if not contents_containers:
                content_lessons = subject_page_soup.find_all('div','table-responsive')
                for content_lesson in content_lessons:
                    lesson_links = content_lesson.find_all('a')
                    for lesson_link in lesson_links:
                        lesson_download_url = lesson_link['href']
                        print(f"Found lesson download link")
                        
                        try:
                            pdf_response = requests.get(lesson_download_url)
                            
                            # Use unique numbered filenames with global counter
                            pdf_filename = f"file_{file_counter}.pdf"
                            file_counter += 1  # Increment counter for next file
                            
                            try:
                                with open(pdf_filename, 'wb') as f:
                                    f.write(pdf_response.content)
                                print(f"File downloaded: {pdf_filename}")
                            except Exception as e:
                                print(f"Error saving file: {e}, skipping...")
                                
                        except Exception as e:
                            print(f"Error downloading file: {e}, skipping...")
                continue
                
            print(f"Found {len(contents_containers)} content containers")
            
            for container_index, content_container in enumerate(contents_containers):
                print(f"Processing content container {container_index + 1}/{len(contents_containers)}")
                
                content_link_element = content_container.find('a')
                if not content_link_element:
                    print("No content link found in this container, skipping...")
                    continue
                
                content_page_url = content_link_element['href']
                print(f"Found content page URL: {content_page_url}")
            
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
                    
                        # Use unique numbered filenames with global counter
                        pdf_filename = f"file_{file_counter}.pdf"
                        file_counter += 1  # Increment counter for next file
                    
                        try:
                            # Fixed: was using pdf_filename.content instead of pdf_response.content
                            with open(pdf_filename, 'wb') as f:
                                f.write(pdf_response.content)
                            print(f"File downloaded: {pdf_filename}")
                        except Exception as e:
                            print(f"Error saving file: {e}, skipping...")
                        
                    except Exception as e:
                        print(f"Error downloading file: {e}, skipping...")
                except Exception as e:
                    print(f"Error processing content page: {e}, skipping...")
                
                # Small delay between processing content containers
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error accessing subject page: {e}, skipping...")
            
        # Add a small delay to avoid overwhelming the server
        time.sleep(1)
        
    except Exception as e:
        print(f"General error processing subject: {e}, moving to next subject...")

print("Scraping completed!")