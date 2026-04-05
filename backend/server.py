from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import random
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# LLM API Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Knowledge Database - Words with wisdom phrases in multiple languages
KNOWLEDGE_DB = [
    {"id": "virtue", "ES": "VIRTUD", "EN": "VIRTUE", "FR": "VERTU", "infoES": "La virtud es la fuerza del alma.", "infoEN": "Virtue is the soul's strength.", "infoFR": "La vertu est la force de l'âme.", "category": "philosophy"},
    {"id": "logic", "ES": "LOGICA", "EN": "LOGIC", "FR": "LOGIQUE", "infoES": "La lógica es la base de la verdad.", "infoEN": "Logic is the basis of truth.", "infoFR": "La logique est la base de la vérité.", "category": "philosophy"},
    {"id": "honor", "ES": "HONOR", "EN": "HONOR", "FR": "HONNEUR", "infoES": "El honor guía nuestras acciones.", "infoEN": "Honor guides our actions.", "infoFR": "L'honneur guide nos actions.", "category": "values"},
    {"id": "ethics", "ES": "ETICA", "EN": "ETHICS", "FR": "ETHIQUE", "infoES": "La ética es vivir con justicia.", "infoEN": "Ethics is living with justice.", "infoFR": "L'éthique c'est l'art de bien vivre.", "category": "philosophy"},
    {"id": "success", "ES": "EXITO", "EN": "SUCCESS", "FR": "SUCCES", "infoES": "El éxito es persistir.", "infoEN": "Success is persisting.", "infoFR": "Le succès c'est persister.", "category": "motivation"},
    {"id": "wisdom", "ES": "SABIDURIA", "EN": "WISDOM", "FR": "SAGESSE", "infoES": "La sabiduría es el arte de vivir.", "infoEN": "Wisdom is the art of living.", "infoFR": "La sagesse est l'art de vivre.", "category": "philosophy"},
    {"id": "courage", "ES": "VALOR", "EN": "COURAGE", "FR": "COURAGE", "infoES": "El valor nos hace libres.", "infoEN": "Courage sets us free.", "infoFR": "Le courage nous libère.", "category": "values"},
    {"id": "peace", "ES": "PAZ", "EN": "PEACE", "FR": "PAIX", "infoES": "La paz comienza dentro de ti.", "infoEN": "Peace begins within you.", "infoFR": "La paix commence en toi.", "category": "spirituality"},
    {"id": "truth", "ES": "VERDAD", "EN": "TRUTH", "FR": "VERITE", "infoES": "La verdad siempre prevalece.", "infoEN": "Truth always prevails.", "infoFR": "La vérité prévaut toujours.", "category": "values"},
    {"id": "hope", "ES": "ESPERANZA", "EN": "HOPE", "FR": "ESPOIR", "infoES": "La esperanza es el motor del alma.", "infoEN": "Hope is the soul's engine.", "infoFR": "L'espoir est le moteur de l'âme.", "category": "spirituality"},
    {"id": "dream", "ES": "SUENO", "EN": "DREAM", "FR": "REVE", "infoES": "Los sueños construyen el futuro.", "infoEN": "Dreams build the future.", "infoFR": "Les rêves construisent l'avenir.", "category": "motivation"},
    {"id": "glory", "ES": "GLORIA", "EN": "GLORY", "FR": "GLOIRE", "infoES": "La gloria llega con esfuerzo.", "infoEN": "Glory comes with effort.", "infoFR": "La gloire vient avec l'effort.", "category": "motivation"},
    {"id": "love", "ES": "AMOR", "EN": "LOVE", "FR": "AMOUR", "infoES": "El amor todo lo puede.", "infoEN": "Love conquers all.", "infoFR": "L'amour peut tout.", "category": "spirituality"},
    {"id": "faith", "ES": "FE", "EN": "FAITH", "FR": "FOI", "infoES": "La fe mueve montañas.", "infoEN": "Faith moves mountains.", "infoFR": "La foi déplace les montagnes.", "category": "spirituality"},
    {"id": "strength", "ES": "FUERZA", "EN": "STRENGTH", "FR": "FORCE", "infoES": "La fuerza nace del interior.", "infoEN": "Strength comes from within.", "infoFR": "La force vient de l'intérieur.", "category": "motivation"},
    {"id": "unity", "ES": "UNION", "EN": "UNITY", "FR": "UNITE", "infoES": "La unión hace la fuerza.", "infoEN": "Unity is strength.", "infoFR": "L'union fait la force.", "category": "values"},
    {"id": "life", "ES": "VIDA", "EN": "LIFE", "FR": "VIE", "infoES": "La vida es un regalo.", "infoEN": "Life is a gift.", "infoFR": "La vie est un cadeau.", "category": "philosophy"},
    {"id": "soul", "ES": "ALMA", "EN": "SOUL", "FR": "AME", "infoES": "El alma es eterna.", "infoEN": "The soul is eternal.", "infoFR": "L'âme est éternelle.", "category": "spirituality"},
]

# Models
class ScoreRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_name: str
    score: int
    level: int
    language: str
    words_found: int = 0
    time_remaining: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScoreCreate(BaseModel):
    player_name: str
    score: int
    level: int
    language: str
    words_found: int = 0
    time_remaining: int = 0

class WordPlacement(BaseModel):
    word: str
    info: str
    coords: List[dict]
    category: str = "general"

class GameBoard(BaseModel):
    matrix: List[List[str]]
    size: int
    words: List[WordPlacement]
    level: int
    time_limit: int

class GameRequest(BaseModel):
    level: int
    language: str

class AIHintRequest(BaseModel):
    word: str
    language: str
    found_letters: List[str] = []

class AIHintResponse(BaseModel):
    hint: str
    encouragement: str

class AIGenerateWordsRequest(BaseModel):
    language: str
    category: str = "general"
    count: int = 3

class ShareData(BaseModel):
    score: int
    level: int
    words_found: int
    language: str

# Helper functions
def can_place_word(matrix, word, row, col, direction, size):
    dr, dc = direction
    for i, letter in enumerate(word):
        nr = row + i * dr
        nc = col + i * dc
        if nr < 0 or nr >= size or nc < 0 or nc >= size:
            return False
        if matrix[nr][nc] and matrix[nr][nc] != letter:
            return False
    return True

def place_word(matrix, word, row, col, direction):
    coords = []
    dr, dc = direction
    for i, letter in enumerate(word):
        nr = row + i * dr
        nc = col + i * dc
        matrix[nr][nc] = letter
        coords.append({"r": nr, "c": nc})
    return coords

def get_level_config(level: int):
    """Get game configuration based on level"""
    configs = {
        1: {"size": 8, "words": 3, "time": 150},
        2: {"size": 8, "words": 4, "time": 140},
        3: {"size": 9, "words": 4, "time": 130},
        4: {"size": 9, "words": 5, "time": 125},
        5: {"size": 10, "words": 5, "time": 120},
        6: {"size": 10, "words": 6, "time": 115},
        7: {"size": 11, "words": 6, "time": 110},
        8: {"size": 11, "words": 7, "time": 105},
        9: {"size": 12, "words": 7, "time": 100},
        10: {"size": 12, "words": 8, "time": 95},
    }
    level = max(1, min(level, 10))
    return configs.get(level, configs[10])

def generate_board(size: int, words: List[dict], language: str, level: int) -> GameBoard:
    directions = [(0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)]
    word_placements = []
    config = get_level_config(level)
    
    placed = False
    attempts = 0
    max_attempts = 100
    
    while not placed and attempts < max_attempts:
        attempts += 1
        matrix = [['' for _ in range(size)] for _ in range(size)]
        placed = True
        word_placements = []
        
        for word_data in words:
            word = word_data[language]
            info = word_data.get(f"info{language}", "")
            category = word_data.get("category", "general")
            word_placed = False
            
            for _ in range(200):
                direction = random.choice(directions)
                row = random.randint(0, size - 1)
                col = random.randint(0, size - 1)
                
                if can_place_word(matrix, word, row, col, direction, size):
                    coords = place_word(matrix, word, row, col, direction)
                    word_placements.append(WordPlacement(word=word, info=info, coords=coords, category=category))
                    word_placed = True
                    break
            
            if not word_placed:
                placed = False
                break
    
    # Fill empty cells with random letters
    for r in range(size):
        for c in range(size):
            if not matrix[r][c]:
                matrix[r][c] = chr(65 + random.randint(0, 25))
    
    return GameBoard(matrix=matrix, size=size, words=word_placements, level=level, time_limit=config["time"])

# API Routes
@api_router.get("/")
async def root():
    return {"message": "AbdoulGame API - Polyglot Word Search", "version": "2.0"}

@api_router.get("/knowledge")
async def get_knowledge():
    return KNOWLEDGE_DB

@api_router.post("/game/generate", response_model=GameBoard)
async def generate_game(request: GameRequest):
    level = max(1, min(request.level, 10))
    language = request.language.upper() if request.language.upper() in ["ES", "EN", "FR"] else "ES"
    
    config = get_level_config(level)
    size = config["size"]
    num_words = config["words"]
    
    # Randomly select words for this game
    selected_words = random.sample(KNOWLEDGE_DB, min(num_words, len(KNOWLEDGE_DB)))
    
    return generate_board(size, selected_words, language, level)

@api_router.post("/ai/hint", response_model=AIHintResponse)
async def get_ai_hint(request: AIHintRequest):
    """Get an intelligent AI-generated hint for a word"""
    if not EMERGENT_LLM_KEY:
        return AIHintResponse(
            hint="Busca las letras que forman esta palabra de sabiduría.",
            encouragement="¡Tú puedes encontrarla!"
        )
    
    lang_names = {"ES": "Spanish", "EN": "English", "FR": "French"}
    lang_name = lang_names.get(request.language, "Spanish")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"hint-{uuid.uuid4()}",
            system_message=f"""You are a wise and encouraging game assistant for a word search game. 
            Respond ONLY in {lang_name}. Be warm, motivating, and give clever hints without revealing the answer directly.
            Keep responses short (1-2 sentences max for hint, 1 sentence for encouragement)."""
        ).with_model("openai", "gpt-4o")
        
        found_str = ", ".join(request.found_letters) if request.found_letters else "none yet"
        
        message = UserMessage(
            text=f"Give a creative hint for finding the word '{request.word}' in a word search. Letters found so far: {found_str}. Don't reveal the word directly. Also add a short motivational encouragement."
        )
        
        response = await chat.send_message(message)
        
        # Parse response - expect hint and encouragement
        lines = response.strip().split('\n')
        hint = lines[0] if lines else "Sigue buscando..."
        encouragement = lines[1] if len(lines) > 1 else "¡Vas muy bien!"
        
        return AIHintResponse(hint=hint, encouragement=encouragement)
    except Exception as e:
        logging.error(f"AI Hint error: {e}")
        fallback_hints = {
            "ES": ("Piensa en el significado profundo de esta palabra.", "¡Confía en tu intuición!"),
            "EN": ("Think about the deep meaning of this word.", "Trust your intuition!"),
            "FR": ("Pensez au sens profond de ce mot.", "Faites confiance à votre intuition!")
        }
        hint, enc = fallback_hints.get(request.language, fallback_hints["ES"])
        return AIHintResponse(hint=hint, encouragement=enc)

@api_router.post("/ai/encouragement")
async def get_ai_encouragement(language: str = "ES", words_found: int = 0, total_words: int = 0):
    """Get personalized AI encouragement based on progress"""
    if not EMERGENT_LLM_KEY:
        messages = {
            "ES": "¡Sigue así, campeón!",
            "EN": "Keep going, champion!",
            "FR": "Continue comme ça, champion!"
        }
        return {"message": messages.get(language, messages["ES"])}
    
    lang_names = {"ES": "Spanish", "EN": "English", "FR": "French"}
    lang_name = lang_names.get(language, "Spanish")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"encourage-{uuid.uuid4()}",
            system_message=f"You are an enthusiastic sports commentator for a word game. Respond ONLY in {lang_name}. Be exciting and motivating! Keep it to 1 short sentence."
        ).with_model("openai", "gpt-4o")
        
        progress = (words_found / total_words * 100) if total_words > 0 else 0
        
        message = UserMessage(
            text=f"Player found {words_found} of {total_words} words ({progress:.0f}% complete). Give a short, exciting encouragement like a football commentator!"
        )
        
        response = await chat.send_message(message)
        return {"message": response.strip()}
    except Exception as e:
        logging.error(f"AI Encouragement error: {e}")
        return {"message": "¡Increíble jugada! ¡Sigue adelante!"}

@api_router.post("/ai/wisdom")
async def get_ai_wisdom(word: str, language: str = "ES"):
    """Generate AI wisdom phrase for a found word"""
    if not EMERGENT_LLM_KEY:
        return {"wisdom": f"Has encontrado: {word}"}
    
    lang_names = {"ES": "Spanish", "EN": "English", "FR": "French"}
    lang_name = lang_names.get(language, "Spanish")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"wisdom-{uuid.uuid4()}",
            system_message=f"You are a wise philosopher. Generate a profound but short wisdom phrase about a concept. Respond ONLY in {lang_name}. Maximum 15 words."
        ).with_model("openai", "gpt-4o")
        
        message = UserMessage(text=f"Create a short, inspiring wisdom phrase about '{word}'")
        response = await chat.send_message(message)
        return {"wisdom": response.strip()}
    except Exception as e:
        logging.error(f"AI Wisdom error: {e}")
        return {"wisdom": f"💡 {word}: Una palabra de poder y significado."}

@api_router.post("/share/generate")
async def generate_share_text(data: ShareData):
    """Generate shareable text for social media"""
    lang_templates = {
        "ES": f"🏆 ¡Acabo de completar el Nivel {data.level} en AbdoulGame!\n⭐ Puntuación: {data.score}\n📝 Palabras encontradas: {data.words_found}\n\n¿Puedes superarme? 🎮\n#AbdoulGame #WordSearch #Polyglot",
        "EN": f"🏆 Just completed Level {data.level} in AbdoulGame!\n⭐ Score: {data.score}\n📝 Words found: {data.words_found}\n\nCan you beat me? 🎮\n#AbdoulGame #WordSearch #Polyglot",
        "FR": f"🏆 Je viens de terminer le Niveau {data.level} dans AbdoulGame!\n⭐ Score: {data.score}\n📝 Mots trouvés: {data.words_found}\n\nPouvez-vous me battre? 🎮\n#AbdoulGame #WordSearch #Polyglot"
    }
    return {"text": lang_templates.get(data.language, lang_templates["ES"])}

@api_router.post("/scores", response_model=ScoreRecord)
async def save_score(input: ScoreCreate):
    score_obj = ScoreRecord(**input.model_dump())
    doc = score_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.scores.insert_one(doc)
    return score_obj

@api_router.get("/scores/top", response_model=List[ScoreRecord])
async def get_top_scores(limit: int = 10):
    scores = await db.scores.find({}, {"_id": 0}).sort("score", -1).limit(limit).to_list(limit)
    for score in scores:
        if isinstance(score['timestamp'], str):
            score['timestamp'] = datetime.fromisoformat(score['timestamp'])
    return scores

@api_router.get("/scores/player/{player_name}", response_model=List[ScoreRecord])
async def get_player_scores(player_name: str, limit: int = 20, skip: int = 0):
    scores = await db.scores.find({"player_name": player_name}, {"_id": 0}).sort("score", -1).skip(skip).limit(limit).to_list(limit)
    for score in scores:
        if isinstance(score['timestamp'], str):
            score['timestamp'] = datetime.fromisoformat(score['timestamp'])
    return scores

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
