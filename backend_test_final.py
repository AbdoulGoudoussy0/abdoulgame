import requests
import sys
import json
import time
from datetime import datetime

class AbdoulGameFinalTester:
    def __init__(self, base_url="https://knowledge-seeker-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_security_headers(self):
        """Test security headers on API responses"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            # Check for security headers
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options', 
                'X-XSS-Protection',
                'Referrer-Policy',
                'Permissions-Policy'
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if missing_headers:
                success = False
                details += f", Missing security headers: {missing_headers}"
            else:
                details += f", All security headers present: {security_headers}"
            
            self.log_test("Security Headers", success, details)
            return success
        except Exception as e:
            self.log_test("Security Headers", False, str(e))
            return False

    def test_input_sanitization(self):
        """Test input sanitization for player names"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE scores; --",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "' OR '1'='1"
        ]
        
        all_passed = True
        for malicious_input in malicious_inputs:
            try:
                test_score = {
                    "player_name": malicious_input,
                    "score": 1000,
                    "level": 1,
                    "language": "ES",
                    "words_found": 3,
                    "time_remaining": 60
                }
                
                response = requests.post(
                    f"{self.api_url}/scores",
                    json=test_score,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                success = response.status_code == 200
                details = f"Input: {malicious_input[:20]}..., Status: {response.status_code}"
                
                if success:
                    saved_score = response.json()
                    sanitized_name = saved_score.get('player_name', '')
                    
                    # Check if dangerous characters were removed
                    dangerous_chars = ['<', '>', '"', "'", ';', '\\']
                    if any(char in sanitized_name for char in dangerous_chars):
                        success = False
                        details += f", Dangerous characters not sanitized: {sanitized_name}"
                    else:
                        details += f", Properly sanitized to: {sanitized_name}"
                
                self.log_test(f"Input Sanitization - {malicious_input[:10]}...", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Input Sanitization - {malicious_input[:10]}...", False, str(e))
                all_passed = False
        
        return all_passed

    def test_score_validation(self):
        """Test score bounds checking and validation"""
        test_cases = [
            {"score": -100, "expected_score": 0, "description": "Negative score"},
            {"score": 999999, "expected_score": 100000, "description": "Score too high"},
            {"score": 1500, "expected_score": 1500, "description": "Valid score"},
            {"level": -1, "expected_level": 1, "description": "Negative level"},
            {"level": 15, "expected_level": 10, "description": "Level too high"},
            {"words_found": -5, "expected_words": 0, "description": "Negative words"},
            {"words_found": 50, "expected_words": 20, "description": "Too many words"},
            {"time_remaining": -10, "expected_time": 0, "description": "Negative time"},
            {"time_remaining": 500, "expected_time": 300, "description": "Time too high"}
        ]
        
        all_passed = True
        for i, case in enumerate(test_cases):
            try:
                test_score = {
                    "player_name": f"TestPlayer_{i}",
                    "score": case.get("score", 1000),
                    "level": case.get("level", 1),
                    "language": "ES",
                    "words_found": case.get("words_found", 3),
                    "time_remaining": case.get("time_remaining", 60)
                }
                
                response = requests.post(
                    f"{self.api_url}/scores",
                    json=test_score,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                success = response.status_code == 200
                details = f"{case['description']}, Status: {response.status_code}"
                
                if success:
                    saved_score = response.json()
                    
                    # Check if values were properly validated
                    if "score" in case:
                        actual_score = saved_score.get('score', 0)
                        if actual_score != case['expected_score']:
                            success = False
                            details += f", Score validation failed: expected {case['expected_score']}, got {actual_score}"
                    
                    if "level" in case:
                        actual_level = saved_score.get('level', 1)
                        if actual_level != case['expected_level']:
                            success = False
                            details += f", Level validation failed: expected {case['expected_level']}, got {actual_level}"
                    
                    if "words_found" in case:
                        actual_words = saved_score.get('words_found', 0)
                        if actual_words != case['expected_words']:
                            success = False
                            details += f", Words validation failed: expected {case['expected_words']}, got {actual_words}"
                    
                    if "time_remaining" in case:
                        actual_time = saved_score.get('time_remaining', 0)
                        if actual_time != case['expected_time']:
                            success = False
                            details += f", Time validation failed: expected {case['expected_time']}, got {actual_time}"
                    
                    if success:
                        details += ", Validation working correctly"
                
                self.log_test(f"Score Validation - {case['description']}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Score Validation - {case['description']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_predefined_hints(self):
        """Test that hints work without AI (predefined content)"""
        test_cases = [
            {"word": "VIRTUD", "language": "ES"},
            {"word": "WISDOM", "language": "EN"},
            {"word": "SAGESSE", "language": "FR"}
        ]
        
        all_passed = True
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/ai/hint",
                    json=case,
                    headers={'Content-Type': 'application/json'},
                    timeout=5  # Should be fast since no AI
                )
                success = response.status_code == 200
                details = f"Word: {case['word']}, Lang: {case['language']}, Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    hint = data.get('hint', '')
                    encouragement = data.get('encouragement', '')
                    
                    # Check that responses are predefined (not AI-generated)
                    if not hint or not encouragement:
                        success = False
                        details += ", Empty hint or encouragement"
                    elif len(hint) < 10 or len(encouragement) < 5:
                        success = False
                        details += ", Hint or encouragement too short"
                    else:
                        details += f", Hint: {len(hint)} chars, Encouragement: {len(encouragement)} chars"
                
                self.log_test(f"Predefined Hints {case['language']}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Predefined Hints {case['language']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_predefined_wisdom(self):
        """Test that wisdom works without AI (database phrases)"""
        test_cases = [
            {"word": "VIRTUD", "language": "ES"},
            {"word": "VIRTUE", "language": "EN"},
            {"word": "VERTU", "language": "FR"}
        ]
        
        all_passed = True
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/ai/wisdom",
                    params={"word": case['word'], "language": case['language']},
                    timeout=5  # Should be fast since no AI
                )
                success = response.status_code == 200
                details = f"Word: {case['word']}, Lang: {case['language']}, Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    wisdom = data.get('wisdom', '')
                    
                    if not wisdom:
                        success = False
                        details += ", Empty wisdom"
                    elif len(wisdom) < 5:
                        success = False
                        details += ", Wisdom too short"
                    else:
                        details += f", Wisdom: {wisdom[:50]}..."
                
                self.log_test(f"Predefined Wisdom {case['language']}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Predefined Wisdom {case['language']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_crossing_words_support(self):
        """Test that words can share letters (crossing words)"""
        try:
            # Generate a game and check if words can potentially cross
            response = requests.post(
                f"{self.api_url}/game/generate",
                json={"level": 5, "language": "ES"},
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                words = data.get('words', [])
                matrix = data.get('matrix', [])
                
                if len(words) >= 2:
                    # Check if any cells are used by multiple words (crossing)
                    cell_usage = {}
                    for word_obj in words:
                        for coord in word_obj.get('coords', []):
                            cell_key = f"{coord['r']}-{coord['c']}"
                            if cell_key in cell_usage:
                                cell_usage[cell_key].append(word_obj['word'])
                            else:
                                cell_usage[cell_key] = [word_obj['word']]
                    
                    crossing_cells = {k: v for k, v in cell_usage.items() if len(v) > 1}
                    
                    if crossing_cells:
                        details += f", Found {len(crossing_cells)} crossing cells"
                        for cell, words_at_cell in list(crossing_cells.items())[:3]:  # Show first 3
                            details += f", Cell {cell}: {words_at_cell}"
                    else:
                        # This is not necessarily a failure, just means no crossing in this generation
                        details += ", No crossing words in this generation (acceptable)"
                else:
                    success = False
                    details += ", Not enough words generated"
            
            self.log_test("Crossing Words Support", success, details)
            return success
        except Exception as e:
            self.log_test("Crossing Words Support", False, str(e))
            return False

    def run_all_tests(self):
        """Run all final version backend tests"""
        print(f"🚀 Starting AbdoulGame Final Version Backend Tests")
        print(f"🎯 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Test security features
        print("\n🔒 Testing Security Features...")
        self.test_security_headers()
        self.test_input_sanitization()
        self.test_score_validation()
        
        # Test no-AI features
        print("\n🤖 Testing No-AI Features...")
        self.test_predefined_hints()
        self.test_predefined_wisdom()
        
        # Test game mechanics
        print("\n🎮 Testing Game Mechanics...")
        self.test_crossing_words_support()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All final version backend features working perfectly!")
            return True
        else:
            print("⚠️  Some backend features failed. Check details above.")
            failed_tests = [r for r in self.test_results if not r['success']]
            print("\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return False

def main():
    tester = AbdoulGameFinalTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())