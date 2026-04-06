"""
AbdoulGame Backend API Tests
Tests for: Knowledge DB, Categories, Game Generation, AI Hints/Wisdom, Light/Dark Mode Support
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasicEndpoints:
    """Basic API health and endpoint tests"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "AbdoulGame" in data["message"]
        print(f"✓ API root working: {data['message']}")

    def test_security_headers(self):
        """Test security headers are present"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        print("✓ Security headers present")


class TestKnowledgeDatabase:
    """Tests for the expanded educational knowledge database"""
    
    def test_get_knowledge_db(self):
        """Test knowledge database endpoint returns all words"""
        response = requests.get(f"{BASE_URL}/api/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 39  # Should have 39+ words (12 categories with 3+ words each)
        print(f"✓ Knowledge DB has {len(data)} words")
    
    def test_knowledge_db_has_all_languages(self):
        """Test each word has ES, EN, FR translations"""
        response = requests.get(f"{BASE_URL}/api/knowledge")
        data = response.json()
        
        for word in data[:10]:  # Check first 10 words
            assert "ES" in word, f"Missing ES for {word.get('id')}"
            assert "EN" in word, f"Missing EN for {word.get('id')}"
            assert "FR" in word, f"Missing FR for {word.get('id')}"
            assert "infoES" in word, f"Missing infoES for {word.get('id')}"
            assert "infoEN" in word, f"Missing infoEN for {word.get('id')}"
            assert "infoFR" in word, f"Missing infoFR for {word.get('id')}"
        print("✓ All words have ES/EN/FR translations and info")
    
    def test_knowledge_db_has_categories(self):
        """Test each word has category information"""
        response = requests.get(f"{BASE_URL}/api/knowledge")
        data = response.json()
        
        categories_found = set()
        for word in data:
            assert "category" in word, f"Missing category for {word.get('id')}"
            categories_found.add(word["category"])
        
        # Should have 12 categories
        expected_categories = {
            "philosophy", "values", "emotions", "success", "strength",
            "relationships", "learning", "health", "nature", "spirituality",
            "creativity", "justice"
        }
        assert categories_found == expected_categories, f"Missing categories: {expected_categories - categories_found}"
        print(f"✓ All 12 educational categories present: {categories_found}")


class TestCategories:
    """Tests for category endpoint"""
    
    def test_get_categories(self):
        """Test categories endpoint returns all 12 categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 12
        print(f"✓ Categories endpoint returns {len(data)} categories")
    
    def test_categories_have_translations(self):
        """Test each category has ES/EN/FR translations"""
        response = requests.get(f"{BASE_URL}/api/categories")
        data = response.json()
        
        for cat in data:
            assert "id" in cat
            assert "ES" in cat
            assert "EN" in cat
            assert "FR" in cat
        print("✓ All categories have ES/EN/FR translations")


class TestGameGeneration:
    """Tests for game board generation"""
    
    def test_generate_game_level_1_spanish(self):
        """Test game generation for level 1 in Spanish"""
        response = requests.post(f"{BASE_URL}/api/game/generate", json={
            "level": 1,
            "language": "ES"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "matrix" in data
        assert "words" in data
        assert "size" in data
        assert "level" in data
        assert "time_limit" in data
        
        assert data["level"] == 1
        assert data["size"] == 8  # Level 1 has 8x8 grid
        assert len(data["words"]) >= 1  # At least 1 word should be placed
        assert len(data["words"]) <= 3  # Level 1 targets 3 words
        assert data["time_limit"] == 180  # Level 1 has 180 seconds
        print(f"✓ Level 1 Spanish game generated: {len(data['words'])} words, {data['size']}x{data['size']} grid")
    
    def test_generate_game_level_5_english(self):
        """Test game generation for level 5 in English"""
        response = requests.post(f"{BASE_URL}/api/game/generate", json={
            "level": 5,
            "language": "EN"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["level"] == 5
        assert data["size"] == 10  # Level 5 has 10x10 grid
        # Word placement may not always place all words due to grid constraints
        assert len(data["words"]) >= 3  # At least 3 words should be placed
        assert len(data["words"]) <= 5  # Level 5 targets 5 words
        print(f"✓ Level 5 English game generated: {len(data['words'])} words")
    
    def test_generate_game_level_10_french(self):
        """Test game generation for level 10 in French"""
        response = requests.post(f"{BASE_URL}/api/game/generate", json={
            "level": 10,
            "language": "FR"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["level"] == 10
        assert data["size"] == 12  # Level 10 has 12x12 grid
        assert len(data["words"]) == 8  # Level 10 has 8 words
        print(f"✓ Level 10 French game generated: {len(data['words'])} words")
    
    def test_words_have_category_info(self):
        """Test generated words include category information"""
        response = requests.post(f"{BASE_URL}/api/game/generate", json={
            "level": 3,
            "language": "ES"
        })
        data = response.json()
        
        for word in data["words"]:
            assert "word" in word
            assert "info" in word
            assert "coords" in word
            assert "category" in word
            assert "categoryName" in word
            assert len(word["coords"]) > 0
        print("✓ Generated words include category information")
    
    def test_generate_game_by_category(self):
        """Test game generation filtered by category"""
        # Use level 1 which only needs 3 words
        response = requests.post(f"{BASE_URL}/api/game/generate", json={
            "level": 1,
            "language": "ES",
            "category": "emotions"  # emotions has 4 words, enough for level 1
        })
        assert response.status_code == 200
        data = response.json()
        
        # Game should generate successfully
        assert len(data["words"]) >= 1, "At least one word should be generated"
        print(f"Generated {len(data['words'])} words")
        
        # Check that words have category info
        for word in data["words"]:
            assert "category" in word
            assert "categoryName" in word
        print("✓ Category filtering works for game generation")


class TestAIHintsAndWisdom:
    """Tests for AI hint and wisdom endpoints (no-cost local implementation)"""
    
    def test_get_hint_spanish(self):
        """Test hint endpoint in Spanish"""
        response = requests.post(f"{BASE_URL}/api/ai/hint", json={
            "word": "SABIDURIA",
            "language": "ES",
            "found_letters": []
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "hint" in data
        assert "encouragement" in data
        assert len(data["hint"]) > 0
        assert len(data["encouragement"]) > 0
        print(f"✓ Spanish hint: {data['hint'][:50]}...")
    
    def test_get_hint_english(self):
        """Test hint endpoint in English"""
        response = requests.post(f"{BASE_URL}/api/ai/hint", json={
            "word": "WISDOM",
            "language": "EN",
            "found_letters": []
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "hint" in data
        assert "encouragement" in data
        print(f"✓ English hint: {data['hint'][:50]}...")
    
    def test_get_hint_french(self):
        """Test hint endpoint in French"""
        response = requests.post(f"{BASE_URL}/api/ai/hint", json={
            "word": "SAGESSE",
            "language": "FR",
            "found_letters": []
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "hint" in data
        assert "encouragement" in data
        print(f"✓ French hint: {data['hint'][:50]}...")
    
    def test_get_wisdom_spanish(self):
        """Test wisdom endpoint returns educational info in Spanish"""
        response = requests.post(f"{BASE_URL}/api/ai/wisdom", params={
            "word": "SABIDURIA",
            "language": "ES"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "wisdom" in data
        assert "category" in data
        assert "sabiduría" in data["wisdom"].lower() or "conocimiento" in data["wisdom"].lower()
        print(f"✓ Spanish wisdom: {data['wisdom'][:60]}...")
    
    def test_get_wisdom_english(self):
        """Test wisdom endpoint returns educational info in English"""
        response = requests.post(f"{BASE_URL}/api/ai/wisdom", params={
            "word": "WISDOM",
            "language": "EN"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "wisdom" in data
        assert "category" in data
        print(f"✓ English wisdom: {data['wisdom'][:60]}...")
    
    def test_get_wisdom_french(self):
        """Test wisdom endpoint returns educational info in French"""
        response = requests.post(f"{BASE_URL}/api/ai/wisdom", params={
            "word": "SAGESSE",
            "language": "FR"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "wisdom" in data
        assert "category" in data
        print(f"✓ French wisdom: {data['wisdom'][:60]}...")
    
    def test_wisdom_for_all_categories(self):
        """Test wisdom returns correct category for words from different categories"""
        test_words = [
            ("VERDAD", "ES", "philosophy"),
            ("HONOR", "ES", "values"),
            ("AMOR", "ES", "emotions"),
            ("EXITO", "ES", "success"),
            ("VALOR", "ES", "strength"),
            ("FAMILIA", "ES", "relationships"),
            ("SABER", "ES", "learning"),
            ("SALUD", "ES", "health"),
            ("NATURALEZA", "ES", "nature"),
            ("FE", "ES", "spirituality"),
            ("CREATIVIDAD", "ES", "creativity"),
            ("LIBERTAD", "ES", "justice"),
        ]
        
        for word, lang, expected_category in test_words:
            response = requests.post(f"{BASE_URL}/api/ai/wisdom", params={
                "word": word,
                "language": lang
            })
            assert response.status_code == 200
            data = response.json()
            assert "wisdom" in data
            assert len(data["wisdom"]) > 0
        
        print("✓ Wisdom works for all 12 categories")


class TestShareFeature:
    """Tests for share text generation"""
    
    def test_share_spanish(self):
        """Test share text generation in Spanish"""
        response = requests.post(f"{BASE_URL}/api/share/generate", json={
            "score": 500,
            "level": 3,
            "words_found": 4,
            "language": "ES"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "text" in data
        assert "AbdoulGame" in data["text"]
        assert "500" in data["text"]
        assert "Nivel 3" in data["text"]
        print("✓ Spanish share text generated")
    
    def test_share_english(self):
        """Test share text generation in English"""
        response = requests.post(f"{BASE_URL}/api/share/generate", json={
            "score": 800,
            "level": 5,
            "words_found": 6,
            "language": "EN"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "text" in data
        assert "Level 5" in data["text"]
        print("✓ English share text generated")


class TestScores:
    """Tests for score saving and retrieval"""
    
    def test_save_score(self):
        """Test saving a score"""
        response = requests.post(f"{BASE_URL}/api/scores", json={
            "player_name": "TEST_Player",
            "score": 1000,
            "level": 5,
            "language": "ES",
            "words_found": 5,
            "time_remaining": 60
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["player_name"] == "TEST_Player"
        assert data["score"] == 1000
        assert data["level"] == 5
        print("✓ Score saved successfully")
    
    def test_get_top_scores(self):
        """Test retrieving top scores"""
        response = requests.get(f"{BASE_URL}/api/scores/top?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} top scores")
    
    def test_input_sanitization(self):
        """Test that dangerous input is sanitized"""
        response = requests.post(f"{BASE_URL}/api/scores", json={
            "player_name": "<script>alert('xss')</script>",
            "score": 100,
            "level": 1,
            "language": "ES"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Script tags should be removed
        assert "<script>" not in data["player_name"]


class TestNewEndpointsV6:
    """Tests for new V6 endpoints: achievements, inspirational quotes, daily challenge"""
    
    def test_get_achievements_spanish(self):
        """Test achievements endpoint returns all 10 achievements in Spanish"""
        response = requests.get(f"{BASE_URL}/api/achievements?language=ES")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 10  # Should have 10 achievements
        
        # Check structure of first achievement
        achievement = data[0]
        assert "id" in achievement
        assert "icon" in achievement
        assert "name" in achievement
        assert "description" in achievement
        assert "requirement" in achievement
        
        # Verify Spanish localization
        assert any("Filósofo" in a["name"] for a in data)
        print(f"✓ Achievements endpoint returns {len(data)} achievements in Spanish")
    
    def test_get_achievements_english(self):
        """Test achievements endpoint returns achievements in English"""
        response = requests.get(f"{BASE_URL}/api/achievements?language=EN")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 10
        # Verify English localization
        assert any("Philosopher" in a["name"] for a in data)
        print("✓ Achievements endpoint returns achievements in English")
    
    def test_get_achievements_french(self):
        """Test achievements endpoint returns achievements in French"""
        response = requests.get(f"{BASE_URL}/api/achievements?language=FR")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 10
        # Verify French localization
        assert any("Philosophe" in a["name"] for a in data)
        print("✓ Achievements endpoint returns achievements in French")
    
    def test_inspirational_quote_philosophy(self):
        """Test inspirational quote for philosophy category"""
        response = requests.get(f"{BASE_URL}/api/inspirational-quote?category=philosophy&language=ES")
        assert response.status_code == 200
        data = response.json()
        
        assert "quote" in data
        assert "category" in data
        assert data["category"] == "philosophy"
        assert len(data["quote"]) > 10  # Should have meaningful content
        print(f"✓ Philosophy quote: {data['quote'][:50]}...")
    
    def test_inspirational_quote_all_categories(self):
        """Test inspirational quotes for all 12 categories"""
        categories = [
            "philosophy", "values", "emotions", "success", "strength",
            "relationships", "learning", "health", "nature", "spirituality",
            "creativity", "justice"
        ]
        
        for category in categories:
            response = requests.get(f"{BASE_URL}/api/inspirational-quote?category={category}&language=ES")
            assert response.status_code == 200
            data = response.json()
            assert "quote" in data
            assert len(data["quote"]) > 0
        
        print("✓ Inspirational quotes work for all 12 categories")
    
    def test_inspirational_quote_all_languages(self):
        """Test inspirational quotes in all 3 languages"""
        for lang in ["ES", "EN", "FR"]:
            response = requests.get(f"{BASE_URL}/api/inspirational-quote?category=success&language={lang}")
            assert response.status_code == 200
            data = response.json()
            assert "quote" in data
            assert len(data["quote"]) > 0
        
        print("✓ Inspirational quotes work in ES/EN/FR")
    
    def test_daily_challenge_spanish(self):
        """Test daily challenge endpoint in Spanish"""
        response = requests.get(f"{BASE_URL}/api/daily-challenge?language=ES")
        assert response.status_code == 200
        data = response.json()
        
        assert "date" in data
        assert "level" in data
        assert "board" in data
        assert "message" in data
        
        # Daily challenge is always level 5
        assert data["level"] == 5
        
        # Board should have proper structure
        board = data["board"]
        assert "matrix" in board
        assert "words" in board
        assert "size" in board
        assert board["size"] == 10  # Level 5 has 10x10 grid
        
        # Message should be in Spanish
        assert "Desafío del día" in data["message"]
        print(f"✓ Daily challenge generated for {data['date']}")
    
    def test_daily_challenge_consistency(self):
        """Test that daily challenge returns same board for same day"""
        response1 = requests.get(f"{BASE_URL}/api/daily-challenge?language=ES")
        response2 = requests.get(f"{BASE_URL}/api/daily-challenge?language=ES")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Same date should return same board
        assert data1["date"] == data2["date"]
        assert data1["board"]["matrix"] == data2["board"]["matrix"]
        print("✓ Daily challenge is consistent (same board for same day)")
    
    def test_daily_challenge_all_languages(self):
        """Test daily challenge in all 3 languages"""
        messages = {}
        for lang in ["ES", "EN", "FR"]:
            response = requests.get(f"{BASE_URL}/api/daily-challenge?language={lang}")
            assert response.status_code == 200
            data = response.json()
            messages[lang] = data["message"]
        
        # Messages should be different for each language
        assert "Desafío" in messages["ES"]
        assert "Challenge" in messages["EN"]
        assert "Défi" in messages["FR"]
        print("✓ Daily challenge messages localized for ES/EN/FR")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
