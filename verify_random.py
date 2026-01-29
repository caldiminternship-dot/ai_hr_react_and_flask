from question_generator import QuestionGenerator

def verify():
    print("Initializing Generator...")
    gen = QuestionGenerator()
    
    print("Generating questions for 'frontend'...")
    # This will trigger the code path with random.choice
    questions = gen.generate_initial_skill_questions("frontend")
    
    if questions and len(questions) > 0:
        print("Success! Generated questions:")
        for q in questions:
            print("- " + q)
    else:
        print("Failed to generate questions.")

if __name__ == "__main__":
    verify()
