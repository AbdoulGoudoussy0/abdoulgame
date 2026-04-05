import requests
import sys
import json
import time
from datetime import datetime

class AbdoulGameV2Tester:
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

    def test_ai_hint_endpoint(self):
        """Test AI hint generation endpoint"""
        test_cases = [
            {"word": "VIRTUD", "language": "ES", "found_letters": []},
            {"word": "WISDOM", "language": "EN", "found_letters": ["W", "I"]},
            {"word": "SAGESSE", "language": "FR", "found_letters": ["S", "A"]}
        ]
        
        all_passed = True
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/ai/hint",
                    json=case,
                    headers={'Content-Type': 'application/json'},
                    timeout=30  # AI calls can take longer
                )
                success = response.status_code == 200
                details = f"Word: {case['word']}, Lang: {case['language']}, Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    # Validate response structure
                    required_fields = ['hint', 'encouragement']
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        success = False
                        details += f", Missing fields: {missing_fields}"
                    else:
                        hint = data['hint']
                        encouragement = data['encouragement']
                        details += f", Hint length: {len(hint)}, Encouragement length: {len(encouragement)}"
                        
                        # Validate content is not empty
                        if not hint or not encouragement:
                            success = False
                            details += ", Empty hint or encouragement"
                        elif case['word'].lower() in hint.lower():
                            success = False
                            details += ", Hint reveals the word directly"
                
                self.log_test(f"AI Hint {case['language']} - {case['word']}", success, details)
                if not success:
                    all_passed = False
                    
                # Add delay between AI calls to avoid rate limiting
                time.sleep(1)
                    
            except Exception as e:
                self.log_test(f"AI Hint {case['language']} - {case['word']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_ai_wisdom_endpoint(self):
        """Test AI wisdom generation endpoint"""
        test_cases = [
            {"word": "AMOR", "language": "ES"},
            {"word": "PEACE", "language": "EN"},
            {"word": "COURAGE", "language": "FR"}
        ]
        
        all_passed = True
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/ai/wisdom",
                    params=case,
                    timeout=30
                )
                success = response.status_code == 200
                details = f"Word: {case['word']}, Lang: {case['language']}, Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    if 'wisdom' not in data:
                        success = False
                        details += ", Missing wisdom field"
                    else:
                        wisdom = data['wisdom']
                        details += f", Wisdom length: {len(wisdom)}"
                        
                        # Validate content is not empty
                        if not wisdom:
                            success = False
                            details += ", Empty wisdom"
                
                self.log_test(f"AI Wisdom {case['language']} - {case['word']}", success, details)
                if not success:
                    all_passed = False
                    
                # Add delay between AI calls
                time.sleep(1)
                    
            except Exception as e:
                self.log_test(f"AI Wisdom {case['language']} - {case['word']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_ai_encouragement_endpoint(self):
        """Test AI encouragement endpoint"""
        test_cases = [
            {"language": "ES", "words_found": 2, "total_words": 5},
            {"language": "EN", "words_found": 4, "total_words": 6},
            {"language": "FR", "words_found": 1, "total_words": 3}
        ]
        
        all_passed = True
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/ai/encouragement",
                    params=case,
                    timeout=30
                )
                success = response.status_code == 200
                details = f"Lang: {case['language']}, Progress: {case['words_found']}/{case['total_words']}, Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    if 'message' not in data:
                        success = False
                        details += ", Missing message field"
                    else:
                        message = data['message']
                        details += f", Message length: {len(message)}"
                        
                        # Validate content is not empty
                        if not message:
                            success = False
                            details += ", Empty message"
                
                self.log_test(f"AI Encouragement {case['language']}", success, details)
                if not success:
                    all_passed = False
                    
                # Add delay between AI calls
                time.sleep(1)
                    
            except Exception as e:
                self.log_test(f"AI Encouragement {case['language']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_share_generation_endpoint(self):
        """Test share text generation endpoint"""
        test_cases = [
            {"score": 1500, "level": 3, "words_found": 5, "language": "ES"},
            {"score": 2200, "level": 7, "words_found": 8, "language": "EN"},
            {"score": 800, "level": 2, "words_found": 3, "language": "FR"}
        ]
        
        all_passed = True
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/share/generate",
                    json=case,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                success = response.status_code == 200
                details = f"Score: {case['score']}, Level: {case['level']}, Lang: {case['language']}, Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    if 'text' not in data:
                        success = False
                        details += ", Missing text field"
                    else:
                        text = data['text']
                        details += f", Text length: {len(text)}"
                        
                        # Validate content contains expected elements
                        if not text:
                            success = False
                            details += ", Empty text"
                        elif str(case['score']) not in text:
                            success = False
                            details += ", Score not in share text"
                        elif str(case['level']) not in text:
                            success = False
                            details += ", Level not in share text"
                        elif str(case['words_found']) not in text:
                            success = False
                            details += ", Words found not in share text"
                
                self.log_test(f"Share Generation {case['language']}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Share Generation {case['language']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_game_time_limits(self):
        """Test that game generation returns correct time limits based on level"""
        expected_times = {
            1: 150, 2: 140, 3: 130, 4: 125, 5: 120,
            6: 115, 7: 110, 8: 105, 9: 100, 10: 95
        }
        
        all_passed = True
        for level, expected_time in expected_times.items():
            try:
                response = requests.post(
                    f"{self.api_url}/game/generate",
                    json={"level": level, "language": "ES"},
                    headers={'Content-Type': 'application/json'},
                    timeout=15
                )
                success = response.status_code == 200
                details = f"Level: {level}, Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    if 'time_limit' not in data:
                        success = False
                        details += ", Missing time_limit field"
                    else:
                        actual_time = data['time_limit']
                        details += f", Expected: {expected_time}s, Actual: {actual_time}s"
                        
                        if actual_time != expected_time:
                            success = False
                            details += ", Time limit mismatch"
                
                self.log_test(f"Time Limit Level {level}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Time Limit Level {level}", False, str(e))
                all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all V2 feature tests"""
        print(f"🚀 Starting AbdoulGame V2 Feature Tests")
        print(f"🎯 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Run tests in order
        print("\n🤖 Testing AI Integration...")
        self.test_ai_hint_endpoint()
        self.test_ai_wisdom_endpoint()
        self.test_ai_encouragement_endpoint()
        
        print("\n📱 Testing Share Functionality...")
        self.test_share_generation_endpoint()
        
        print("\n⏱️ Testing Game Time Limits...")
        self.test_game_time_limits()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All V2 features working perfectly!")
            return True
        else:
            print("⚠️  Some V2 features failed. Check details above.")
            failed_tests = [r for r in self.test_results if not r['success']]
            print("\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return False

def main():
    tester = AbdoulGameV2Tester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())