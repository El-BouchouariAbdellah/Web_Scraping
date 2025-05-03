from bs4 import BeautifulSoup
import requests
import time
import os

class MoutamadrisScraper:
    def __init__(self):
        self.base_url = 'https://moutamadris.ma'
        self.success_count = 0
        self.fail_count = 0
        
    def create_folder(self, folder_path):
        """Create a folder if it doesn't exist"""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"✅ Created folder: {folder_path}")
        else:
            print(f"📁 Using existing folder: {folder_path}")
    
    def get_soup(self, url):
        """Get BeautifulSoup object from a URL"""
        try:
            response = requests.get(url)
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"❌ Error fetching URL {url}: {e}")
            return None
    
    def download_file(self, url, save_path):
        """Download a file from URL and save it to the specified path"""
        try:
            response = requests.get(url)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ File downloaded: {save_path}")
            self.success_count += 1
            return True
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
            self.fail_count += 1
            return False
    
    def process_tableone(self, table, subject_folder, file_counter):
        """Process a tableone element to find and download PDF files"""
        links = table.find_all('a')
        if not links:
            print("❌ No lesson links found in table")
            return file_counter
            
        print(f"🔗 Found {len(links)} lesson links in table")
        for link in links:
            download_url = link['href']
            pdf_filename = os.path.join(subject_folder, f"file_{file_counter}.pdf")
            if self.download_file(download_url, pdf_filename):
                file_counter += 1
                
        return file_counter
    
    def process_table_responsive(self, div, subject_folder, file_counter):
        """Process a table-responsive div to find and download PDF files"""
        links = div.find_all('a')
        if not links:
            print("❌ No lesson links found in responsive table")
            return file_counter
            
        print(f"🔗 Found {len(links)} lesson links")
        for link in links:
            download_url = link['href']
            pdf_filename = os.path.join(subject_folder, f"file_{file_counter}.pdf")
            if self.download_file(download_url, pdf_filename):
                file_counter += 1
                
        return file_counter
    
    def process_content_container(self, container, subject_folder, file_counter):
        """Process a content container to find and download PDF files"""
        content_link = container.find('a')
        if not content_link:
            print("❌ No content link found in container")
            return file_counter
            
        content_url = content_link['href']
        #print(f"🔗 Found content page URL: {content_url}")
        
        content_soup = self.get_soup(content_url)
        if not content_soup:
            return file_counter
            
        # Check for "mawad" class in the content page
        if content_soup.find(class_="mawad"):
            print("⚠️ This page doesn't have any lessons, skipping...")
            return file_counter
            
        article_content = content_soup.find('div', class_="entry-content")
        if not article_content:
            print("❌ No article content found")
            return file_counter
            
        download_link = article_content.find('a')
        if not download_link:
            print("❌ No download link found in entry content")
            return file_counter
            
        pdf_url = download_link['href']
        #print(f"⬇️ Found download link: {pdf_url}")
        
        pdf_filename = os.path.join(subject_folder, f"file_{file_counter}.pdf")
        if self.download_file(pdf_url, pdf_filename):
            file_counter += 1
            
        return file_counter
    
    def process_subject(self, subject_element, grade_folder):
        """Process a subject to find and download all its content"""
        subject_link = subject_element.find('a')
        if not subject_link:
            print("❌ No link found for this subject, skipping...")
            return
            
        subject_name = subject_link.text
        print(f"Subject: {subject_name}")
        
        # Create subject folder
        subject_folder = os.path.join(grade_folder, subject_name)
        self.create_folder(subject_folder)
        
        subject_url = subject_link['href']
        subject_soup = self.get_soup(subject_url)
        if not subject_soup:
            return
            
        # Check if this subject has no lessons
        if subject_soup.find(class_="mawad"):
            print("⚠️ This subject doesn't have any lessons on this website, skipping...")
            return
        
        file_counter = 1
        
        # Try to find content containers (regular path)
        contents_containers = subject_soup.find_all('li', 'medium-8 column')
        if contents_containers:
            print(f"🔍 Found {len(contents_containers)} content containers")
            for i, container in enumerate(contents_containers):
                print(f"📄 Processing content container {i + 1}/{len(contents_containers)}")
                file_counter = self.process_content_container(container, subject_folder, file_counter)
                time.sleep(0.5)  # Small delay between containers
            return
            
        # Alternative path 1: table-responsive divs (for French subject)
        print("🔍 No content containers found, checking table-responsive divs...")
        content_divs = subject_soup.find_all('div', 'table-responsive')
        if content_divs:
            for div in content_divs:
                file_counter = self.process_table_responsive(div, subject_folder, file_counter)
            return
                
        # Alternative path 2: tableone tables
        print("❌ No table-responsive divs found, checking tableone tables...")
        tables = subject_soup.find_all('table', id='tableone')
        if tables:
            for table in tables:
                file_counter = self.process_tableone(table, subject_folder, file_counter)
        else:
            print("❌ No content found for this subject")
    
    def process_grade(self, grade_element, grade_index, total_grades):
        """Process a grade to find and download all its subjects"""
        grade_link = grade_element.find('a')
        if not grade_link:
            print("❌ No link found for this grade, skipping...")
            return
            
        grade_name = grade_link.text
        print(f"\n\n{'='*50}")
        print(f"Processing Grade {grade_index + 1}/{total_grades}: {grade_name}")
        print(f"{'='*50}")
        
        # Create grade folder
        self.create_folder(grade_name)
        
        # Reset counters for this grade
        grade_success_before = self.success_count
        grade_fail_before = self.fail_count
        
        # Get grade page and find subjects
        grade_url = grade_link['href']
        grade_soup = self.get_soup(grade_url)
        if not grade_soup:
            return
            
        subject_elements = grade_soup.find_all('li', 'mada')
        if not subject_elements:
            print(f"❌ No subjects found for grade: {grade_name}")
            return
            
        print(f"Found {len(subject_elements)} subjects in {grade_name}")
        
        # Process each subject
        for i, subject_element in enumerate(subject_elements):
            try:
                print(f"\nProcessing subject {i + 1}/{len(subject_elements)}")
                self.process_subject(subject_element, grade_name)
                time.sleep(1)  # Small delay between subjects
            except Exception as e:
                print(f"❌ General error processing subject: {e}, moving to next subject...")
        
        # Print summary for this grade
        grade_success = self.success_count - grade_success_before
        grade_fail = self.fail_count - grade_fail_before
        
        print(f"\n=== Grade {grade_name} Summary ===")
        print(f"✅ Successfully downloaded: {grade_success} files")
        print(f"❌ Failed downloads: {grade_fail} files")
        print(f"📁 Total files attempted: {grade_success + grade_fail}")
    
    def run(self):
        """Main method to run the scraper"""
        print("Starting scraper for moutamadris.ma")
        
        # Get all grades
        grades_soup = self.get_soup(f'{self.base_url}/cours/')
        if not grades_soup:
            print("Failed to fetch grades page")
            return
            
        grades_div = grades_soup.find('div', 'read')
        if not grades_div:
            print("Could not find grades container")
            return
            
        # Get only medium-6 column elements (to avoid downloading controls)
        grade_elements = grades_div.find_all('li', class_='medium-6 column')
        
        print(f"Found {len(grade_elements)} grades to process")
        
        # Process each grade
        for i, grade_element in enumerate(grade_elements):
            self.process_grade(grade_element, i, len(grade_elements))
            time.sleep(2)  # Small delay between grades
        
        # Print final summary
        print("\n\n" + "="*50)
        print("=== FINAL SCRAPING SUMMARY ===")
        print(f"✅ Total successful downloads: {self.success_count}")
        print(f"❌ Total failed downloads: {self.fail_count}")
        print(f"📁 Total files attempted: {self.success_count + self.fail_count}")
        print("Scraping completed!")
        print("="*50)


if __name__ == "__main__":
    scraper = MoutamadrisScraper()
    scraper.run()