import os
from dotenv import load_dotenv
# Configuration settings

load_dotenv()
OPENROUTER_API_KEY = os.getenv("API_KEY") 
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

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
        "JavaScript", "React", "Angular", "Vue",
        "HTML", "CSS", "TypeScript"
    ],

    "fullstack": [
        "Frontend + Backend",
        "End-to-End Application Development",
        "System Design",
        "DevOps Basics"
    ],

    # Infrastructure & Cloud
    "devops": [
        "AWS", "Azure", "GCP",
        "Docker", "Kubernetes",
        "CI/CD Pipelines",
        "Terraform",
        "Linux"
    ],

    "networking": [
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
        "Python", "SQL",
        "Data Analysis",
        "Machine Learning",
        "Deep Learning",
        "PyTorch",
        "TensorFlow"
    ],

    # Mobile Development
    "mobile": [
        "Android",
        "iOS",
        "React Native",
        "Flutter"
    ],

    # AEC / BIM / Core Engineering
    "aec_bim": [
        "Tekla Structures",
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
        "Manual Testing",
        "Automation Testing",
        "Selenium",
        "Cypress",
        "API Testing",
        "Performance Testing"
    ],

    "ui_ux": [
        "User Research",
        "Wireframing",
        "Prototyping",
        "Figma",
        "Adobe XD",
        "Usability Testing"
    ],

    "project_management": [
        "Agile",
        "Scrum",
        "Kanban",
        "JIRA",
        "Risk Management",
        "Stakeholder Communication"
    ],

    "cybersecurity": [
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
ABUSIVE_KEYWORDS = ["tab switching", "stupid", "idiot", "dumb", "worthless", "hate", "useless", "terrible"]