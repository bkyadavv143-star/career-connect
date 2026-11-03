from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta
import os

from accounts.models import User, Company, CandidateProfile, EmployerProfile
from jobs.models import Job, Application
from notifications.models import Notification


def create_minimal_pdf(title, author, content_text):
    """Generates a valid minimalist PDF file in bytes without third-party dependencies."""
    pdf_template = f"""%PDF-1.4
1 0 obj
<<
  /Type /Catalog
  /Pages 2 0 R
>>
endobj
2 0 obj
<<
  /Type /Pages
  /Kids [3 0 R]
  /Count 1
>>
endobj
3 0 obj
<<
  /Type /Page
  /Parent 2 0 R
  /MediaBox [0 0 612 792]
  /Resources <<
    /Font <<
      /F1 4 0 R
    >>
  >>
  /Contents 5 0 R
>>
endobj
4 0 obj
<<
  /Type /Font
  /Subtype /Type1
  /BaseFont /Helvetica
>>
endobj
5 0 obj
<<
  /Length 120
>>
stream
BT
/F1 18 Tf
50 720 Td
({title}) Tj
/F1 12 Tf
0 -30 Td
(Author: {author}) Tj
0 -25 Td
(Summary: {content_text[:60]}) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000060 00000 n 
0000000117 00000 n 
0000000227 00000 n 
0000000297 00000 n 
trailer
<<
  /Size 6
  /Root 1 0 R
>>
startxref
468
%%EOF"""
    return pdf_template.encode('latin1')


class Command(BaseCommand):
    help = "Seed database with realistic initial data for CareerConnect Job Board"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting database seeding for CareerConnect..."))

        # 1. Admin Superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@careerconnect.com',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'phone': '+91 9800000001',
                'bio': 'Platform Administrator for CareerConnect Job Board.'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[+] Admin user created: admin / admin123"))

        # 2. Companies
        companies_data = [
            {
                'name': 'Google Cloud India',
                'website': 'https://cloud.google.com',
                'industry': 'Cloud & Enterprise Computing',
                'company_size': '500+',
                'headquarters': 'Bengaluru, Karnataka',
                'description': 'Google Cloud accelerates every organization’s ability to digitally transform its business with scalable infrastructure and AI platform services.',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg',
            },
            {
                'name': 'Microsoft India Development Center',
                'website': 'https://microsoft.com',
                'industry': 'Software & Artificial Intelligence',
                'company_size': '500+',
                'headquarters': 'Hyderabad, Telangana',
                'description': 'Microsoft IDC is one of Microsoft’s largest R&D centers outside Redmond, building cutting edge AI, Windows, and Azure technologies.',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg',
            },
            {
                'name': 'Amazon Web Services',
                'website': 'https://aws.amazon.com',
                'industry': 'Cloud Services & E-Commerce',
                'company_size': '500+',
                'headquarters': 'Bengaluru, Karnataka',
                'description': 'Amazon Web Services is the world’s most comprehensive and broadly adopted cloud platform, offering over 200 fully featured services.',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg',
            },
            {
                'name': 'Infosys Digital',
                'website': 'https://infosys.com',
                'industry': 'IT Services & Consulting',
                'company_size': '500+',
                'headquarters': 'Bengaluru, Karnataka',
                'description': 'A global leader in next-generation digital services and consulting, enabling clients across 56 countries to navigate digital transformation.',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg',
            },
            {
                'name': 'Razorpay Payments',
                'website': 'https://razorpay.com',
                'industry': 'FinTech & Digital Payments',
                'company_size': '201-500',
                'headquarters': 'Bengaluru, Karnataka',
                'description': 'Razorpay is India’s first full-stack financial solutions company powering business banking and payment gateways for millions of businesses.',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg',
            }
        ]

        companies = {}
        for cdata in companies_data:
            comp, _ = Company.objects.get_or_create(
                name=cdata['name'],
                defaults=cdata
            )
            companies[cdata['name']] = comp
        self.stdout.write(self.style.SUCCESS(f"[+] Created {len(companies)} verified partner companies"))

        # 3. Employers
        employers_data = [
            {
                'username': 'techlead_google',
                'email': 'lead@google.com',
                'first_name': 'Amitabh',
                'last_name': 'Kapur',
                'company': companies['Google Cloud India'],
                'designation': 'Engineering Director & Hiring Lead',
                'phone': '+91 9811223344',
            },
            {
                'username': 'hr_microsoft',
                'email': 'recruiting@microsoft.com',
                'first_name': 'Divya',
                'last_name': 'Nair',
                'company': companies['Microsoft India Development Center'],
                'designation': 'Principal Talent Acquisition Partner',
                'phone': '+91 9822334455',
            },
            {
                'username': 'aws_recruiter',
                'email': 'talent@amazon.com',
                'first_name': 'Rohan',
                'last_name': 'Deshmukh',
                'company': companies['Amazon Web Services'],
                'designation': 'Lead Cloud Recruiter',
                'phone': '+91 9833445566',
            },
            {
                'username': 'infosys_campus',
                'email': 'campus@infosys.com',
                'first_name': 'Meera',
                'last_name': 'Krishnan',
                'company': companies['Infosys Digital'],
                'designation': 'University Relations Lead',
                'phone': '+91 9844556677',
            },
            {
                'username': 'razorpay_hr',
                'email': 'careers@razorpay.com',
                'first_name': 'Arjun',
                'last_name': 'Mehta',
                'company': companies['Razorpay Payments'],
                'designation': 'Senior Tech Recruiter',
                'phone': '+91 9855667788',
            }
        ]

        employers = []
        for edata in employers_data:
            company = edata.pop('company')
            designation = edata.pop('designation')
            emp_user, created = User.objects.get_or_create(
                username=edata['username'],
                defaults={
                    'email': edata['email'],
                    'first_name': edata['first_name'],
                    'last_name': edata['last_name'],
                    'phone': edata['phone'],
                    'role': 'EMPLOYER',
                }
            )
            if created:
                emp_user.set_password('pass123')
                emp_user.save()

            EmployerProfile.objects.get_or_create(
                user=emp_user,
                defaults={
                    'company': company,
                    'designation': designation,
                }
            )
            employers.append(emp_user)
        self.stdout.write(self.style.SUCCESS(f"[+] Created {len(employers)} employer profiles (password: pass123)"))

        # 4. Candidates with resumes
        candidates_data = [
            {
                'username': 'rahul_sharma',
                'email': 'rahul.cse@example.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'phone': '+91 9911223344',
                'headline': 'Full-Stack Developer | Python, Django, React, REST APIs',
                'skills': 'Python, Django, React, JavaScript, PostgreSQL, Docker, Git, REST APIs',
                'education_degree': 'B.Tech in Computer Science & Engineering',
                'education_institution': 'National Institute of Technology (NIT)',
                'graduation_year': 2026,
                'cgpa_or_percentage': '8.8 CGPA',
                'experience_years': 1.5,
                'current_location': 'Bengaluru, India',
                'github_url': 'https://github.com/rahul-sharma-dev',
                'linkedin_url': 'https://linkedin.com/in/rahul-sharma-cse',
            },
            {
                'username': 'priya_patel',
                'email': 'priya.ai@example.com',
                'first_name': 'Priya',
                'last_name': 'Patel',
                'phone': '+91 9922334455',
                'headline': 'AI/ML Engineer | Deep Learning, NLP & Computer Vision',
                'skills': 'Python, PyTorch, TensorFlow, NLP, Scikit-Learn, Pandas, OpenCV, FastAPI',
                'education_degree': 'B.Tech in Artificial Intelligence & Data Science',
                'education_institution': 'Vellore Institute of Technology (VIT)',
                'graduation_year': 2025,
                'cgpa_or_percentage': '9.2 CGPA',
                'experience_years': 2.0,
                'current_location': 'Hyderabad, India',
                'github_url': 'https://github.com/priyapatel-ai',
                'linkedin_url': 'https://linkedin.com/in/priya-patel-ml',
            },
            {
                'username': 'aman_verma',
                'email': 'aman.cloud@example.com',
                'first_name': 'Aman',
                'last_name': 'Verma',
                'phone': '+91 9933445566',
                'headline': 'Cloud Solutions Architect & DevOps Engineer | AWS Certified',
                'skills': 'AWS, Kubernetes, Terraform, Docker, CI/CD, Linux, Python, Bash',
                'education_degree': 'B.Tech in Information Technology',
                'education_institution': 'Delhi Technological University (DTU)',
                'graduation_year': 2024,
                'cgpa_or_percentage': '8.5 CGPA',
                'experience_years': 2.5,
                'current_location': 'Delhi NCR, India',
                'github_url': 'https://github.com/aman-cloud',
                'linkedin_url': 'https://linkedin.com/in/aman-verma-cloud',
            },
            {
                'username': 'sneha_reddy',
                'email': 'sneha.frontend@example.com',
                'first_name': 'Sneha',
                'last_name': 'Reddy',
                'phone': '+91 9944556677',
                'headline': 'Frontend Engineer | Modern UI/UX, Next.js, TypeScript',
                'skills': 'React, Next.js, TypeScript, Tailwind CSS, Redux, UI/UX, Figma',
                'education_degree': 'B.Tech in Computer Science',
                'education_institution': 'BITS Pilani',
                'graduation_year': 2025,
                'cgpa_or_percentage': '8.9 CGPA',
                'experience_years': 1.0,
                'current_location': 'Bengaluru, India',
                'github_url': 'https://github.com/sneha-reddy-web',
                'linkedin_url': 'https://linkedin.com/in/sneha-reddy-frontend',
            },
            {
                'username': 'vikram_singh',
                'email': 'vikram.fresher@example.com',
                'first_name': 'Vikram',
                'last_name': 'Singh',
                'phone': '+91 9955667788',
                'headline': 'Aspiring Software Engineer | DSA, Java & Python Enthusiast',
                'skills': 'Java, Python, C++, Data Structures, Algorithms, SQL, HTML, CSS',
                'education_degree': 'B.Tech in Computer Science & Engineering',
                'education_institution': 'SRM Institute of Science and Technology',
                'graduation_year': 2026,
                'cgpa_or_percentage': '8.2 CGPA',
                'experience_years': 0.0,
                'current_location': 'Chennai, India',
                'github_url': 'https://github.com/vikram-singh-cse',
                'linkedin_url': 'https://linkedin.com/in/vikram-singh-tech',
            }
        ]

        candidates = []
        for cdata in candidates_data:
            headline = cdata.pop('headline')
            skills = cdata.pop('skills')
            education_degree = cdata.pop('education_degree')
            education_institution = cdata.pop('education_institution')
            graduation_year = cdata.pop('graduation_year')
            cgpa_or_percentage = cdata.pop('cgpa_or_percentage')
            experience_years = cdata.pop('experience_years')
            current_location = cdata.pop('current_location')
            github_url = cdata.pop('github_url')
            linkedin_url = cdata.pop('linkedin_url')

            cand_user, created = User.objects.get_or_create(
                username=cdata['username'],
                defaults={
                    'email': cdata['email'],
                    'first_name': cdata['first_name'],
                    'last_name': cdata['last_name'],
                    'phone': cdata['phone'],
                    'role': 'CANDIDATE',
                }
            )
            if created:
                cand_user.set_password('pass123')
                cand_user.save()

            # Generate sample PDF resume
            pdf_bytes = create_minimal_pdf(
                title=f"Curriculum Vitae - {cand_user.get_full_name()}",
                author=cand_user.get_full_name(),
                content_text=f"Skills: {skills}. Education: {education_degree} from {education_institution}."
            )
            pdf_file = ContentFile(pdf_bytes, name=f"{cand_user.username}_resume.pdf")

            profile, _ = CandidateProfile.objects.get_or_create(
                user=cand_user,
                defaults={
                    'headline': headline,
                    'skills': skills,
                    'education_degree': education_degree,
                    'education_institution': education_institution,
                    'graduation_year': graduation_year,
                    'cgpa_or_percentage': cgpa_or_percentage,
                    'experience_years': experience_years,
                    'current_location': current_location,
                    'github_url': github_url,
                    'linkedin_url': linkedin_url,
                    'resume': pdf_file,
                }
            )
            candidates.append(cand_user)
        self.stdout.write(self.style.SUCCESS(f"[+] Created {len(candidates)} candidate profiles with PDF resumes (pass: pass123)"))

        # 5. Job Listings
        google_emp = employers[0]
        msft_emp = employers[1]
        aws_emp = employers[2]
        infosys_emp = employers[3]
        razorpay_emp = employers[4]

        today = timezone.now().date()

        jobs_data = [
            {
                'employer': google_emp,
                'company': google_emp.employer_profile.company,
                'title': 'Senior Full-Stack Python Engineer',
                'description': 'We are looking for a Senior Full-Stack Python Engineer to build resilient distributed services and AI tooling for Google Cloud. You will architect high-throughput RESTful microservices, optimize database queries, and work alongside world-class engineers.',
                'required_skills': 'Python, Django, PostgreSQL, Docker, Kubernetes, REST APIs, Microservices',
                'location': 'Bengaluru, Karnataka',
                'is_remote': True,
                'employment_type': 'FULL_TIME',
                'experience_level': 'MID',
                'min_salary': 1800000,
                'max_salary': 3200000,
                'vacancies': 3,
                'deadline': today + timedelta(days=30),
                'status': 'ACTIVE',
                'is_featured': True,
            },
            {
                'employer': msft_emp,
                'company': msft_emp.employer_profile.company,
                'title': 'AI/ML Research Scientist - Copilot Platforms',
                'description': 'Join Microsoft IDC to innovate at the frontier of Generative AI and Foundation Models. Responsibilities include fine-tuning large language models, optimizing inference latency, and integrating intelligent agents into enterprise suites.',
                'required_skills': 'Python, PyTorch, Transformers, Deep Learning, NLP, CUDA, LLMs',
                'location': 'Hyderabad, Telangana',
                'is_remote': False,
                'employment_type': 'FULL_TIME',
                'experience_level': 'SENIOR',
                'min_salary': 2500000,
                'max_salary': 4500000,
                'vacancies': 2,
                'deadline': today + timedelta(days=45),
                'status': 'ACTIVE',
                'is_featured': True,
            },
            {
                'employer': aws_emp,
                'company': aws_emp.employer_profile.company,
                'title': 'Cloud DevOps Specialist & Infrastructure Architect',
                'description': 'Help thousands of enterprise customers migrate to AWS infrastructure. You will write Infrastructure-as-Code scripts, design zero-downtime deployment pipelines, and maintain multi-region resilience.',
                'required_skills': 'AWS, Terraform, Kubernetes, Linux, Docker, CI/CD, Python, Prometheus',
                'location': 'Bengaluru, Karnataka',
                'is_remote': True,
                'employment_type': 'FULL_TIME',
                'experience_level': 'MID',
                'min_salary': 1600000,
                'max_salary': 2800000,
                'vacancies': 4,
                'deadline': today + timedelta(days=25),
                'status': 'ACTIVE',
                'is_featured': True,
            },
            {
                'employer': razorpay_emp,
                'company': razorpay_emp.employer_profile.company,
                'title': 'Frontend React & UI Engineer',
                'description': 'Design and implement seamless checkout interfaces for millions of consumers and merchants. You will build highly responsive, accessible, and ultra-fast web components using React, TypeScript, and modern state management.',
                'required_skills': 'React, TypeScript, Next.js, Redux, Tailwind CSS, Webpack, Jest',
                'location': 'Bengaluru, Karnataka',
                'is_remote': True,
                'employment_type': 'FULL_TIME',
                'experience_level': 'ENTRY',
                'min_salary': 1000000,
                'max_salary': 1800000,
                'vacancies': 2,
                'deadline': today + timedelta(days=20),
                'status': 'ACTIVE',
                'is_featured': True,
            },
            {
                'employer': infosys_emp,
                'company': infosys_emp.employer_profile.company,
                'title': 'Software Engineer Trainee (Campus Placement 2026)',
                'description': 'Exciting career opportunity for final year B.Tech/BE Computer Science students. Extensive training in enterprise full-stack web development, database management, and cloud basics with immediate project deployment.',
                'required_skills': 'Java, Python, C++, Data Structures, SQL, OOPs, HTML, CSS',
                'location': 'Mysuru / Pune, India',
                'is_remote': False,
                'employment_type': 'FULL_TIME',
                'experience_level': 'ENTRY',
                'min_salary': 500000,
                'max_salary': 850000,
                'vacancies': 25,
                'deadline': today + timedelta(days=60),
                'status': 'ACTIVE',
                'is_featured': False,
            },
            {
                'employer': google_emp,
                'company': google_emp.employer_profile.company,
                'title': 'Summer Software Engineering Intern (2026)',
                'description': 'Experience the excitement of building Google products during an intensive 10-week summer internship. Work directly on production codebases under the mentorship of Google Staff Engineers.',
                'required_skills': 'C++, Python, Algorithms, Problem Solving, Git',
                'location': 'Bengaluru, Karnataka',
                'is_remote': False,
                'employment_type': 'INTERNSHIP',
                'experience_level': 'ENTRY',
                'min_salary': 75000,
                'max_salary': 120000,
                'vacancies': 5,
                'deadline': today + timedelta(days=15),
                'status': 'ACTIVE',
                'is_featured': True,
            },
            {
                'employer': razorpay_emp,
                'company': razorpay_emp.employer_profile.company,
                'title': 'Backend Python / Django Developer',
                'description': 'Join the Core Banking API team to handle high-frequency payment transactions. You will optimize database locks, implement secure payment webhooks, and ensure compliance with regulatory standards.',
                'required_skills': 'Python, Django, PostgreSQL, Redis, Celery, REST APIs',
                'location': 'Bengaluru, Karnataka',
                'is_remote': True,
                'employment_type': 'FULL_TIME',
                'experience_level': 'ENTRY',
                'min_salary': 900000,
                'max_salary': 1600000,
                'vacancies': 2,
                'deadline': today + timedelta(days=35),
                'status': 'ACTIVE',
                'is_featured': False,
            },
            {
                'employer': msft_emp,
                'company': msft_emp.employer_profile.company,
                'title': 'Cybersecurity & Cloud Compliance Analyst',
                'description': 'Monitor Azure enterprise endpoints, perform threat modeling, audit automated CI/CD security gates, and respond to platform vulnerabilities.',
                'required_skills': 'Cybersecurity, Network Security, Linux, Azure, SIEM, Python',
                'location': 'Noida / Bengaluru, India',
                'is_remote': True,
                'employment_type': 'FULL_TIME',
                'experience_level': 'MID',
                'min_salary': 1400000,
                'max_salary': 2400000,
                'vacancies': 1,
                'deadline': today + timedelta(days=40),
                'status': 'ACTIVE',
                'is_featured': False,
            },
            {
                'employer': aws_emp,
                'company': aws_emp.employer_profile.company,
                'title': 'Technical Writer & Developer Documentation Intern',
                'description': 'Craft crystal-clear API references, interactive tutorial guides, and code samples for developer documentation across AWS services.',
                'required_skills': 'Technical Writing, Markdown, Python, Git, Documentation',
                'location': 'Remote, India',
                'is_remote': True,
                'employment_type': 'INTERNSHIP',
                'experience_level': 'ENTRY',
                'min_salary': 40000,
                'max_salary': 60000,
                'vacancies': 2,
                'deadline': today + timedelta(days=18),
                'status': 'ACTIVE',
                'is_featured': False,
            },
            {
                'employer': infosys_emp,
                'company': infosys_emp.employer_profile.company,
                'title': 'Contract Part-Time UI Designer (Design System)',
                'description': 'Help our team standardize visual component libraries in Figma and align UI tokens for client enterprise portals.',
                'required_skills': 'Figma, UI/UX, Design Systems, Wireframing, Prototyping',
                'location': 'Hybrid, Bengaluru',
                'is_remote': True,
                'employment_type': 'PART_TIME',
                'experience_level': 'MID',
                'min_salary': 350000,
                'max_salary': 600000,
                'vacancies': 1,
                'deadline': today - timedelta(days=5),
                'status': 'CLOSED',
                'is_featured': False,
            }
        ]

        created_jobs = []
        for jdata in jobs_data:
            job, _ = Job.objects.get_or_create(
                employer=jdata['employer'],
                company=jdata['company'],
                title=jdata['title'],
                defaults=jdata
            )
            created_jobs.append(job)
        self.stdout.write(self.style.SUCCESS(f"[+] Created {len(created_jobs)} rich job vacancies across multiple domains"))

        # 6. Applications with diverse statuses
        c_rahul = candidates[0]
        c_priya = candidates[1]
        c_aman = candidates[2]
        c_sneha = candidates[3]
        c_vikram = candidates[4]

        applications_data = [
            {
                'job': created_jobs[0],  # Google Senior Python
                'candidate': c_rahul,
                'status': 'SHORTLISTED',
                'cover_letter': 'Dear Amitabh, I have 1.5+ years building full-stack Python and Django applications with high concurrency. I am excited to contribute to Google Cloud.',
                'employer_notes': 'Strong GitHub repository with Django REST Framework. Scheduled technical round 1 for Thursday.',
            },
            {
                'job': created_jobs[6],  # Razorpay Backend Python
                'candidate': c_rahul,
                'status': 'SELECTED',
                'cover_letter': 'Hello Razorpay Team, having engineered payment integrations and REST microservices in Django, I would love to work on your Core Banking platform.',
                'employer_notes': 'Cleared all technical rounds with flying colors. Offer letter dispatched at 14 LPA.',
            },
            {
                'job': created_jobs[1],  # Microsoft AI/ML
                'candidate': c_priya,
                'status': 'SHORTLISTED',
                'cover_letter': 'Dear Microsoft IDC Team, I have worked extensively with PyTorch, Transformer fine-tuning and LLM benchmarking. I have published research at college.',
                'employer_notes': 'Impressive research portfolio and deep learning projects. Moving to HR interview.',
            },
            {
                'job': created_jobs[2],  # AWS DevOps
                'candidate': c_aman,
                'status': 'SELECTED',
                'cover_letter': 'Dear Hiring Lead, I am a certified AWS Solutions Architect with hands-on experience provisioning multi-cluster Kubernetes on EKS with Terraform.',
                'employer_notes': 'Excellent depth in cloud infrastructure and zero-downtime CI/CD. Offer extended.',
            },
            {
                'job': created_jobs[3],  # Razorpay Frontend
                'candidate': c_sneha,
                'status': 'PENDING',
                'cover_letter': 'Hi there! I build ultra-performant React web apps with Next.js and Tailwind CSS. Would love to elevate the Razorpay checkout experience.',
                'employer_notes': '',
            },
            {
                'job': created_jobs[4],  # Infosys Campus
                'candidate': c_vikram,
                'status': 'PENDING',
                'cover_letter': 'Respected Campus Recruiter, I am a final-year B.Tech CSE student passionate about software engineering, Java, and solving real-world challenges.',
                'employer_notes': '',
            },
            {
                'job': created_jobs[5],  # Google Summer Intern
                'candidate': c_vikram,
                'status': 'REJECTED',
                'cover_letter': 'I want to learn and contribute to Google open-source projects this summer.',
                'employer_notes': 'Good candidate, but looking for stronger algorithmic contest track record this term. Encouraged to reapply.',
            }
        ]

        for app_data in applications_data:
            app, _ = Application.objects.get_or_create(
                job=app_data['job'],
                candidate=app_data['candidate'],
                defaults=app_data
            )
        self.stdout.write(self.style.SUCCESS(f"[+] Created {len(applications_data)} realistic job applications with status tracking"))

        # 7. Notifications
        Notification.objects.get_or_create(
            recipient=c_rahul,
            title="Interview Shortlisted: Google Cloud India",
            defaults={
                'message': "Congratulations Rahul! Amitabh Kapur has shortlisted your application for 'Senior Full-Stack Python Engineer'.",
                'notification_type': 'STATUS_CHANGE',
                'target_url': '/dashboard/candidate/',
            }
        )

        Notification.objects.get_or_create(
            recipient=c_rahul,
            title="Offer Extended: Razorpay Payments",
            defaults={
                'message': "Amazing news! You have been Selected for 'Backend Python / Django Developer' at Razorpay Payments.",
                'notification_type': 'STATUS_CHANGE',
                'target_url': '/dashboard/candidate/',
            }
        )

        Notification.objects.get_or_create(
            recipient=google_emp,
            title="New Applicant for Senior Full-Stack Python Engineer",
            defaults={
                'message': "Rahul Sharma applied for 'Senior Full-Stack Python Engineer'.",
                'notification_type': 'NEW_APPLICATION',
                'target_url': '/dashboard/employer/applicants/',
            }
        )

        self.stdout.write(self.style.SUCCESS("[+] Seeded realistic in-app notifications"))
        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] CareerConnect database successfully seeded with full viva-ready data!"))
