import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_project.settings')
django.setup()

from resumeapp.models import JobDescription

def seed_jobs():
    jobs_data = [
        {
            'title': 'Python Developer',
            'company': 'TechSol Solutions',
            'description': 'We are seeking a Python Developer to build and optimize backend applications. You will collaborate with design teams, integrate frontend elements, and write clean, structured code. Experience with REST APIs and databases is required.',
            'required_skills': 'python, django, sql, git, html, css, bootstrap',
            'experience_required': 1,
            'location': 'Mumbai, India'
        },
        {
            'title': 'Backend Developer',
            'company': 'NextGen Systems',
            'description': 'Looking for a Backend Developer skilled in server-side technologies. The ideal candidate will design databases, maintain microservices, deploy containers, and optimize web app queries for low latency. Experience with MVC patterns is a plus.',
            'required_skills': 'python, django, postgresql, redis, docker, git, nginx',
            'experience_required': 2,
            'location': 'Bangalore, India'
        },
        {
            'title': 'Data Analyst',
            'company': 'DataMetrics Corp',
            'description': 'Join our analytics team to process massive datasets, draw visualizations, and generate business reports. You will work with relational databases and construct machine learning workflows for data pipelines.',
            'required_skills': 'python, pandas, numpy, sql, matplotlib, seaborn, data analysis',
            'experience_required': 1,
            'location': 'Remote, India'
        },
        {
            'title': 'Machine Learning Engineer',
            'company': 'AIBrain Labs',
            'description': 'We are looking for a Machine Learning Engineer to design and train artificial intelligence systems. You will build NLP pipelines, optimize text similarity classifiers, and write mathematical packages to represent multi-dimensional vectors.',
            'required_skills': 'python, scikit-learn, machine learning, nlp, natural language processing, numpy, pandas, tensorflow, pytorch',
            'experience_required': 2,
            'location': 'Hyderabad, India'
        }
    ]

    print("Checking database for existing job descriptions...")
    for job in jobs_data:
        # Check if job already exists to prevent duplication
        exists = JobDescription.objects.filter(title=job['title'], company=job['company']).exists()
        if not exists:
            JobDescription.objects.create(
                title=job['title'],
                company=job['company'],
                description=job['description'],
                required_skills=job['required_skills'],
                experience_required=job['experience_required'],
                location=job['location']
            )
            print(f"Added Job: {job['title']} at {job['company']}")
        else:
            print(f"Job already exists: {job['title']} at {job['company']}")
            
    print("Database seeding completed!")

if __name__ == '__main__':
    seed_jobs()
