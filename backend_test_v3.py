import requests
import sys
import json
import time
from datetime import datetime

class AbdoulGameV3Tester:
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
                if 'message' in data and 'version' in data:
                    details += f", Message: {data['message']}, Version: {data['version']}"
                else:
                    success = False
                    details += ", Missing message or version"
            
            self.log_test("API Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, str(e))
            return False

    def test_knowledge_database(self):
        """Test knowledge database endpoint"""
        try:
            response = requests.get(f"{self.api_url}/knowledge", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check structure of first item
                    first_item = data[0]
                    required_fields = ['id', 'ES', 'EN', 'FR', 'infoES', 'infoEN', 'infoFR', 'category']
                    missing_fields = [field for field in required_fields if field not in first_item]
                    
                    if missing_fields:
                        success = False
                        details += f", Missing fields: {missing_fields}"
                    else:
                        details += f", Items: {len(data)}, Languages: ES/EN/FR supported"
                else:
                    success = False
                    details += ", Empty or invalid knowledge database"
            
            self.log_test("Knowledge Database", success, details)
            return success
        except Exception as e:
            self.log_test("Knowledge Database", False, str(e))
            return False

    def test_game_generation_multilingual(self):
        """Test game generation for all languages and levels"""
        languages = ["ES", "EN", "FR"]
        levels = [1, 5, 10]  # Test low, mid, high levels
        
        all_passed = True
        for lang in languages:
            for level in levels:
                try:
                    response = requests.post(
                        f"{self.api_url}/game/generate",
                        json={"level": level, "language": lang},
                        headers={'Content-Type': 'application/json'},
                        timeout=15
                    )
                    success = response.status_code == 200
                    details = f"Level: {level}, Lang: {lang}, Status: {response.status_code}"
                    
                    if success:
                        data = response.json()
                        required_fields = ['matrix', 'size', 'words', 'level', 'time_limit']
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            success = False
                            details += f", Missing fields: {missing_fields}"
                        else:
                            matrix = data['matrix']
                            words = data['words']
                            size = data['size']
                            time_limit = data['time_limit']
                            
                            # Validate matrix structure
                            if len(matrix) != size or any(len(row) != size for row in matrix):
                                success = False
                                details += ", Invalid matrix dimensions"
                            elif len(words) == 0:
                                success = False
                                details += ", No words generated"
                            else:
                                details += f", Size: {size}x{size}, Words: {len(words)}, Time: {time_limit}s"
                                
                                # Check if words have correct language
                                for word_obj in words:
                                    if 'word' not in word_obj or 'coords' not in word_obj:
                                        success = False
                                        details += ", Invalid word structure"
                                        break
                    
                    self.log_test(f"Game Generation {lang} Level {level}", success, details)
                    if not success:
                        all_passed = False
                        
                except Exception as e:
                    self.log_test(f"Game Generation {lang} Level {level}", False, str(e))
                    all_passed = False
        
        return all_passed

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
                
                self.log_test(f"AI Hint {case['language']} - {case['word']}", success, details)
                if not success:
                    all_passed = False
                    
                # Add delay between AI calls to avoid rate limiting
                time.sleep(1)
                    
            except Exception as e:
                self.log_test(f"AI Hint {case['language']} - {case['word']}", False, str(e))
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
                        elif "#AbdoulGame" not in text:
                            success = False
                            details += ", Missing hashtag"
                
                self.log_test(f"Share Generation {case['language']}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Share Generation {case['language']}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_score_endpoints(self):
        """Test score saving and retrieval endpoints"""
        # Test score saving
        test_score = {
            "player_name": f"TestPlayer_{int(time.time())}",
            "score": 1500,
            "level": 5,
            "language": "ES",
            "words_found": 6,
            "time_remaining": 45
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
            save_details = f"Status: {response.status_code}"
            
            if save_success:
                saved_score = response.json()
                if 'id' in saved_score:
                    save_details += f", Score ID: {saved_score['id']}"
                else:
                    save_success = False
                    save_details += ", Missing score ID"
            
            self.log_test("Score Saving", save_success, save_details)
            
            # Test top scores retrieval
            response = requests.get(f"{self.api_url}/scores/top?limit=5", timeout=10)
            top_success = response.status_code == 200
            top_details = f"Status: {response.status_code}"
            
            if top_success:
                top_scores = response.json()
                if isinstance(top_scores, list):
                    top_details += f", Retrieved {len(top_scores)} scores"
                else:
                    top_success = False
                    top_details += ", Invalid response format"
            
            self.log_test("Top Scores Retrieval", top_success, top_details)
            
            # Test player scores retrieval
            response = requests.get(f"{self.api_url}/scores/player/{test_score['player_name']}", timeout=10)
            player_success = response.status_code == 200
            player_details = f"Status: {response.status_code}"
            
            if player_success:
                player_scores = response.json()
                if isinstance(player_scores, list):
                    player_details += f", Retrieved {len(player_scores)} player scores"
                else:
                    player_success = False
                    player_details += ", Invalid response format"
            
            self.log_test("Player Scores Retrieval", player_success, player_details)
            
            return save_success and top_success and player_success
            
        except Exception as e:
            self.log_test("Score Endpoints", False, str(e))
            return False

    def run_all_tests(self):
        """Run all V3 backend tests"""
        print(f"🚀 Starting AbdoulGame V3 Backend Tests")
        print(f"🎯 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Run core API tests
        print("\n🔧 Testing Core API...")
        self.test_api_root()
        self.test_knowledge_database()
        
        print("\n🎮 Testing Game Generation...")
        self.test_game_generation_multilingual()
        
        print("\n🤖 Testing AI Features...")
        self.test_ai_hint_endpoint()
        
        print("\n📱 Testing Share Functionality...")
        self.test_share_generation_endpoint()
        
        print("\n💾 Testing Score System...")
        self.test_score_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All V3 backend features working perfectly!")
            return True
        else:
            print("⚠️  Some backend features failed. Check details above.")
            failed_tests = [r for r in self.test_results if not r['success']]
            print("\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return False

def main():
    tester = AbdoulGameV3Tester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())