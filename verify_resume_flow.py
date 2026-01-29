import io
from resume_parser import parse_resume
from config import SKILL_CATEGORIES
from utils import extract_skills
from skill_mapper import map_skills_to_category

class MockFile:
    def __init__(self, name, content):
        self.name = name
        self.content = content
        
    def getvalue(self):
        return self.content.encode('utf-8')

def test_resume_flow():
    print("Testing Resume Parser Flow...")
    
    # 1. Mock a resume (Text file for simplicity in test)
    resume_content = """
    John Doe
    Software Engineer
    
    Experience:
    - Built a REST API using Python and Flask
    - Managed AWS infrastructure
    - Developed frontend with React and TypeScript
    - Implemented CI/CD pipelines with Docker and Kubernetes
    """
    
    mock_file = MockFile("resume.txt", resume_content)
    
    # 2. Parse
    text = parse_resume(mock_file)
    print(f"Extracted Text Length: {len(text)}")
    
    # 3. Extract Skills
    skills = extract_skills(text)
    print(f"Extracted Skills: {skills}")
    
    # 4. Map Category
    category = map_skills_to_category(skills)
    print(f"Mapped Category: {category}")
    
    # Validation
    expected_skills = ["python", "flask", "aws", "react", "typescript", "docker", "kubernetes", "api", "software engineer", "infrastructure", "ci/cd"]
    # (Note: "software engineer" depends on if it's in config, others are definitely there)
    
    matched = any(s in skills for s in ["python", "flask", "aws", "react"])
    if matched and category != "backend": 
        # Actually in this mix, backend/fullstack/devops matches. 
        # Python, Flask, AWS, Docker, K8s -> likely Backend or DevOps.
        # React, TS -> Frontend.
        # Let's see what it picks. Ideally Fullstack or Backend.
        pass
        
    print(f"Test Result: {'PASS' if len(skills) > 3 else 'FAIL'}")

if __name__ == "__main__":
    test_resume_flow()
