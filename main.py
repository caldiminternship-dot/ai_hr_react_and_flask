import sys
from interview_manager import InterviewManager
from utils import format_response, Fore, Style

def main():
    """Main function to run the AI-powered virtual HR interviewer"""
    try:
        # Initialize interview manager
        manager = InterviewManager()
        
        # Start interview
        manager.start_interview()
        
        # Ask initial question
        initial_question = manager.ask_initial_question()
        manager.interview_data["questions_asked"].append(initial_question)
        
        # Get initial response
        max_retries = 2
        for attempt in range(max_retries + 1):
            response = input(format_response("\nCandidate: ", Fore.GREEN))
            
            result = manager.process_response(response)
            
            if result.get("terminate"):
                manager.end_interview(early_termination=True, reason=result["reason"])
                return
            
            if not result.get("needs_more_info", False):
                break
            
            if attempt < max_retries:
                print(format_response("\nAI Interviewer: Please share your background to begin:", Fore.BLUE))
            else:
                print(format_response("\nUnable to proceed without background information.", Fore.RED))
                manager.end_interview(early_termination=True, reason="poor_response")
                return
        
        # Continue with AI-generated questions
        question_count = 0
        while manager.should_continue():
            # Get next AI-generated question
            question = manager.get_next_question()
            
            if not question:
                continue
            
            question_count += 1
            
            # Display question only once here
            print(format_response(f"\n[Question {question_count}/{manager.max_questions}]", Fore.CYAN))
            print(format_response(f"Interviewer: {question}", Fore.BLUE + Style.BRIGHT))
            
            # Get response
            response = input(format_response("\nCandidate: ", Fore.GREEN))
            
            # Process response
            result = manager.process_response(response)
            if result.get("terminate"):
                manager.end_interview(early_termination=True, reason=result["reason"])
                return
            
            if result.get("skip", False):
                question_count -= 1
                continue
        
        # End interview
        manager.end_interview()
        
    except KeyboardInterrupt:
        print(format_response("\n\nInterview interrupted by user.", Fore.YELLOW))
        sys.exit(0)
    except Exception as e:
        print(format_response(f"\nAn error occurred: {str(e)}", Fore.RED))
        sys.exit(1)

if __name__ == "__main__":
    main()