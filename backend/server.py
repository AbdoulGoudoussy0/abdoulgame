from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import random
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Security Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Input sanitization helper
def sanitize_input(text: str, max_length: int = 100) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', text)
    # Limit length
    return sanitized[:max_length].strip()

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
    """Get a hint for a word - uses predefined hints (no AI cost)"""
    # Predefined hints by language - no AI needed
    hints = {
        "ES": [
            "Busca en las diagonales, ¡ahí se esconden!",
            "Intenta leer de derecha a izquierda también",
            "Las letras brillantes te guían al tesoro",
            "Mira bien las esquinas del tablero",
            "A veces las palabras van hacia arriba"
        ],
        "EN": [
            "Search the diagonals, they hide there!",
            "Try reading right to left as well",
            "The glowing letters guide you to treasure",
            "Look carefully at the board corners",
            "Sometimes words go upward"
        ],
        "FR": [
            "Cherchez dans les diagonales, elles s'y cachent!",
            "Essayez de lire de droite à gauche aussi",
            "Les lettres brillantes vous guident vers le trésor",
            "Regardez bien les coins du plateau",
            "Parfois les mots vont vers le haut"
        ]
    }
    
    encouragements = {
        "ES": ["¡Tú puedes!", "¡Sigue así, campeón!", "¡Casi lo tienes!", "¡Eres increíble!", "¡No te rindas!"],
        "EN": ["You can do it!", "Keep going, champion!", "Almost there!", "You're amazing!", "Don't give up!"],
        "FR": ["Tu peux le faire!", "Continue, champion!", "Tu y es presque!", "Tu es incroyable!", "N'abandonne pas!"]
    }
    
    lang = request.language if request.language in hints else "ES"
    hint = random.choice(hints[lang])
    encouragement = random.choice(encouragements[lang])
    
    return AIHintResponse(hint=hint, encouragement=encouragement)

@api_router.post("/ai/encouragement")
async def get_ai_encouragement(language: str = "ES", words_found: int = 0, total_words: int = 0):
    """Get encouragement based on progress - no AI cost"""
    progress = (words_found / total_words * 100) if total_words > 0 else 0
    
    messages = {
        "ES": {
            "start": "¡Vamos, encuentra tu primera palabra!",
            "progress": f"¡Genial! {words_found} de {total_words} palabras. ¡Sigue así!",
            "almost": "¡Ya casi terminas! ¡Un último esfuerzo!",
            "done": "¡INCREÍBLE! ¡Las encontraste todas!"
        },
        "EN": {
            "start": "Let's go, find your first word!",
            "progress": f"Great! {words_found} of {total_words} words. Keep it up!",
            "almost": "Almost done! One last push!",
            "done": "AMAZING! You found them all!"
        },
        "FR": {
            "start": "Allez, trouvez votre premier mot!",
            "progress": f"Génial! {words_found} sur {total_words} mots. Continue!",
            "almost": "Presque fini! Un dernier effort!",
            "done": "INCROYABLE! Tu les as tous trouvés!"
        }
    }
    
    lang = language if language in messages else "ES"
    
    if progress == 0:
        return {"message": messages[lang]["start"]}
    elif progress >= 100:
        return {"message": messages[lang]["done"]}
    elif progress >= 75:
        return {"message": messages[lang]["almost"]}
    else:
        return {"message": messages[lang]["progress"]}

@api_router.post("/ai/wisdom")
async def get_ai_wisdom(word: str, language: str = "ES"):
    """Get wisdom phrase for a found word - uses predefined phrases (no AI cost)"""
    # Find the word in our knowledge database
    word_data = next((w for w in KNOWLEDGE_DB if w.get(language) == word), None)
    
    if word_data:
        info_key = f"info{language}"
        wisdom = word_data.get(info_key, f"¡Encontraste: {word}!")
        return {"wisdom": wisdom}
    
    # Fallback generic wisdom phrases
    generic_wisdom = {
        "ES": [
            f"{word}: Una palabra que inspira grandeza.",
            f"Has descubierto {word}, símbolo de sabiduría.",
            f"{word} representa el camino hacia el conocimiento."
        ],
        "EN": [
            f"{word}: A word that inspires greatness.",
            f"You discovered {word}, symbol of wisdom.",
            f"{word} represents the path to knowledge."
        ],
        "FR": [
            f"{word}: Un mot qui inspire la grandeur.",
            f"Vous avez découvert {word}, symbole de sagesse.",
            f"{word} représente le chemin vers la connaissance."
        ]
    }
    
    lang = language if language in generic_wisdom else "ES"
    return {"wisdom": random.choice(generic_wisdom[lang])}

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
    # Sanitize player name
    sanitized_name = sanitize_input(input.player_name, 50)
    if not sanitized_name:
        sanitized_name = "Jugador"
    
    # Validate score bounds
    validated_score = max(0, min(input.score, 100000))
    validated_level = max(1, min(input.level, 10))
    validated_words = max(0, min(input.words_found, 20))
    validated_time = max(0, min(input.time_remaining, 300))
    
    score_obj = ScoreRecord(
        player_name=sanitized_name,
        score=validated_score,
        level=validated_level,
        language=input.language[:2].upper() if input.language else "ES",
        words_found=validated_words,
        time_remaining=validated_time
    )
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
    # Sanitize and validate inputs
    sanitized_name = sanitize_input(player_name, 50)
    validated_limit = max(1, min(limit, 100))
    validated_skip = max(0, min(skip, 10000))
    
    scores = await db.scores.find(
        {"player_name": sanitized_name}, 
        {"_id": 0}
    ).sort("score", -1).skip(validated_skip).limit(validated_limit).to_list(validated_limit)
    
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
