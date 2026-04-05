import requests
import sys
import json
from datetime import datetime

class AbdoulGameAPITester:
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

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            self.log_test("API Root", success, details)
            return success
        except Exception as e:
            self.log_test("API Root", False, str(e))
            return False

    def test_knowledge_endpoint(self):
        """Test knowledge database endpoint"""
        try:
            response = requests.get(f"{self.api_url}/knowledge", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Words count: {len(data)}"
                # Verify structure
                if len(data) > 0:
                    first_word = data[0]
                    required_fields = ['id', 'ES', 'EN', 'FR', 'infoES', 'infoEN', 'infoFR']
                    missing_fields = [field for field in required_fields if field not in first_word]
                    if missing_fields:
                        success = False
                        details += f", Missing fields: {missing_fields}"
            self.log_test("Knowledge Database", success, details)
            return success, data if success else []
        except Exception as e:
            self.log_test("Knowledge Database", False, str(e))
            return False, []

    def test_game_generation(self):
        """Test game generation endpoint"""
        test_cases = [
            {"level": 1, "language": "ES"},
            {"level": 3, "language": "EN"},
            {"level": 5, "language": "FR"},
            {"level": 10, "language": "ES"},  # Max level
        ]
        
        all_passed = True
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/game/generate",
                    json=case,
                    headers={'Content-Type': 'application/json'},
                    timeout=15
                )
                success = response.status_code == 200
                details = f"Level {case['level']}, Lang {case['language']}, Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    # Validate response structure
                    required_fields = ['matrix', 'size', 'words']
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        success = False
                        details += f", Missing fields: {missing_fields}"
                    else:
                        # Validate matrix
                        matrix = data['matrix']
                        size = data['size']
                        words = data['words']
                        
                        if len(matrix) != size or any(len(row) != size for row in matrix):
                            success = False
                            details += ", Invalid matrix dimensions"
                        elif len(words) == 0:
                            success = False
                            details += ", No words generated"
                        else:
                            details += f", Size: {size}x{size}, Words: {len(words)}"
                            # Validate word structure
                            for word in words:
                                if not all(field in word for field in ['word', 'info', 'coords']):
                                    success = False
                                    details += ", Invalid word structure"
                                    break
                
                self.log_test(f"Game Generation {case['language']} L{case['level']}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Game Generation {case['language']} L{case['level']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_score_endpoints(self):
        """Test score-related endpoints"""
        # Test saving a score
        test_score = {
            "player_name": f"TestPlayer_{datetime.now().strftime('%H%M%S')}",
            "score": 1500,
            "level": 3,
            "language": "ES"
        }
        
        try:
            # Save score
            response = requests.post(
                f"{self.api_url}/scores",
                json=test_score,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            save_success = response.status_code == 200
            details = f"Save Status: {response.status_code}"
            
            if save_success:
                saved_score = response.json()
                details += f", ID: {saved_score.get('id', 'No ID')}"
                
                # Test getting top scores
                top_response = requests.get(f"{self.api_url}/scores/top?limit=5", timeout=10)
                top_success = top_response.status_code == 200
                if top_success:
                    top_scores = top_response.json()
                    details += f", Top scores count: {len(top_scores)}"
                else:
                    save_success = False
                    details += f", Top scores failed: {top_response.status_code}"
                
                # Test getting player scores
                player_response = requests.get(
                    f"{self.api_url}/scores/player/{test_score['player_name']}", 
                    timeout=10
                )
                player_success = player_response.status_code == 200
                if player_success:
                    player_scores = player_response.json()
                    details += f", Player scores count: {len(player_scores)}"
                    # Verify our score is there
                    if not any(s['score'] == test_score['score'] for s in player_scores):
                        save_success = False
                        details += ", Score not found in player scores"
                else:
                    save_success = False
                    details += f", Player scores failed: {player_response.status_code}"
            
            self.log_test("Score Endpoints", save_success, details)
            return save_success
            
        except Exception as e:
            self.log_test("Score Endpoints", False, str(e))
            return False

    def test_cors_headers(self):
        """Test CORS headers"""
        try:
            response = requests.options(f"{self.api_url}/", timeout=10)
            success = response.status_code in [200, 204]
            details = f"Status: {response.status_code}"
            
            if success:
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                }
                details += f", CORS headers present: {bool(cors_headers['Access-Control-Allow-Origin'])}"
            
            self.log_test("CORS Headers", success, details)
            return success
        except Exception as e:
            self.log_test("CORS Headers", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting AbdoulGame API Tests")
        print(f"🎯 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Run tests in order
        self.test_api_root()
        self.test_knowledge_endpoint()
        self.test_game_generation()
        self.test_score_endpoints()
        self.test_cors_headers()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check details above.")
            failed_tests = [r for r in self.test_results if not r['success']]
            print("\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return False

def main():
    tester = AbdoulGameAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())