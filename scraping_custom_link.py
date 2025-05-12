from bs4 import BeautifulSoup
import requests
import time
import os

main_page_url = 'https://moutamadris.ma/%D8%A7%D9%84%D8%AC%D8%B0%D8%B9-%D8%A7%D9%84%D9%85%D8%B4%D8%AA%D8%B1%D9%83/'
main_page_html = requests.get(main_page_url).text
main_page_soup = BeautifulSoup(main_page_html, 'lxml')
subject_elements = main_page_soup.find_all('li', 'mada')

file_counter = 1  # Global counter for unique filenames
success_count = 0  # Counter for successful downloads
fail_count = 0     # Counter for failed downloads

print(f"Starting scraper for moutamadris.ma")
print(f"Found {len(subject_elements)} subjects to process")

for subject_index, subject_element in enumerate(subject_elements):
    try:
        print(f"\nProcessing subject {subject_index + 1}/{len(subject_elements)}")
        subject_link_element = subject_element.find('a')
        if not subject_link_element:
            print(f"❌ No link found for this subject, skipping...")
            continue
            
        subject_name = subject_link_element.text.strip()
        print(f"Subject: {subject_name}")
        
        # Create a folder for this subject using the raw subject_name
        if not os.path.exists(subject_name):
            os.makedirs(subject_name)
            print(f"✅ Created folder: {subject_name}")
        else:
            print(f"📁 Using existing folder: {subject_name}")
        
        subject_page_url = subject_link_element['href']
        try:
            subject_page_html = requests.get(subject_page_url).text
            subject_page_soup = BeautifulSoup(subject_page_html, 'lxml')
            
            # Check for "mawad" class - if found, skip this subject
            mawad_element = subject_page_soup.find(class_="mawad")
            if mawad_element:
                print(f"⚠️ This subject doesn't have any lessons on this website, skipping to next subject...")
                continue
            
            # Find all elements with class "medium-8 column"
            contents_containers = subject_page_soup.find_all('li', 'medium-8 column')
            
            if not contents_containers:
                print(f"🔍 No content containers found, checking table-responsive divs...")
                content_lessons = subject_page_soup.find_all('div','table-responsive')
                if not content_lessons:
                    print(f"❌ No table-responsive divs found either, skipping subject...")
                    continue
                    
                for content_lesson in content_lessons:
                    tbody = content_lesson.find('tbody')
                    if tbody:
                        table_info = tbody.find_all('tr')
                    else:
                        table_info = []                    
                    print(table_info)
                    
                    lesson_links = .find_all('a')
                    if not lesson_links:
                        print(f"❌ No lesson links found, skipping this container...")
                        content_lessons_table = subject_page_soup.find_all('table', id = 'tableone')
                        if not content_lessons_table:
                                continue
                        for content_lesson_table in content_lessons_table:
                                lesson_table_links = content_lesson_table.find_all('a')
                                if not lesson_table_links:
                                    print(f"❌ No lesson links found, skipping this container...")                                    
                                    continue

                                print(f"🔗 Found {len(lesson_table_links)} lesson links")
                                for lesson_table_link in lesson_table_links:
                                    lesson_table_download_url = lesson_table_link['href']

                                    try:
                                        pdf_table_response = requests.get(lesson_table_download_url)

                                        pdf_filename = os.path.join(subject_name, f"file_{file_counter}.pdf")
                                        file_counter += 1  # Increment counter for next file

                                        try:
                                            with open(pdf_filename, 'wb') as f:
                                                f.write(pdf_table_response.content)
                                            print(f"✅ File downloaded: {pdf_filename}")
                                            success_count += 1
                                        except Exception as e:
                                            print(f"❌ Error saving file: {e}, skipping...")
                                            fail_count += 1
                                    except Exception as e:
                                        print(f"❌ Error downloading file: {e}, skipping...")
                                        fail_count += 1
                                continue
                        for content_lesson in content_lessons:
                            lesson_links = content_lesson.find_all('a')
                            if not lesson_links:
                                print(f"❌ No lesson links found, skipping this container...")
                                continue
                                
                            print(f"🔗 Found {len(lesson_links)} lesson links")
                            for lesson_link in lesson_links:
                                lesson_download_url = lesson_link['href']
                                ##print(f"⬇️ Attempting download from {lesson_download_url}")
                                
                                try:
                                    pdf_response = requests.get(lesson_download_url)
                                    
                                    # Use numbered filenames within the subject folder
                                    pdf_filename = os.path.join(subject_name, f"file_{file_counter}.pdf")
                                    file_counter += 1  # Increment counter for next file
                                    
                                    try:
                                        with open(pdf_filename, 'wb') as f:
                                            f.write(pdf_response.content)
                                        print(f"✅ File downloaded: {pdf_filename}")
                                        success_count += 1
                                    except Exception as e:
                                        print(f"❌ Error saving file: {e}, skipping...")
                                        fail_count += 1
                                        
                                except Exception as e:
                                    print(f"❌ Error downloading file: {e}, skipping...")
                                    fail_count += 1
                        continue
                        
                    print(f"🔗 Found {len(lesson_links)} lesson links")
                    for lesson_link in lesson_links:
                        lesson_download_url = lesson_link['href']
                        print(f"⬇️ Attempting download from {lesson_download_url}")
                        
                        try:
                            pdf_response = requests.get(lesson_download_url)
                            
                            # Use unique numbered filenames with global counter
                            pdf_filename = os.path.join(subject_name, f"file_{file_counter}.pdf")
                            file_counter += 1  # Increment counter for next file
                            
                            try:
                                with open(pdf_filename, 'wb') as f:
                                    f.write(pdf_response.content)
                                print(f"✅ File downloaded: {pdf_filename}")
                                success_count += 1
                            except Exception as e:
                                print(f"❌ Error saving file: {e}, skipping...")
                                fail_count += 1
                                
                        except Exception as e:
                            print(f"❌ Error downloading file: {e}, skipping...")
                            fail_count += 1
                continue
                
            print(f"🔍 Found {len(contents_containers)} content containers")
            
            for container_index, content_container in enumerate(contents_containers):
                print(f"📄 Processing content container {container_index + 1}/{len(contents_containers)}")
                
                content_link_element = content_container.find('a')
                if not content_link_element:
                    print(f"❌ No content link found in this container, skipping...")
                    continue
                
                content_page_url = content_link_element['href']
                print(f"🔗 Found content page URL: {content_page_url}")
            
                try:
                    content_page_html = requests.get(content_page_url).text
                    content_page_soup = BeautifulSoup(content_page_html, 'lxml')
                    
                    # Check for "mawad" class in the content page
                    mawad_element = content_page_soup.find(class_="mawad")
                    if mawad_element:
                        print(f"⚠️ This subject doesn't have any lessons on this website, skipping to next subject...")
                        break  # Break out of the container loop and move to next subject
                    
                    article_content = content_page_soup.find('div', class_="entry-content")
                
                    if not article_content:
                        print(f"❌ No article content found, skipping...")
                        continue
                    
                    download_link_element = article_content.find('a')
                    if not download_link_element:
                        print(f"❌ No download link found in entry content, skipping...")
                        continue
                    
                    pdf_download_url = download_link_element['href']
                    print(f"⬇️ Found download link: {pdf_download_url}")
                
                    try:
                        pdf_response = requests.get(pdf_download_url)
                        
                        # Simple numbered filename in the subject folder
                        pdf_filename = os.path.join(subject_name, f"file_{file_counter}.pdf")
                        file_counter += 1  # Increment counter for next file
                    
                        try:
                            with open(pdf_filename, 'wb') as f:
                                f.write(pdf_response.content)
                            print(f"✅ File downloaded: {pdf_filename}")
                            success_count += 1
                        except Exception as e:
                            print(f"❌ Error saving file: {e}, skipping...")
                            fail_count += 1
                        
                    except Exception as e:
                        print(f"❌ Error downloading file: {e}, skipping...")
                        fail_count += 1
                except Exception as e:
                    print(f"❌ Error processing content page: {e}, skipping...")
                
                # Small delay between processing content containers
                time.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Error accessing subject page: {e}, skipping...")
            
        # Add a small delay to avoid overwhelming the server
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ General error processing subject: {e}, moving to next subject...")

print("\n=== Scraping Summary ===")
print(f"✅ Total successful downloads: {success_count}")
print(f"❌ Total failed downloads: {fail_count}")
print(f"📁 Total files attempted: {success_count + fail_count}")
print("Scraping completed!")