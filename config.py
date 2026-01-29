import os
from dotenv import load_dotenv
# Configuration settings

load_dotenv()
OPENROUTER_API_KEY = os.getenv("API_KEY") 
OPENROUTER_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "llama-3.3-70b-versatile"

# Interview settings
MAX_QUESTIONS = 7
MIN_QUESTIONS = 3
QUESTION_DIFFICULTY_LEVELS = ["basic", "intermediate", "advanced", "scenario-based"]

# Skill categories
SKILL_CATEGORIES = {
    # Software Development
    "backend": [
        "Python", "Java", "Node.js", "C#", "Go",
        "Databases", "REST APIs", "Microservices"
    ],

    "frontend": [
        "Frontend",
        "JavaScript", "React", "Angular", "Vue",
        "HTML", "CSS", "TypeScript"
    ],

    "fullstack": [
        "Fullstack",
        "Frontend + Backend",
        "End-to-End Application Development",
        "System Design",
        "DevOps Basics"
    ],

    # Infrastructure & Cloud
    "devops": [
        "DevOps",
        "AWS", "Azure", "GCP",
        "Docker", "Kubernetes",
        "CI/CD Pipelines",
        "Terraform",
        "Linux"
    ],

    "networking": [
        "Networking", "Network Engineering",
        "Computer Networks",
        "TCP/IP",
        "Routing & Switching",
        "LAN / WAN",
        "DNS",
        "DHCP",
        "Firewalls",
        "VPN",
        "Network Security"
    ],

    # Data & AI
    "data": [
        "Data", "Data Science", "Data Engineering",
        "Python", "SQL",
        "Data Analysis",
        "Machine Learning",
        "Deep Learning",
        "PyTorch",
        "TensorFlow"
    ],

    # Mobile Development
    "mobile": [
        "Mobile", "App Development",
        "Android",
        "iOS",
        "React Native",
        "Flutter"
    ],

    # AEC / BIM / Core Engineering
    "aec_bim": [
        "AEC", "BIM", "AEC_BIM",
        "Tekla",
        "AutoCAD",
        "Structural Steel Detailing",
        "BIM Modeling",
        "Shop Drawings",
        "Erection Drawings",
        "Fabrication Drawings",
        "GA Drawings",
        "Connection Detailing",
        "IS / AISC / BS Codes"
    ],

    # Human Resources
    "hr": [
        "HR", "Human Resources",
        "Recruitment & Staffing",
        "Talent Acquisition",
        "HR Operations",
        "Payroll Management",
        "Employee Relations",
        "Performance Management",
        "HR Policies & Compliance",
        "Onboarding & Offboarding"
    ],

    # Additional Useful Domains
    "qa_testing": [
        "QA", "Testing", "Quality Assurance",
        "Manual Testing",
        "Automation Testing",
        "Selenium",
        "Cypress",
        "API Testing",
        "Performance Testing"
    ],

    "ui_ux": [
        "UI", "UX", "UI/UX", "Product Design",
        "User Research",
        "Wireframing",
        "Prototyping",
        "Figma",
        "Adobe XD",
        "Usability Testing"
    ],

    "cybersecurity": [
        "Cybersecurity", "Security", "InfoSec",
        "Information Security",
        "Threat Modeling",
        "Vulnerability Assessment",
        "Penetration Testing",
        "IAM",
        "SIEM",
        "SOC Operations"
    ]
}


# Termination keywords
TERMINATION_KEYWORDS = ["quit", "exit", "stop", "end", "terminate", "abort"]
ABUSIVE_KEYWORDS = ["tab switching", "stupid", "idiot", "dumb", "worthless", "hate", "useless"]