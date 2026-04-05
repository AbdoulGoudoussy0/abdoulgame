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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Knowledge Database - Words with wisdom phrases in multiple languages
KNOWLEDGE_DB = [
    {"id": "virtue", "ES": "VIRTUD", "EN": "VIRTUE", "FR": "VERTU", "infoES": "La virtud es la fuerza del alma.", "infoEN": "Virtue is the soul's strength.", "infoFR": "La vertu est la force de l'âme."},
    {"id": "logic", "ES": "LOGICA", "EN": "LOGIC", "FR": "LOGIQUE", "infoES": "La lógica es la base de la verdad.", "infoEN": "Logic is the basis of truth.", "infoFR": "La logique est la base de la vérité."},
    {"id": "honor", "ES": "HONOR", "EN": "HONOR", "FR": "HONNEUR", "infoES": "El honor guía nuestras acciones.", "infoEN": "Honor guides our actions.", "infoFR": "L'honneur guide nos actions."},
    {"id": "ethics", "ES": "ETICA", "EN": "ETHICS", "FR": "ETHIQUE", "infoES": "La ética es vivir con justicia.", "infoEN": "Ethics is living with justice.", "infoFR": "L'éthique c'est l'art de bien vivre."},
    {"id": "success", "ES": "EXITO", "EN": "SUCCESS", "FR": "SUCCES", "infoES": "El éxito es persistir.", "infoEN": "Success is persisting.", "infoFR": "Le succès c'est persister."},
    {"id": "wisdom", "ES": "SABIDURIA", "EN": "WISDOM", "FR": "SAGESSE", "infoES": "La sabiduría es el arte de vivir.", "infoEN": "Wisdom is the art of living.", "infoFR": "La sagesse est l'art de vivre."},
    {"id": "courage", "ES": "VALOR", "EN": "COURAGE", "FR": "COURAGE", "infoES": "El valor nos hace libres.", "infoEN": "Courage sets us free.", "infoFR": "Le courage nous libère."},
    {"id": "peace", "ES": "PAZ", "EN": "PEACE", "FR": "PAIX", "infoES": "La paz comienza dentro de ti.", "infoEN": "Peace begins within you.", "infoFR": "La paix commence en toi."},
    {"id": "truth", "ES": "VERDAD", "EN": "TRUTH", "FR": "VERITE", "infoES": "La verdad siempre prevalece.", "infoEN": "Truth always prevails.", "infoFR": "La vérité prévaut toujours."},
    {"id": "hope", "ES": "ESPERANZA", "EN": "HOPE", "FR": "ESPOIR", "infoES": "La esperanza es el motor del alma.", "infoEN": "Hope is the soul's engine.", "infoFR": "L'espoir est le moteur de l'âme."},
    {"id": "dream", "ES": "SUENO", "EN": "DREAM", "FR": "REVE", "infoES": "Los sueños construyen el futuro.", "infoEN": "Dreams build the future.", "infoFR": "Les rêves construisent l'avenir."},
    {"id": "glory", "ES": "GLORIA", "EN": "GLORY", "FR": "GLOIRE", "infoES": "La gloria llega con esfuerzo.", "infoEN": "Glory comes with effort.", "infoFR": "La gloire vient avec l'effort."},
]

# Models
class ScoreRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_name: str
    score: int
    level: int
    language: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScoreCreate(BaseModel):
    player_name: str
    score: int
    level: int
    language: str

class WordPlacement(BaseModel):
    word: str
    info: str
    coords: List[dict]

class GameBoard(BaseModel):
    matrix: List[List[str]]
    size: int
    words: List[WordPlacement]

class GameRequest(BaseModel):
    level: int
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

def generate_board(size: int, words: List[dict], language: str) -> GameBoard:
    directions = [(0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)]
    word_placements = []
    
    placed = False
    attempts = 0
    max_attempts = 50
    
    while not placed and attempts < max_attempts:
        attempts += 1
        matrix = [['' for _ in range(size)] for _ in range(size)]
        placed = True
        word_placements = []
        
        for word_data in words:
            word = word_data[language]
            info = word_data.get(f"info{language}", "")
            word_placed = False
            
            for _ in range(150):
                direction = random.choice(directions)
                row = random.randint(0, size - 1)
                col = random.randint(0, size - 1)
                
                if can_place_word(matrix, word, row, col, direction, size):
                    coords = place_word(matrix, word, row, col, direction)
                    word_placements.append(WordPlacement(word=word, info=info, coords=coords))
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
    
    return GameBoard(matrix=matrix, size=size, words=word_placements)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "AbdoulGame API - Polyglot Word Search"}

@api_router.get("/knowledge")
async def get_knowledge():
    return KNOWLEDGE_DB

@api_router.post("/game/generate", response_model=GameBoard)
async def generate_game(request: GameRequest):
    level = max(1, min(request.level, 10))
    language = request.language.upper() if request.language.upper() in ["ES", "EN", "FR"] else "ES"
    
    # Board size increases with level
    size = min(8 + level, 12)
    
    # Number of words increases with level
    num_words = min(3 + level, len(KNOWLEDGE_DB))
    
    # Randomly select words for this game
    selected_words = random.sample(KNOWLEDGE_DB, num_words)
    
    return generate_board(size, selected_words, language)

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
async def get_player_scores(player_name: str):
    scores = await db.scores.find({"player_name": player_name}, {"_id": 0}).sort("score", -1).to_list(100)
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
