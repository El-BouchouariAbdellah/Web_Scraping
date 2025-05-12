from bs4 import BeautifulSoup
import requests
import time
import os

# Initialize global counters
total_success_count = 0
total_fail_count = 0

def create_folder(folder_path):
    """Create a folder if it doesn't exist"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ Created folder: {folder_path}")
        return True
    else:
        print(f"📁 Using existing folder: {folder_path}")
        return False

def download_file(url, save_path):
    """Download a file from URL and save it to the specified path"""
    try:
        response = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ File downloaded: {save_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading file: {e}, skipping...")
        return False

def extract_cell_link(cell):
    """Extract a link from a table cell"""
    try:
        link = cell.find('a')
        if link and 'href' in link.attrs:
            return link['href']
        return None
    except Exception as e:
        print(f"❌ Error extracting cell link: {e}")
        return None

def process_table_for_downloads(table, save_folder, file_counter):
    """Process a table to extract and download first and second cell links from each row"""
    success_count = 0
    fail_count = 0
    
    try:
        rows = table.find_all('tr')
        for row_index, row in enumerate(rows):
            cells = row.find_all('td')
            
            # Skip rows with no cells or just one cell
            if len(cells) < 1:
                continue
                
            # Process first cell in each row
            if len(cells) >= 1:
                url = extract_cell_link(cells[0])
                if url:
                    pdf_filename = os.path.join(save_folder, f"file_{file_counter}_first_cell.pdf")
                    if download_file(url, pdf_filename):
                        success_count += 1
                    else:
                        fail_count += 1
                    file_counter += 1
            
            # Process second cell in each row if it exists
            if len(cells) >= 2:
                url = extract_cell_link(cells[1])
                if url:
                    pdf_filename = os.path.join(save_folder, f"file_{file_counter}_second_cell.pdf")
                    if download_file(url, pdf_filename):
                        success_count += 1
                    else:
                        fail_count += 1
                    file_counter += 1
    except Exception as e:
        print(f"❌ Error processing table rows: {e}")
    
    return success_count, fail_count, file_counter

def process_html_tables(html_content, save_folder, file_counter):
    """Process all tables in HTML content for downloads"""
    success_count = 0
    fail_count = 0
    
    soup = BeautifulSoup(html_content, 'lxml')
    tables = soup.find_all('table')
    
    print(f"Found {len(tables)} tables to process")
    
    for table_index, table in enumerate(tables):
        print(f"Processing table {table_index + 1}/{len(tables)}")
        table_success, table_fail, file_counter = process_table_for_downloads(table, save_folder, file_counter)
        success_count += table_success
        fail_count += table_fail
    
    return success_count, fail_count, file_counter

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
        
    grade_name = grade_link_element.text.strip()
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
        file_counter = 1
        
        # Process each subject within this grade
        for subject_index, subject_element in enumerate(subject_elements):
            try:
                print(f"\nProcessing subject {subject_index + 1}/{len(subject_elements)}")
                subject_link_element = subject_element.find('a')
                if not subject_link_element:
                    print(f"❌ No link found for this subject, skipping...")
                    continue
                    
                subject_name = subject_link_element.text.strip()
                print(f"Subject: {subject_name}")
                
                # Create a subject folder inside the grade folder
                subject_folder = os.path.join(grade_folder, subject_name)
                create_folder(subject_folder)
                
                subject_page_url = subject_link_element['href']
                try:
                    subject_page_html = requests.get(subject_page_url).text
                    subject_page_soup = BeautifulSoup(subject_page_html, 'lxml')
                                        
                    # First try to process tables directly
                    tables = subject_page_soup.find_all('table')
                    if tables:
                        print(f"Found {len(tables)} tables to process directly")
                        for table_index, table in enumerate(tables):
                            print(f"Processing table {table_index + 1}/{len(tables)}")
                            success, fail, file_counter = process_table_for_downloads(table, subject_folder, file_counter)
                            grade_success_count += success
                            grade_fail_count += fail
                    
                    # Find all elements with class "medium-8 column"
                    contents_containers = subject_page_soup.find_all('li', 'medium-8 column')
                    
                    
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
                                print(f"⚠️ This page doesn't have any lessons, skipping...")
                                continue
                            
                            # Try to process tables in this content page
                            tables = content_page_soup.find_all('table')
                            if tables:  
                                print(f"Found {len(tables)} tables in content page")
                                for table in tables:
                                    success, fail, file_counter = process_table_for_downloads(
                                        table, subject_folder, file_counter
                                    )
                                    grade_success_count += success
                                    grade_fail_count += fail
                                continue
                                
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
        
        # Print summary for this grade
        print(f"\n=== Grade {grade_name} Summary ===")
        print(f"✅ Successfully downloaded: {grade_success_count} files")
        print(f"❌ Failed downloads: {grade_fail_count} files")
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
print(f"📁 Total files attempted: {total_success_count + total_fail_count}")
print("Scraping completed!")
print("="*50)