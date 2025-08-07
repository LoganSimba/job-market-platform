from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from analytics import JobAnalytics
import uvicorn

# Create FastAPI app
app = FastAPI(title="Job Market Intelligence Platform")

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize analytics
analytics = JobAnalytics()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page with live analytics"""
    try:
        summary = analytics.generate_market_summary()
        top_skills = analytics.get_top_skills(10)

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "summary": summary,
            "top_skills": top_skills
            
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Error loading dashboard: {str(e)}</h1>", status_code=500)



@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Simple test page"""
    return templates.TemplateResponse("test.html", {
        "request": request,
        "message": "Hello World!",
        "total_jobs": 1000
    })





@app.get("/api/skills")
async def get_skills_data():
    """API endpoint for skills data"""
    try:
        skills = analytics.get_top_skills(15)
        return {"skills": skills}
    except Exception as e:
        return {"error": str(e)}

@app.get("/salaries", response_class=HTMLResponse)
async def salaries_page(request: Request):
    """Salary analysis page (template-rendered)"""
    try:
        locations = analytics.get_salary_by_location()
        comparison = analytics.get_salary_comparison([
            "Boston, MA", "San Francisco, CA", "New York, NY", "Portland, ME", "Remote"
        ])

        return templates.TemplateResponse("salaries.html", {
            "request": request,
            "locations": locations,
            "comparison": comparison
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)



@app.get("/companies", response_class=HTMLResponse)
async def companies(request: Request):
    analytics = JobAnalytics()
    companies = analytics.get_company_insights()
    
    # DEBUG: Let's see what we're getting
    print("DEBUG: Top 5 companies:")
    for i, company in enumerate(companies[:5]):
        print(f"  {i+1}. {company['company']} - {company['job_count']} jobs")
    print(f"DEBUG: Total companies returned: {len(companies)}")
    
    analytics.close()
    return templates.TemplateResponse("companies.html", {
        "request": request,
        "companies": companies
    })








@app.get("/api/market-summary")
async def get_market_summary():
    """API endpoint for overall market summary"""
    try:
        summary = analytics.generate_market_summary()
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}


@app.get("/skills", response_class=HTMLResponse)
async def skills_page(request: Request, skill: str = "Python"):  # Add skill parameter with default
    """Skills analysis page with dynamic skill search"""
    try:
        skills = analytics.get_top_skills(20)
        
        # Use the searched skill instead of hardcoded "Python"
        skill_impact = analytics.get_skill_salary_impact(skill)
        
        # DEBUG: See what we're getting
        print(f"DEBUG: Analyzing skill '{skill}'")
        print(f"DEBUG: skill_impact = {skill_impact}")
        
        return templates.TemplateResponse("skills.html", {
            "request": request,
            "skills": skills,
            "python_impact": skill_impact,  # Keep same variable name for now
            "current_skill": skill  # Add this so template knows which skill we're showing
        })
    except Exception as e:
        print(f"ERROR in skills_page: {e}")
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)




@app.get("/salaries", response_class=HTMLResponse)
async def salaries_page(request: Request):
    """Salary analysis page"""
    try:
        locations = analytics.get_salary_by_location()
        
        # Compare key locations
        key_locations = ["Boston, MA", "San Francisco, CA", "New York, NY", "Portland, ME", "Remote"]
        comparison = analytics.get_salary_comparison(key_locations)
        
        return templates.TemplateResponse("salaries.html", {
            "request": request,
            "locations": locations,
            "comparison": comparison
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

@app.get("/companies", response_class=HTMLResponse)
async def companies_page(request: Request):
    """Company analysis page"""
    try:
        companies = analytics.get_company_insights(25)
        location_insights = analytics.get_location_insights()
        
        return templates.TemplateResponse("companies.html", {
            "request": request,
            "companies": companies,
            "location_insights": location_insights
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

@app.get("/trends", response_class=HTMLResponse)
async def trends_page(request: Request):
    """Market trends page"""
    try:
        remote_trends = analytics.get_remote_work_trends()
        location_insights = analytics.get_location_insights()
        
        return templates.TemplateResponse("trends.html", {
            "request": request,
            "remote_trends": remote_trends,
            "location_insights": location_insights
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)