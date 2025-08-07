import random
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from database import engine, create_tables
from models.job import Job

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class JobDataGenerator:
    def __init__(self):
        # Your target locations with salary multipliers
        self.locations = {
            "Portland, ME": 0.85,
            "Bangor, ME": 0.80,
            "Augusta, ME": 0.82,
            "Boston, MA": 1.15,
            "Cambridge, MA": 1.20,
            "Worcester, MA": 0.95,
            "Manchester, NH": 0.90,
            "Burlington, VT": 0.88,
            "Hartford, CT": 1.00,
            "Providence, RI": 0.95,
            "New York, NY": 1.25,
            "San Francisco, CA": 1.40,
            "Austin, TX": 1.05,
            "Seattle, WA": 1.20,
            "Remote": 1.10
        }
        
        # Tech job titles with base salaries
        self.job_titles = {
            "Software Engineer Intern": 75000,
            "Python Developer": 85000,
            "Full Stack Developer": 90000,
            "Frontend Developer": 80000,
            "Backend Developer": 88000,
            "Data Analyst": 75000,
            "Software Developer": 85000,
            "React Developer": 82000,
            "JavaScript Developer": 83000,
            "Junior Software Engineer": 70000,
            "Web Developer": 75000,
            "DevOps Engineer": 95000,
            "Machine Learning Engineer": 105000,
            "Data Scientist": 100000,
        }
        
        # Mix of companies (realistic for New England + major tech)
        self.companies = [
            # New England companies
            "Liberty Mutual", "Fidelity Investments", "Raytheon", "TripAdvisor",
            "Wayfair", "HubSpot", "CarGurus", "Toast", "DataRobot", "PTC",
            "Akamai", "iRobot", "LogMeIn", "Carbonite", "Brightcove",
            
            # Maine/Regional companies  
            "IDEXX", "WEX", "Tilson", "Kepware", "Critical Insights",
            "Tyler Technologies", "Machias Savings Bank", "ImmuCell",
            
            # Major tech (remote/satellite offices)
            "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix",
            "Spotify", "Slack", "Zoom", "Salesforce", "Adobe", "Oracle",
            
            # Startups/Scale-ups
            "TechCorp", "DataFlow Solutions", "CloudTech Inc", "WebSolutions",
            "InnovateLabs", "CodeCraft", "DevStream", "TechNova",
            "ByteWorks", "StackFlow", "AppForge", "DataVault"
        ]
        
        # Technical skills with frequency weights
        self.skills_pool = {
            "Python": 0.7, "JavaScript": 0.8, "React": 0.6, "Java": 0.5,
            "SQL": 0.8, "Git": 0.9, "HTML": 0.7, "CSS": 0.7,
            "Node.js": 0.5, "PostgreSQL": 0.4, "AWS": 0.6, "Docker": 0.4,
            "TypeScript": 0.4, "Django": 0.3, "Flask": 0.3, "FastAPI": 0.2,
            "Vue.js": 0.3, "Angular": 0.4, "MongoDB": 0.3, "Redis": 0.2,
            "Linux": 0.4, "REST API": 0.6, "GraphQL": 0.2, "Kubernetes": 0.2,
            "Azure": 0.3, "GCP": 0.2, "Jenkins": 0.2, "Pandas": 0.3,
            "NumPy": 0.2, "Machine Learning": 0.3, "TensorFlow": 0.1,
            "Agile": 0.5, "Scrum": 0.4, "CI/CD": 0.3
        }
        
        # Job descriptions templates
        self.description_templates = [
            "Join our team to develop innovative software solutions using modern technologies. Work on exciting projects that impact millions of users.",
            "We're seeking a talented developer to build scalable web applications and contribute to our growing platform.",
            "Exciting opportunity to work with cutting-edge technology in a collaborative environment. Build the future of digital solutions.",
            "Join a fast-growing company where you'll design and implement robust software systems that drive business growth.",
            "Work on challenging problems with a team of experienced engineers. Opportunity to learn and grow your technical skills.",
            "Build high-performance applications that serve thousands of users daily. Work with modern tech stack and best practices.",
            "Contribute to an innovative platform that's transforming the industry. Great opportunity for career development.",
            "Join our engineering team to create solutions that make a real difference. Work with latest frameworks and tools."
        ]
    
    def generate_skills(self):
        """Generate realistic skill combinations for a job"""
        selected_skills = []
        
        for skill, probability in self.skills_pool.items():
            if random.random() < probability:
                selected_skills.append(skill)
        
        # Ensure at least 3 skills per job
        if len(selected_skills) < 3:
            remaining_skills = [s for s in self.skills_pool.keys() if s not in selected_skills]
            selected_skills.extend(random.sample(remaining_skills, 3 - len(selected_skills)))
        
        return ", ".join(selected_skills)
    
    def calculate_salary(self, base_salary, location):
        """Calculate salary based on location and add some randomness"""
        location_multiplier = self.locations.get(location, 1.0)
        
        # Apply location multiplier
        adjusted_salary = base_salary * location_multiplier
        
        # Add random variation (±15%)
        variation = random.uniform(0.85, 1.15)
        final_salary = int(adjusted_salary * variation)
        
        # Round to nearest 1000
        return round(final_salary, -3)
    
    def determine_remote_type(self, location):
        """Determine if job is remote, hybrid, or on-site"""
        if location == "Remote":
            return "Remote"
        elif random.random() < 0.15:  # 15% chance of hybrid
            return "Hybrid"
        elif random.random() < 0.05:  # 5% chance of remote even for location-specific jobs
            return "Remote"
        else:
            return "On-site"
    
    def generate_job_data(self):
        """Generate a single realistic job posting"""
        # Pick random components
        title = random.choice(list(self.job_titles.keys()))
        company = random.choice(self.companies)
        location = random.choice(list(self.locations.keys()))
        
        # Calculate salary
        base_salary = self.job_titles[title]
        salary = self.calculate_salary(base_salary, location)
         
        # Create salary range (±10K from base)
        salary_min = salary - random.randint(5000, 10000)
        salary_max = salary + random.randint(5000, 15000)
        
        # Generate other fields
        skills = self.generate_skills()
        description = random.choice(self.description_templates)
        remote_type = self.determine_remote_type(location)
        
        # Generate realistic posting date (last 30 days)
        days_ago = random.randint(1, 30)
        date_posted = datetime.now() - timedelta(days=days_ago)
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'salary_text': f"${salary_min:,} - ${salary_max:,}",
            'skills': skills,
            'description': description,
            'url': f"https://example-jobs.com/job/{random.randint(100000, 999999)}",
            'remote': remote_type,
            'date_posted': date_posted
        }
    
    def generate_and_save_jobs(self, num_jobs=500):
        """Generate multiple jobs and save to database"""
        # Ensure database tables exist
        create_tables()
        
        db = SessionLocal()
        
        try:
            print(f"🎲 Generating {num_jobs} realistic job postings...")
            
            jobs_created = 0
            for i in range(num_jobs):
                job_data = self.generate_job_data()
                
                # Create Job object
                job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    salary_min=job_data['salary_min'],
                    salary_max=job_data['salary_max'],
                    salary_text=job_data['salary_text'],
                    skills=job_data['skills'],
                    description=job_data['description'],
                    url=job_data['url'],
                    remote=job_data['remote'],
                    date_posted=job_data['date_posted']
                )
                
                db.add(job)
                jobs_created += 1
                
                # Show progress
                if (i + 1) % 50 == 0:
                    print(f"  ✅ Generated {i + 1} jobs...")
            
            # Commit all jobs to database
            db.commit()
            print(f"🎉 Successfully created {jobs_created} job postings!")
            
            # Show some sample data
            self.show_sample_data(db)
            
        except Exception as e:
            print(f"❌ Error generating jobs: {e}")
            db.rollback()
        finally:
            db.close()
    
    def show_sample_data(self, db):
        """Display sample of generated data"""
        print(f"\n📊 Sample Job Data:")
        sample_jobs = db.query(Job).limit(5).all()
        
        for i, job in enumerate(sample_jobs, 1):
            print(f"\n{i}. {job.title} at {job.company}")
            print(f"   📍 {job.location} ({job.remote})")
            print(f"   💰 {job.salary_text}")
            print(f"   🛠️  Skills: {job.skills[:50]}...")
        
        # Show statistics
        total_jobs = db.query(Job).count()
        avg_salary = db.query(Job).filter(Job.salary_min.isnot(None)).with_entities(
            ((Job.salary_min + Job.salary_max) / 2).label('avg')
        ).subquery()
        
        print(f"\n📈 Database Statistics:")
        print(f"   Total Jobs: {total_jobs}")
        print(f"   Locations: {len(set([job.location for job in db.query(Job).all()]))}")
        print(f"   Companies: {len(set([job.company for job in db.query(Job).all()]))}")

# Main execution
if __name__ == "__main__":
    generator = JobDataGenerator()
    generator.generate_and_save_jobs(500)  # Generate 500 jobs