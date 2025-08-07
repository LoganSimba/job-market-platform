import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
import re

class IndeedScraper:
    def __init__(self):
        self.base_url = "https://www.indeed.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Tech skills to look for in job descriptions
        self.tech_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'React', 'Angular', 'Vue',
            'Node.js', 'Django', 'Flask', 'FastAPI', 'SQL', 'PostgreSQL', 'MySQL',
            'MongoDB', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
            'Git', 'Linux', 'REST API', 'GraphQL', 'HTML', 'CSS', 'TypeScript',
            'Machine Learning', 'Data Science', 'Pandas', 'NumPy', 'TensorFlow',
            'PyTorch', 'Scikit-learn', 'Agile', 'Scrum', 'CI/CD', 'Jenkins'
        ]
    
    def build_search_url(self, job_title, location, start=0):
        """Build Indeed search URL"""
        job_title = job_title.replace(' ', '+')
        location = location.replace(' ', '+').replace(',', '%2C')
        
        url = f"{self.base_url}/jobs?q={job_title}&l={location}&start={start}"
        return url
    
    def extract_salary_info(self, salary_text):
        """Extract salary min/max from salary string"""
        if not salary_text:
            return None, None, salary_text
        
        # Remove extra whitespace and common words
        salary_text = re.sub(r'\s+', ' ', salary_text.strip())
        
        # Look for salary ranges like "$60,000 - $80,000" or "$60K - $80K"
        range_pattern = r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)[Kk]?\s*[-–]\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)[Kk]?'
        range_match = re.search(range_pattern, salary_text)
        
        if range_match:
            min_sal = float(range_match.group(1).replace(',', ''))
            max_sal = float(range_match.group(2).replace(',', ''))
            
            # Convert K to thousands
            if 'k' in salary_text.lower():
                min_sal *= 1000
                max_sal *= 1000
                
            return min_sal, max_sal, salary_text
        
        # Look for single salary like "$75,000" or "$75K"
        single_pattern = r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)[Kk]?'
        single_match = re.search(single_pattern, salary_text)
        
        if single_match:
            salary = float(single_match.group(1).replace(',', ''))
            if 'k' in salary_text.lower():
                salary *= 1000
            return salary, salary, salary_text
        
        return None, None, salary_text
    
    def extract_skills(self, description):
        """Extract technical skills from job description"""
        if not description:
            return ""
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in self.tech_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return ", ".join(found_skills)
    
    def determine_remote_type(self, location, description):
        """Determine if job is remote, hybrid, or on-site"""
        location_lower = location.lower() if location else ""
        desc_lower = description.lower() if description else ""
        
        remote_keywords = ['remote', 'work from home', 'wfh', 'telecommute']
        hybrid_keywords = ['hybrid', 'flexible', 'part remote']
        
        for keyword in remote_keywords:
            if keyword in location_lower or keyword in desc_lower:
                return "Remote"
        
        for keyword in hybrid_keywords:
            if keyword in location_lower or keyword in desc_lower:
                return "Hybrid"
        
        return "On-site"
    
    def scrape_job_listings(self, job_title, location, max_pages=3):
        """Scrape job listings from Indeed"""
        jobs = []
        
        print(f"🔍 Searching for '{job_title}' jobs in '{location}'...")
        
        for page in range(max_pages):
            start = page * 10  # Indeed shows 10 jobs per page
            url = self.build_search_url(job_title, location, start)
            
            print(f"📄 Scraping page {page + 1}...")
            
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                if not job_cards:
                    print(f"⚠️ No job cards found on page {page + 1}")
                    break
                
                for card in job_cards:
                    try:
                        job_data = self.extract_job_data(card)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        print(f"⚠️ Error extracting job data: {e}")
                        continue
                
                # Random delay to be respectful
                time.sleep(random.uniform(1, 3))
                
            except requests.RequestException as e:
                print(f"❌ Error scraping page {page + 1}: {e}")
                break
        
        print(f"✅ Found {len(jobs)} jobs for '{job_title}' in '{location}'")
        return jobs
    
    def extract_job_data(self, job_card):
        """Extract data from a single job card"""
        try:
            # Job title and URL
            title_elem = job_card.find('h2', class_='jobTitle')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a')
            if title_link:
                title = title_link.get_text(strip=True)
                job_url = urljoin(self.base_url, title_link.get('href', ''))
            else:
                title = title_elem.get_text(strip=True)
                job_url = None
            
            # Company name
            company_elem = job_card.find('span', class_='companyName')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Location
            location_elem = job_card.find('div', class_='companyLocation')
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            # Salary
            salary_elem = job_card.find('span', class_='metadata')
            salary_text = salary_elem.get_text(strip=True) if salary_elem else None
            salary_min, salary_max, salary_original = self.extract_salary_info(salary_text)
            
            # Job description snippet
            summary_elem = job_card.find('div', class_='summary')
            description = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Extract skills and remote type
            skills = self.extract_skills(description)
            remote_type = self.determine_remote_type(location, description)
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_text': salary_original,
                'skills': skills,
                'description': description,
                'url': job_url,
                'remote': remote_type
            }
            
        except Exception as e:
            print(f"⚠️ Error extracting job data: {e}")
            return None

# Test function
if __name__ == "__main__":
    scraper = IndeedScraper()
    
    # Test with a simple search
    jobs = scraper.scrape_job_listings("Python Developer", "Boston, MA", max_pages=2)
    
    print(f"\n📊 Sample results:")
    for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
        print(f"\n{i+1}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job['salary_text']}")
        print(f"   Skills: {job['skills']}")
        print(f"   Remote: {job['remote']}")