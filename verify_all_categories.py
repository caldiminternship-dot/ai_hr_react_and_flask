from skill_mapper import map_skills_to_category

def verify_all():
    test_cases = [
        ("Networking", "networking"),
        ("Data Science", "data"),
        ("Mobile", "mobile"),
        ("DevOps", "devops"),
        ("HR", "hr"),
        ("QA", "qa_testing"),
        ("UI/UX", "ui_ux"),
        ("Cybersecurity", "cybersecurity"),
        ("Fullstack", "fullstack"),
        ("Software Engineering", "backend") # Fallback check
    ]

    print("Verifying Skill Mapping...")
    for skill_input, expected in test_cases:
        result = map_skills_to_category([skill_input])
        status = "PASS" if result == expected else f"FAIL (Got {result})"
        print(f"Input: {[skill_input]} -> {expected} | {status}")

if __name__ == "__main__":
    verify_all()
