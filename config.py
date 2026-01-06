import os

# Configuration settings
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Interview settings
MAX_QUESTIONS = 7
MIN_QUESTIONS = 3
QUESTION_DIFFICULTY_LEVELS = ["basic", "intermediate", "advanced", "scenario-based"]

# Skill categories
SKILL_CATEGORIES = {
    "backend": ["Python", "Java", "Node.js", "C#", "Go", "Database", "API", "Microservices"],
    "frontend": ["JavaScript", "React", "Angular", "Vue", "HTML/CSS", "TypeScript"],
    "fullstack": ["Frontend+Backend", "DevOps basics", "End-to-end development"],
    "devops": ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform", "Linux"],
    "data": ["Python", "SQL", "Machine Learning", "Data Analysis", "PyTorch", "TensorFlow"],
    "mobile": ["iOS", "Android", "React Native", "Flutter"]
}

# Termination keywords
TERMINATION_KEYWORDS = ["quit", "exit", "stop", "end", "terminate", "abort"]
ABUSIVE_KEYWORDS = ["stupid", "idiot", "dumb", "worthless", "hate", "useless", "terrible"]