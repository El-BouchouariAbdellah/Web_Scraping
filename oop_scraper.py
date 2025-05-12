from bs4 import BeautifulSoup
import requests
import time
import os

# Initialize global counters
total_success_count = 0
total_fail_count = 0
total_empty_cells = 0

def create_folder(folder_path):
    """Create a folder if it doesn't exist"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ Created folder: {folder_path}")
        return True
    else:
        print(f"📁 Using existing folder: {folder_path}")
        return False

print("Starting scraper for moutamadris.ma")

# Get all grades
grades_page_url = 'https://moutamadris.ma/cours/'
grades_page_html = requests.get(grades_page_url).text
grades_page_soup = BeautifulSoup(grades_page_html, 'lxml')
grades_element_div = grades_page_soup.find('div','read')
grades_element = grades_element_div.find_all('li', class_='medium-6 column') # pour eviter le telechargement des controles

print(f"Found {len(grades_element)} grades to process")

# Process each grade
for grade_index, grade_element in enumerate(grades_element):
    grade_link_element = grade_element.find('a')
    if not grade_link_element:
        print(f"❌ No link found for this grade, skipping...")
        continue
        
    grade_name = grade_link_element.text #.strip()
    print(f"\n\n{'='*50}")
    print(f"Processing Grade {grade_index + 1}/{len(grades_element)}: {grade_name}")
    print(f"{'='*50}")

    # Create a folder for this grade
    grade_folder = grade_name 
    create_folder(grade_folder)
    
    # Process the grade page to find subjects
    grade_page_url = grade_link_element['href']
    try:
        grade_page_html = requests.get(grade_page_url).text
        grade_page_soup = BeautifulSoup(grade_page_html, 'lxml')
        subject_elements = grade_page_soup.find_all('li', 'mada')
        
        if not subject_elements:
            print(f"❌ No subjects found for grade: {grade_name}, skipping...")
            continue
            
        print(f"Found {len(subject_elements)} subjects in {grade_name}")
        
        # Initialize counters for this grade
        grade_success_count = 0
        grade_fail_count = 0
        grade_empty_cells = 0
        file_counter = 1
        
        # Process each subject within this grade
        for subject_index, subject_element in enumerate(subject_elements):
            try:
                print(f"\nProcessing subject {subject_index + 1}/{len(subject_elements)}")
                subject_link_element = subject_element.find('a')
                if not subject_link_element:
                    print(f"❌ No link found for this subject, skipping...")
                    continue
                    
                subject_name = subject_link_element.text #.strip()
                print(f"Subject: {subject_name}")
                
                # Create a subject folder inside the grade folder
                subject_folder = os.path.join(grade_folder, subject_name)
                create_folder(subject_folder)
                
                subject_page_url = subject_link_element['href']
                try:
                    subject_page_html = requests.get(subject_page_url).text
                    subject_page_soup = BeautifulSoup(subject_page_html, 'lxml')
                    
                    # Check for "mawad" class - if found, skip this subject
                    mawad_element = subject_page_soup.find(class_="mawad") # to fix the problem of the page with no lessons
                    if mawad_element:
                        print(f"⚠️ This subject doesn't have any lessons on this website, skipping to next subject...")
                        continue
                    
                    # Find all elements with class "medium-8 column"
                    contents_containers = subject_page_soup.find_all('li', 'medium-8 column')
                    
                    if not contents_containers:
                        print(f"🔍 No content containers found, checking table-responsive divs...") # for french subject
                        content_lessons = subject_page_soup.find_all('div', 'table-responsive')
                        if not content_lessons:
                            print(f"❌ No table-responsive divs found , check tableone tables ... ")
                            content_lessons_table = subject_page_soup.find_all('table', id = 'tableone')
                            if not content_lessons_table:
                                continue

                            # Process each table
                            for content_lesson_table in content_lessons_table:
                                # Find all rows in the table
                                table_rows = content_lesson_table.find_all('tr')
                                
                                print(f"📋 Found {len(table_rows)} rows in table")
                                for row in table_rows:
                                    # Get all cells in this row
                                    cells = row.find_all('td')
                                    if not cells or len(cells) == 0:
                                        # This could be a header row, skip it
                                        continue
                                    
                                    # Process only the first cell of the row
                                    first_cell = cells[0]
                                    
                                    # Check if the cell has a link
                                    pdf_link = first_cell.find('a')
                                    
                                    if not pdf_link:
                                        print(f"⚠️ Empty first cell found in row, no PDF link available")
                                        grade_empty_cells += 1
                                        continue
                                    
                                    # Get the PDF link
                                    pdf_url = pdf_link['href']
                                    
                                    try:
                                        pdf_response = requests.get(pdf_url)
                                        
                                        pdf_filename = os.path.join(subject_folder, f"file_{file_counter}.pdf")
                                        file_counter += 1  # Increment counter for next file
                                        
                                        try:
                                            with open(pdf_filename, 'wb') as f:
                                                f.write(pdf_response.content)
                                            print(f"✅ File downloaded from first cell: {pdf_filename}")
                                            grade_success_count += 1
                                        except Exception as e:
                                            print(f"❌ Error saving file: {e}, skipping...")
                                            grade_fail_count += 1
                                    except Exception as e:
                                        print(f"❌ Error downloading file: {e}, skipping...")
                                        grade_fail_count += 1
                                continue
                        
                        # Process table-responsive divs
                        for content_lesson in content_lessons:
                            # Find all tables within this responsive div
                            tables = content_lesson.find_all('table')
                            
                            for table in tables:
                                # Find all rows in the table
                                table_rows = table.find_all('tr')
                                
                                print(f"📋 Found {len(table_rows)} rows in table")
                                for row in table_rows:
                                    # Get all cells in this row
                                    cells = row.find_all('td')
                                    if not cells or len(cells) == 0:
                                        # This could be a header row, skip it
                                        continue
                                    
                                    # Process only the first cell of the row
                                    first_cell = cells[0]
                                    
                                    # Check if the cell has a link
                                    pdf_link = first_cell.find('a')
                                    
                                    if not pdf_link:
                                        print(f"⚠️ Empty first cell found in row, no PDF link available")
                                        grade_empty_cells += 1
                                        continue
                                    
                                    # Get the PDF link
                                    pdf_url = pdf_link['href']
                                    
                                    try:
                                        pdf_response = requests.get(pdf_url)
                                        
                                        pdf_filename = os.path.join(subject_folder, f"file_{file_counter}.pdf")
                                        file_counter += 1  # Increment counter for next file
                                        
                                        try:
                                            with open(pdf_filename, 'wb') as f:
                                                f.write(pdf_response.content)
                                            print(f"✅ File downloaded from first cell: {pdf_filename}")
                                            grade_success_count += 1
                                        except Exception as e:
                                            print(f"❌ Error saving file: {e}, skipping...")
                                            grade_fail_count += 1
                                    except Exception as e:
                                        print(f"❌ Error downloading file: {e}, skipping...")
                                        grade_fail_count += 1
                            
                        continue
                        
                    print(f"🔍 Found {len(contents_containers)} content containers")
                    
                    for container_index, content_container in enumerate(contents_containers):
                        print(f"📄 Processing content container {container_index + 1}/{len(contents_containers)}")
                        
                        content_link_element = content_container.find('a')
                        if not content_link_element:
                            print(f"❌ No content link found in this container, skipping...")
                            continue
                        
                        content_page_url = content_link_element['href']
                    
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
                            
                            # Check for tables in the article content
                            tables = article_content.find_all('table')
                            
                            if tables:
                                for table in tables:
                                    # Find all rows in the table
                                    table_rows = table.find_all('tr')
                                    
                                    print(f"📋 Found {len(table_rows)} rows in table")
                                    for row in table_rows:
                                        # Get all cells in this row
                                        cells = row.find_all('td')
                                        if not cells or len(cells) == 0:
                                            # This could be a header row, skip it
                                            continue
                                        
                                        # Process only the first cell of the row
                                        first_cell = cells[0]
                                        
                                        # Check if the cell has a link
                                        pdf_link = first_cell.find('a')
                                        
                                        if not pdf_link:
                                            print(f"⚠️ Empty first cell found in row, no PDF link available")
                                            grade_empty_cells += 1
                                            continue
                                        
                                        # Get the PDF link
                                        pdf_url = pdf_link['href']
                                        
                                        try:
                                            pdf_response = requests.get(pdf_url)
                                            
                                            pdf_filename = os.path.join(subject_folder, f"file_{file_counter}.pdf")
                                            file_counter += 1  # Increment counter for next file
                                            
                                            try:
                                                with open(pdf_filename, 'wb') as f:
                                                    f.write(pdf_response.content)
                                                print(f"✅ File downloaded from first cell: {pdf_filename}")
                                                grade_success_count += 1
                                            except Exception as e:
                                                print(f"❌ Error saving file: {e}, skipping...")
                                                grade_fail_count += 1
                                        except Exception as e:
                                            print(f"❌ Error downloading file: {e}, skipping...")
                                            grade_fail_count += 1
                            else:
                                # No tables found, continue with the original logic
                                download_link_element = article_content.find('a')
                                if not download_link_element:
                                    print(f"❌ No download link found in entry content, skipping...")
                                    continue
                                
                                pdf_download_url = download_link_element['href']
                                print(f"⬇️ Found download link")
                            
                                try:
                                    pdf_response = requests.get(pdf_download_url)
                                    
                                    # Numbered filename in the subject folder inside grade folder
                                    pdf_filename = os.path.join(subject_folder, f"file_{file_counter}.pdf")
                                    file_counter += 1  # Increment counter for next file
                                
                                    try:
                                        with open(pdf_filename, 'wb') as f:
                                            f.write(pdf_response.content)
                                        print(f"✅ File downloaded: {pdf_filename}")
                                        grade_success_count += 1
                                    except Exception as e:
                                        print(f"❌ Error saving file: {e}, skipping...")
                                        grade_fail_count += 1
                                    
                                except Exception as e:
                                    print(f"❌ Error downloading file: {e}, skipping...")
                                    grade_fail_count += 1
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
        
        # Update total counters
        total_success_count += grade_success_count
        total_fail_count += grade_fail_count
        total_empty_cells += grade_empty_cells
        
        # Print summary for this grade
        print(f"\n=== Grade {grade_name} Summary ===")
        print(f"✅ Successfully downloaded: {grade_success_count} files")
        print(f"❌ Failed downloads: {grade_fail_count} files")
        print(f"⚠️ Empty first cells: {grade_empty_cells}")
        print(f"📁 Total files attempted: {grade_success_count + grade_fail_count}")
        
    except Exception as e:
        print(f"❌ Error processing grade page: {e}, skipping to next grade...")
    
    # Add a small delay before processing next grade
    time.sleep(2)

# Print final summary
print("\n\n" + "="*50)
print("=== FINAL SCRAPING SUMMARY ===")
print(f"✅ Total successful downloads across all grades: {total_success_count}")
print(f"❌ Total failed downloads across all grades: {total_fail_count}")
print(f"⚠️ Total empty first cells across all grades: {total_empty_cells}")
print(f"📁 Total files attempted: {total_success_count + total_fail_count}")
print("Scraping completed!")
print("="*50)