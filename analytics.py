from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_, or_, case
from database import engine
from models.job import Job
import pandas as pd
from collections import Counter
import re

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class JobAnalytics:
    def __init__(self):
        self.db = SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.db.close()
    
    def get_total_jobs_count(self):
        """Get total number of jobs in database"""
        return self.db.query(Job).count()
    
    def get_salary_insights(self, location=None, skill=None):
        """Get salary analysis with optional filters"""
        query = self.db.query(Job).filter(
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None)
        )
        
        # Apply filters
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        
        if skill:
            query = query.filter(Job.skills.ilike(f"%{skill}%"))
        
        jobs = query.all()
        
        if not jobs:
            return {
                'count': 0,
                'avg_salary': 0,
                'min_salary': 0,
                'max_salary': 0,
                'median_salary': 0
            }
        
        # Calculate salary statistics
        salaries = [(job.salary_min + job.salary_max) / 2 for job in jobs]
        
        return {
            'count': len(jobs),
            'avg_salary': round(sum(salaries) / len(salaries)),
            'min_salary': min(salaries),
            'max_salary': max(salaries),
            'median_salary': sorted(salaries)[len(salaries)//2]
        }
    
    def get_salary_by_location(self):
        """Get average salary by location"""
        query = self.db.query(
            Job.location,
            func.count(Job.id).label('job_count'),
            func.avg((Job.salary_min + Job.salary_max) / 2).label('avg_salary')
        ).filter(
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None)
        ).group_by(Job.location).order_by(func.avg((Job.salary_min + Job.salary_max) / 2).desc())
        
        results = []
        for location, count, avg_sal in query.all():
            results.append({
                'location': location,
                'job_count': count,
                'avg_salary': round(avg_sal) if avg_sal else 0
            })
        
        return results
    
    def get_top_skills(self, limit=20):
        """Get most mentioned skills with job counts and salary impact"""
        # Get all skills from all jobs
        all_skills = []
        skill_salaries = {}
        
        jobs = self.db.query(Job).filter(
            Job.skills.isnot(None),
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None)
        ).all()
        
        for job in jobs:
            if job.skills:
                job_skills = [skill.strip() for skill in job.skills.split(',')]
                avg_salary = (job.salary_min + job.salary_max) / 2
                
                for skill in job_skills:
                    if skill:  # Skip empty skills
                        all_skills.append(skill)
                        if skill not in skill_salaries:
                            skill_salaries[skill] = []
                        skill_salaries[skill].append(avg_salary)
        
        # Count skill occurrences
        skill_counts = Counter(all_skills)
        
        # Calculate average salary for each skill
        results = []
        for skill, count in skill_counts.most_common(limit):
            if skill in skill_salaries and len(skill_salaries[skill]) > 0:
                avg_salary = sum(skill_salaries[skill]) / len(skill_salaries[skill])
                results.append({
                    'skill': skill,
                    'job_count': count,
                    'avg_salary': round(avg_salary),
                    'percentage': round((count / len(jobs)) * 100, 1)
                })
        
        return results
    
    def get_location_insights(self):
        """Get comprehensive location analysis"""
        query = self.db.query(
            Job.location,
            func.count(Job.id).label('total_jobs'),
            func.avg((Job.salary_min + Job.salary_max) / 2).label('avg_salary'),
            func.sum(case((Job.remote == 'Remote', 1), else_=0)).label('remote_jobs'),
            func.sum(case((Job.remote == 'Hybrid', 1), else_=0)).label('hybrid_jobs')
        ).filter(
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None)
        ).group_by(Job.location)
        
        results = []
        for location, total, avg_sal, remote, hybrid in query.all():
            remote_percentage = round((remote / total) * 100, 1) if total > 0 else 0
            hybrid_percentage = round((hybrid / total) * 100, 1) if total > 0 else 0
            
            results.append({
                'location': location,
                'total_jobs': total,
                'avg_salary': round(avg_sal) if avg_sal else 0,
                'remote_jobs': remote,
                'hybrid_jobs': hybrid,
                'remote_percentage': remote_percentage,
                'hybrid_percentage': hybrid_percentage,
                'onsite_percentage': round(100 - remote_percentage - hybrid_percentage, 1)
            })
        
        # Sort by total jobs descending
        return sorted(results, key=lambda x: x['total_jobs'], reverse=True)

    def get_company_insights(self, limit=15):
        """Get top hiring companies with job counts and salary info"""
        query = self.db.query(
            Job.company,
            func.count(Job.id).label('job_count'),
            func.avg((Job.salary_min + Job.salary_max) / 2).label('avg_salary'),
            func.min((Job.salary_min + Job.salary_max) / 2).label('min_salary'),
            func.max((Job.salary_min + Job.salary_max) / 2).label('max_salary')
        ).filter(
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None)
        ).group_by(Job.company).order_by(func.count(Job.id).desc()).limit(limit)
        
        results = []
        for company, count, avg_sal, min_sal, max_sal in query.all():
            results.append({
                'company': company,
                'job_count': count,
                'avg_salary': round(avg_sal) if avg_sal else 0,
                'salary_range': f"${round(min_sal):,} - ${round(max_sal):,}" if min_sal and max_sal else "N/A"
            })
        
        return results

    def get_remote_work_trends(self):
        """Analyze remote work distribution"""
        query = self.db.query(
            Job.remote,
            func.count(Job.id).label('count'),
            func.avg((Job.salary_min + Job.salary_max) / 2).label('avg_salary')
        ).filter(
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None)
        ).group_by(Job.remote)
        
        total_jobs = self.db.query(Job).count()
        
        results = []
        for remote_type, count, avg_sal in query.all():
            percentage = round((count / total_jobs) * 100, 1) if total_jobs > 0 else 0
            results.append({
                'type': remote_type,
                'job_count': count,
                'percentage': percentage,
                'avg_salary': round(avg_sal) if avg_sal else 0
            })
        
        return sorted(results, key=lambda x: x['job_count'], reverse=True)
    
    def get_salary_comparison(self, locations_list):
        """Compare salaries across specific locations"""
        results = []
        
        for location in locations_list:
            insights = self.get_salary_insights(location=location)
            if insights['count'] > 0:
                results.append({
                    'location': location,
                    'job_count': insights['count'],
                    'avg_salary': insights['avg_salary'],
                    'salary_range': f"${insights['min_salary']:,.0f} - ${insights['max_salary']:,.0f}"
                })
        
        return sorted(results, key=lambda x: x['avg_salary'], reverse=True)
    
    def get_skill_salary_impact(self, base_skill="Python"):
        """Compare salaries with/without specific skill"""
        # Jobs WITH the skill
        with_skill = self.get_salary_insights(skill=base_skill)
        
        # Jobs WITHOUT the skill
        without_skill_query = self.db.query(Job).filter(
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None),
            ~Job.skills.ilike(f"%{base_skill}%")
        )
        
        without_jobs = without_skill_query.all()
        if without_jobs:
            without_salaries = [(job.salary_min + job.salary_max) / 2 for job in without_jobs]
            without_avg = sum(without_salaries) / len(without_salaries)
        else:
            without_avg = 0
        
        salary_difference = with_skill['avg_salary'] - without_avg if without_avg > 0 else 0
        percentage_increase = round((salary_difference / without_avg) * 100, 1) if without_avg > 0 else 0
        
        return {
        'skill': base_skill,
        'average_salary': with_skill['avg_salary'],  # Direct access
        'market_average': round(without_avg),        # Direct access
        'salary_difference': round(salary_difference),
        'percentage_increase': percentage_increase
    }
    
    def generate_market_summary(self):
        """Generate a comprehensive market summary"""
        total_jobs = self.get_total_jobs_count()
        overall_salary = self.get_salary_insights()
        top_skills = self.get_top_skills(5)
        top_locations = self.get_salary_by_location()[:5]
        remote_trends = self.get_remote_work_trends()
        
        return {
            'total_jobs': total_jobs,
            'avg_salary': overall_salary['avg_salary'],
            'salary_range': f"${overall_salary['min_salary']:,.0f} - ${overall_salary['max_salary']:,.0f}",
            'top_skills': [skill['skill'] for skill in top_skills],
            'highest_paying_location': top_locations[0]['location'] if top_locations else 'N/A',
            'remote_percentage': next((item['percentage'] for item in remote_trends if item['type'] == 'Remote'), 0)
        }

# Test function
if __name__ == "__main__":
    analytics = JobAnalytics()
    
    try:
        print("📊 Job Market Analytics Dashboard")
        print("=" * 50)
        
        # Market Summary
        summary = analytics.generate_market_summary()
        print(f"\n🎯 MARKET OVERVIEW:")
        print(f"   Total Jobs Analyzed: {summary['total_jobs']:,}")
        print(f"   Average Salary: ${summary['avg_salary']:,}")
        print(f"   Salary Range: {summary['salary_range']}")
        print(f"   Remote Work: {summary['remote_percentage']}% of jobs")
        
        # Top Skills
        print(f"\n🛠️  TOP SKILLS IN DEMAND:")
        top_skills = analytics.get_top_skills(10)
        for i, skill in enumerate(top_skills, 1):
            print(f"   {i}. {skill['skill']} - {skill['job_count']} jobs (${skill['avg_salary']:,} avg)")
        
        # Location Analysis
        print(f"\n📍 SALARY BY LOCATION:")
        locations = analytics.get_salary_by_location()[:8]
        for loc in locations:
            print(f"   {loc['location']}: ${loc['avg_salary']:,} avg ({loc['job_count']} jobs)")
        
        # Company Analysis
        print(f"\n🏢 TOP HIRING COMPANIES:")
        companies = analytics.get_company_insights(8)
        for comp in companies:
            print(f"   {comp['company']}: {comp['job_count']} jobs (${comp['avg_salary']:,} avg)")
        
        print(f"\n✅ Analytics complete! Ready to build your web dashboard.")
        
    finally:
        analytics.close()
