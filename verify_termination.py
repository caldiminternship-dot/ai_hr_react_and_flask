from response_analyzer import ResponseAnalyzer
from config import TERMINATION_KEYWORDS, ABUSIVE_KEYWORDS

def verify_termination_logic():
    analyzer = ResponseAnalyzer()
    
    test_cases = [
        # (Input, Expected Result, Expected Reason)
        ("I want to quit", True, "candidate_request"),
        ("Please exit the interview", True, "candidate_request"),
        ("Stop this", True, "candidate_request"),
        ("This is stupid", True, "misconduct"),
        ("You are an idiot", True, "misconduct"),
        ("I hate this", True, "misconduct"),
        ("Session terminated due to tab switching", True, "misconduct"), # This is handled in app.py separately but good to check keyword overlap
        ("This is a valid answer about python", False, ""),
        ("I am explaining my project", False, ""),
    ]
    
    print("Verifying Termination Logic...")
    all_passed = True
    
    for input_text, expected_bool, expected_reason in test_cases:
        should_terminate, reason = analyzer.check_for_termination(input_text)
        
        # Note: Tab switching phrase in app.py is handled before calling analyzer, 
        # but "tab switching" IS in ABUSIVE_KEYWORDS, so analyzer should also catch it if passed.
        
        passed = (should_terminate == expected_bool)
        if passed and should_terminate:
             passed = (reason == expected_reason)
             
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
            print(f"[{status}] Input: '{input_text}'")
            print(f"       Expected: {expected_bool}, {expected_reason}")
            print(f"       Got:      {should_terminate}, {reason}")
        else:
            print(f"[{status}] Input: '{input_text}' -> {reason}")

    if all_passed:
        print("\nAll termination checks PASSED.")
    else:
        print("\nSome termination checks FAILED.")

if __name__ == "__main__":
    verify_termination_logic()
