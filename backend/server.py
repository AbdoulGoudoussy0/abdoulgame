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
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Input sanitization helper
def sanitize_input(text: str, max_length: int = 100) -> str:
    if not text:
        return ""
    sanitized = re.sub(r'[<>"\';\\]', '', text)
    return sanitized[:max_length].strip()

# =============================================================================
# EXPANDED KNOWLEDGE DATABASE - Educational words covering all aspects of life
# =============================================================================
KNOWLEDGE_DB = [
    # === PHILOSOPHY & WISDOM ===
    {"id": "wisdom", "ES": "SABIDURIA", "EN": "WISDOM", "FR": "SAGESSE", 
     "infoES": "La sabiduría es saber aplicar el conocimiento con prudencia.", 
     "infoEN": "Wisdom is knowing how to apply knowledge with prudence.", 
     "infoFR": "La sagesse est savoir appliquer la connaissance avec prudence.",
     "category": "philosophy", "categoryES": "Filosofía", "categoryEN": "Philosophy", "categoryFR": "Philosophie"},
    
    {"id": "truth", "ES": "VERDAD", "EN": "TRUTH", "FR": "VERITE", 
     "infoES": "La verdad es el fundamento de toda relación auténtica.", 
     "infoEN": "Truth is the foundation of every authentic relationship.", 
     "infoFR": "La vérité est le fondement de toute relation authentique.",
     "category": "philosophy", "categoryES": "Filosofía", "categoryEN": "Philosophy", "categoryFR": "Philosophie"},
    
    {"id": "logic", "ES": "LOGICA", "EN": "LOGIC", "FR": "LOGIQUE", 
     "infoES": "La lógica ordena nuestros pensamientos hacia conclusiones válidas.", 
     "infoEN": "Logic organizes our thoughts toward valid conclusions.", 
     "infoFR": "La logique organise nos pensées vers des conclusions valides.",
     "category": "philosophy", "categoryES": "Filosofía", "categoryEN": "Philosophy", "categoryFR": "Philosophie"},

    # === VALUES & ETHICS ===
    {"id": "honor", "ES": "HONOR", "EN": "HONOR", "FR": "HONNEUR", 
     "infoES": "El honor es mantener tu palabra y actuar con integridad.", 
     "infoEN": "Honor is keeping your word and acting with integrity.", 
     "infoFR": "L'honneur est tenir sa parole et agir avec intégrité.",
     "category": "values", "categoryES": "Valores", "categoryEN": "Values", "categoryFR": "Valeurs"},
    
    {"id": "ethics", "ES": "ETICA", "EN": "ETHICS", "FR": "ETHIQUE", 
     "infoES": "La ética guía nuestras decisiones hacia el bien común.", 
     "infoEN": "Ethics guides our decisions toward the common good.", 
     "infoFR": "L'éthique guide nos décisions vers le bien commun.",
     "category": "values", "categoryES": "Valores", "categoryEN": "Values", "categoryFR": "Valeurs"},
    
    {"id": "virtue", "ES": "VIRTUD", "EN": "VIRTUE", "FR": "VERTU", 
     "infoES": "La virtud es la práctica constante de hacer el bien.", 
     "infoEN": "Virtue is the constant practice of doing good.", 
     "infoFR": "La vertu est la pratique constante de faire le bien.",
     "category": "values", "categoryES": "Valores", "categoryEN": "Values", "categoryFR": "Valeurs"},
    
    {"id": "respect", "ES": "RESPETO", "EN": "RESPECT", "FR": "RESPECT", 
     "infoES": "El respeto reconoce la dignidad inherente de cada persona.", 
     "infoEN": "Respect recognizes the inherent dignity of every person.", 
     "infoFR": "Le respect reconnaît la dignité inhérente de chaque personne.",
     "category": "values", "categoryES": "Valores", "categoryEN": "Values", "categoryFR": "Valeurs"},

    # === EMOTIONS & FEELINGS ===
    {"id": "love", "ES": "AMOR", "EN": "LOVE", "FR": "AMOUR", 
     "infoES": "El amor es la fuerza que conecta todos los corazones.", 
     "infoEN": "Love is the force that connects all hearts.", 
     "infoFR": "L'amour est la force qui connecte tous les cœurs.",
     "category": "emotions", "categoryES": "Emociones", "categoryEN": "Emotions", "categoryFR": "Émotions"},
    
    {"id": "joy", "ES": "ALEGRIA", "EN": "JOY", "FR": "JOIE", 
     "infoES": "La alegría es el estado natural del alma en paz.", 
     "infoEN": "Joy is the natural state of a soul at peace.", 
     "infoFR": "La joie est l'état naturel d'une âme en paix.",
     "category": "emotions", "categoryES": "Emociones", "categoryEN": "Emotions", "categoryFR": "Émotions"},
    
    {"id": "peace", "ES": "PAZ", "EN": "PEACE", "FR": "PAIX", 
     "infoES": "La paz interior es el refugio donde renace la claridad.", 
     "infoEN": "Inner peace is the refuge where clarity is reborn.", 
     "infoFR": "La paix intérieure est le refuge où renaît la clarté.",
     "category": "emotions", "categoryES": "Emociones", "categoryEN": "Emotions", "categoryFR": "Émotions"},
    
    {"id": "hope", "ES": "ESPERANZA", "EN": "HOPE", "FR": "ESPOIR", 
     "infoES": "La esperanza es la luz que brilla en los momentos oscuros.", 
     "infoEN": "Hope is the light that shines in dark moments.", 
     "infoFR": "L'espoir est la lumière qui brille dans les moments sombres.",
     "category": "emotions", "categoryES": "Emociones", "categoryEN": "Emotions", "categoryFR": "Émotions"},

    # === SUCCESS & GOALS ===
    {"id": "success", "ES": "EXITO", "EN": "SUCCESS", "FR": "SUCCES", 
     "infoES": "El éxito es la suma de pequeños esfuerzos repetidos cada día.", 
     "infoEN": "Success is the sum of small efforts repeated every day.", 
     "infoFR": "Le succès est la somme de petits efforts répétés chaque jour.",
     "category": "success", "categoryES": "Éxito", "categoryEN": "Success", "categoryFR": "Succès"},
    
    {"id": "goal", "ES": "META", "EN": "GOAL", "FR": "BUT", 
     "infoES": "Una meta clara transforma los sueños en planes de acción.", 
     "infoEN": "A clear goal transforms dreams into action plans.", 
     "infoFR": "Un but clair transforme les rêves en plans d'action.",
     "category": "success", "categoryES": "Éxito", "categoryEN": "Success", "categoryFR": "Succès"},
    
    {"id": "effort", "ES": "ESFUERZO", "EN": "EFFORT", "FR": "EFFORT", 
     "infoES": "El esfuerzo constante supera al talento sin disciplina.", 
     "infoEN": "Constant effort overcomes talent without discipline.", 
     "infoFR": "L'effort constant surpasse le talent sans discipline.",
     "category": "success", "categoryES": "Éxito", "categoryEN": "Success", "categoryFR": "Succès"},
    
    {"id": "dream", "ES": "SUENO", "EN": "DREAM", "FR": "REVE", 
     "infoES": "Los sueños son el primer paso hacia la realidad.", 
     "infoEN": "Dreams are the first step toward reality.", 
     "infoFR": "Les rêves sont le premier pas vers la réalité.",
     "category": "success", "categoryES": "Éxito", "categoryEN": "Success", "categoryFR": "Succès"},

    # === COURAGE & STRENGTH ===
    {"id": "courage", "ES": "VALOR", "EN": "COURAGE", "FR": "COURAGE", 
     "infoES": "El valor no es ausencia de miedo, sino actuar a pesar de él.", 
     "infoEN": "Courage is not the absence of fear, but acting despite it.", 
     "infoFR": "Le courage n'est pas l'absence de peur, mais agir malgré elle.",
     "category": "strength", "categoryES": "Fortaleza", "categoryEN": "Strength", "categoryFR": "Force"},
    
    {"id": "strength", "ES": "FUERZA", "EN": "STRENGTH", "FR": "FORCE", 
     "infoES": "La verdadera fuerza está en levantarse después de caer.", 
     "infoEN": "True strength is in rising after falling.", 
     "infoFR": "La vraie force est de se relever après être tombé.",
     "category": "strength", "categoryES": "Fortaleza", "categoryEN": "Strength", "categoryFR": "Force"},
    
    {"id": "resilience", "ES": "RESILIENCIA", "EN": "RESILIENCE", "FR": "RESILIENCE", 
     "infoES": "La resiliencia transforma los obstáculos en oportunidades.", 
     "infoEN": "Resilience transforms obstacles into opportunities.", 
     "infoFR": "La résilience transforme les obstacles en opportunités.",
     "category": "strength", "categoryES": "Fortaleza", "categoryEN": "Strength", "categoryFR": "Force"},

    # === RELATIONSHIPS & FAMILY ===
    {"id": "family", "ES": "FAMILIA", "EN": "FAMILY", "FR": "FAMILLE", 
     "infoES": "La familia es el primer lugar donde aprendemos a amar.", 
     "infoEN": "Family is the first place where we learn to love.", 
     "infoFR": "La famille est le premier lieu où nous apprenons à aimer.",
     "category": "relationships", "categoryES": "Relaciones", "categoryEN": "Relationships", "categoryFR": "Relations"},
    
    {"id": "friendship", "ES": "AMISTAD", "EN": "FRIENDSHIP", "FR": "AMITIE", 
     "infoES": "La amistad verdadera multiplica las alegrías y divide las penas.", 
     "infoEN": "True friendship multiplies joys and divides sorrows.", 
     "infoFR": "L'amitié vraie multiplie les joies et divise les peines.",
     "category": "relationships", "categoryES": "Relaciones", "categoryEN": "Relationships", "categoryFR": "Relations"},
    
    {"id": "unity", "ES": "UNION", "EN": "UNITY", "FR": "UNITE", 
     "infoES": "La unión de muchos crea una fuerza imparable.", 
     "infoEN": "The unity of many creates an unstoppable force.", 
     "infoFR": "L'union de plusieurs crée une force inarrêtable.",
     "category": "relationships", "categoryES": "Relaciones", "categoryEN": "Relationships", "categoryFR": "Relations"},

    # === KNOWLEDGE & LEARNING ===
    {"id": "knowledge", "ES": "SABER", "EN": "KNOWLEDGE", "FR": "SAVOIR", 
     "infoES": "El saber es un tesoro que nadie puede arrebatarte.", 
     "infoEN": "Knowledge is a treasure that no one can take from you.", 
     "infoFR": "Le savoir est un trésor que personne ne peut vous enlever.",
     "category": "learning", "categoryES": "Aprendizaje", "categoryEN": "Learning", "categoryFR": "Apprentissage"},
    
    {"id": "curiosity", "ES": "CURIOSIDAD", "EN": "CURIOSITY", "FR": "CURIOSITE", 
     "infoES": "La curiosidad es la chispa que enciende el fuego del aprendizaje.", 
     "infoEN": "Curiosity is the spark that ignites the fire of learning.", 
     "infoFR": "La curiosité est l'étincelle qui allume le feu de l'apprentissage.",
     "category": "learning", "categoryES": "Aprendizaje", "categoryEN": "Learning", "categoryFR": "Apprentissage"},
    
    {"id": "education", "ES": "EDUCACION", "EN": "EDUCATION", "FR": "EDUCATION", 
     "infoES": "La educación es el arma más poderosa para cambiar el mundo.", 
     "infoEN": "Education is the most powerful weapon to change the world.", 
     "infoFR": "L'éducation est l'arme la plus puissante pour changer le monde.",
     "category": "learning", "categoryES": "Aprendizaje", "categoryEN": "Learning", "categoryFR": "Apprentissage"},

    # === HEALTH & WELLNESS ===
    {"id": "health", "ES": "SALUD", "EN": "HEALTH", "FR": "SANTE", 
     "infoES": "La salud es la riqueza más valiosa que podemos poseer.", 
     "infoEN": "Health is the most valuable wealth we can possess.", 
     "infoFR": "La santé est la richesse la plus précieuse que nous puissions posséder.",
     "category": "health", "categoryES": "Salud", "categoryEN": "Health", "categoryFR": "Santé"},
    
    {"id": "balance", "ES": "EQUILIBRIO", "EN": "BALANCE", "FR": "EQUILIBRE", 
     "infoES": "El equilibrio entre cuerpo, mente y espíritu es la clave del bienestar.", 
     "infoEN": "Balance between body, mind and spirit is the key to wellbeing.", 
     "infoFR": "L'équilibre entre corps, esprit et âme est la clé du bien-être.",
     "category": "health", "categoryES": "Salud", "categoryEN": "Health", "categoryFR": "Santé"},
    
    {"id": "calm", "ES": "CALMA", "EN": "CALM", "FR": "CALME", 
     "infoES": "La calma es el poder de mantener la claridad en la tormenta.", 
     "infoEN": "Calm is the power to maintain clarity in the storm.", 
     "infoFR": "Le calme est le pouvoir de maintenir la clarté dans la tempête.",
     "category": "health", "categoryES": "Salud", "categoryEN": "Health", "categoryFR": "Santé"},

    # === NATURE & ENVIRONMENT ===
    {"id": "nature", "ES": "NATURALEZA", "EN": "NATURE", "FR": "NATURE", 
     "infoES": "La naturaleza es nuestra maestra más antigua y sabia.", 
     "infoEN": "Nature is our oldest and wisest teacher.", 
     "infoFR": "La nature est notre professeur le plus ancien et le plus sage.",
     "category": "nature", "categoryES": "Naturaleza", "categoryEN": "Nature", "categoryFR": "Nature"},
    
    {"id": "life", "ES": "VIDA", "EN": "LIFE", "FR": "VIE", 
     "infoES": "La vida es un regalo precioso que merece ser vivido plenamente.", 
     "infoEN": "Life is a precious gift that deserves to be fully lived.", 
     "infoFR": "La vie est un cadeau précieux qui mérite d'être pleinement vécu.",
     "category": "nature", "categoryES": "Naturaleza", "categoryEN": "Nature", "categoryFR": "Nature"},
    
    {"id": "time", "ES": "TIEMPO", "EN": "TIME", "FR": "TEMPS", 
     "infoES": "El tiempo es el recurso más valioso; úsalo con sabiduría.", 
     "infoEN": "Time is the most valuable resource; use it wisely.", 
     "infoFR": "Le temps est la ressource la plus précieuse; utilisez-le avec sagesse.",
     "category": "nature", "categoryES": "Naturaleza", "categoryEN": "Nature", "categoryFR": "Nature"},

    # === SPIRITUALITY & FAITH ===
    {"id": "faith", "ES": "FE", "EN": "FAITH", "FR": "FOI", 
     "infoES": "La fe es creer en lo que aún no vemos pero sentimos.", 
     "infoEN": "Faith is believing in what we don't yet see but feel.", 
     "infoFR": "La foi est croire en ce que nous ne voyons pas encore mais ressentons.",
     "category": "spirituality", "categoryES": "Espiritualidad", "categoryEN": "Spirituality", "categoryFR": "Spiritualité"},
    
    {"id": "soul", "ES": "ALMA", "EN": "SOUL", "FR": "AME", 
     "infoES": "El alma es la esencia eterna que habita en cada ser.", 
     "infoEN": "The soul is the eternal essence that dwells in every being.", 
     "infoFR": "L'âme est l'essence éternelle qui habite en chaque être.",
     "category": "spirituality", "categoryES": "Espiritualidad", "categoryEN": "Spirituality", "categoryFR": "Spiritualité"},
    
    {"id": "gratitude", "ES": "GRATITUD", "EN": "GRATITUDE", "FR": "GRATITUDE", 
     "infoES": "La gratitud transforma lo que tenemos en suficiente.", 
     "infoEN": "Gratitude transforms what we have into enough.", 
     "infoFR": "La gratitude transforme ce que nous avons en suffisant.",
     "category": "spirituality", "categoryES": "Espiritualidad", "categoryEN": "Spirituality", "categoryFR": "Spiritualité"},

    # === CREATIVITY & ART ===
    {"id": "creativity", "ES": "CREATIVIDAD", "EN": "CREATIVITY", "FR": "CREATIVITE", 
     "infoES": "La creatividad es ver posibilidades donde otros ven límites.", 
     "infoEN": "Creativity is seeing possibilities where others see limits.", 
     "infoFR": "La créativité est voir des possibilités où d'autres voient des limites.",
     "category": "creativity", "categoryES": "Creatividad", "categoryEN": "Creativity", "categoryFR": "Créativité"},
    
    {"id": "art", "ES": "ARTE", "EN": "ART", "FR": "ART", 
     "infoES": "El arte es el lenguaje universal del alma humana.", 
     "infoEN": "Art is the universal language of the human soul.", 
     "infoFR": "L'art est le langage universel de l'âme humaine.",
     "category": "creativity", "categoryES": "Creatividad", "categoryEN": "Creativity", "categoryFR": "Créativité"},
    
    {"id": "beauty", "ES": "BELLEZA", "EN": "BEAUTY", "FR": "BEAUTE", 
     "infoES": "La belleza está en los ojos de quien sabe mirar con el corazón.", 
     "infoEN": "Beauty is in the eyes of those who know how to look with their heart.", 
     "infoFR": "La beauté est dans les yeux de ceux qui savent regarder avec leur cœur.",
     "category": "creativity", "categoryES": "Creatividad", "categoryEN": "Creativity", "categoryFR": "Créativité"},

    # === FREEDOM & JUSTICE ===
    {"id": "freedom", "ES": "LIBERTAD", "EN": "FREEDOM", "FR": "LIBERTE", 
     "infoES": "La libertad es el derecho de elegir tu propio camino.", 
     "infoEN": "Freedom is the right to choose your own path.", 
     "infoFR": "La liberté est le droit de choisir votre propre chemin.",
     "category": "justice", "categoryES": "Justicia", "categoryEN": "Justice", "categoryFR": "Justice"},
    
    {"id": "justice", "ES": "JUSTICIA", "EN": "JUSTICE", "FR": "JUSTICE", 
     "infoES": "La justicia es dar a cada quien lo que le corresponde.", 
     "infoEN": "Justice is giving everyone what they deserve.", 
     "infoFR": "La justice est donner à chacun ce qui lui revient.",
     "category": "justice", "categoryES": "Justicia", "categoryEN": "Justice", "categoryFR": "Justice"},
    
    {"id": "equality", "ES": "IGUALDAD", "EN": "EQUALITY", "FR": "EGALITE", 
     "infoES": "La igualdad reconoce que todos merecemos las mismas oportunidades.", 
     "infoEN": "Equality recognizes that everyone deserves the same opportunities.", 
     "infoFR": "L'égalité reconnaît que tous méritent les mêmes opportunités.",
     "category": "justice", "categoryES": "Justicia", "categoryEN": "Justice", "categoryFR": "Justice"},
]

# Categories for filtering
CATEGORIES = [
    {"id": "philosophy", "ES": "Filosofía", "EN": "Philosophy", "FR": "Philosophie"},
    {"id": "values", "ES": "Valores", "EN": "Values", "FR": "Valeurs"},
    {"id": "emotions", "ES": "Emociones", "EN": "Emotions", "FR": "Émotions"},
    {"id": "success", "ES": "Éxito", "EN": "Success", "FR": "Succès"},
    {"id": "strength", "ES": "Fortaleza", "EN": "Strength", "FR": "Force"},
    {"id": "relationships", "ES": "Relaciones", "EN": "Relationships", "FR": "Relations"},
    {"id": "learning", "ES": "Aprendizaje", "EN": "Learning", "FR": "Apprentissage"},
    {"id": "health", "ES": "Salud", "EN": "Health", "FR": "Santé"},
    {"id": "nature", "ES": "Naturaleza", "EN": "Nature", "FR": "Nature"},
    {"id": "spirituality", "ES": "Espiritualidad", "EN": "Spirituality", "FR": "Spiritualité"},
    {"id": "creativity", "ES": "Creatividad", "EN": "Creativity", "FR": "Créativité"},
    {"id": "justice", "ES": "Justicia", "EN": "Justice", "FR": "Justice"},
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
    categoryName: str = ""

class GameBoard(BaseModel):
    matrix: List[List[str]]
    size: int
    words: List[WordPlacement]
    level: int
    time_limit: int

class GameRequest(BaseModel):
    level: int
    language: str
    category: Optional[str] = None

class AIHintRequest(BaseModel):
    word: str
    language: str
    found_letters: List[str] = []

class AIHintResponse(BaseModel):
    hint: str
    encouragement: str

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
    configs = {
        1: {"size": 8, "words": 3, "time": 180},
        2: {"size": 8, "words": 4, "time": 165},
        3: {"size": 9, "words": 4, "time": 150},
        4: {"size": 9, "words": 5, "time": 140},
        5: {"size": 10, "words": 5, "time": 130},
        6: {"size": 10, "words": 6, "time": 120},
        7: {"size": 11, "words": 6, "time": 115},
        8: {"size": 11, "words": 7, "time": 110},
        9: {"size": 12, "words": 7, "time": 105},
        10: {"size": 12, "words": 8, "time": 100},
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
            categoryName = word_data.get(f"category{language}", category)
            word_placed = False
            
            for _ in range(200):
                direction = random.choice(directions)
                row = random.randint(0, size - 1)
                col = random.randint(0, size - 1)
                
                if can_place_word(matrix, word, row, col, direction, size):
                    coords = place_word(matrix, word, row, col, direction)
                    word_placements.append(WordPlacement(
                        word=word, info=info, coords=coords, 
                        category=category, categoryName=categoryName
                    ))
                    word_placed = True
                    break
            
            if not word_placed:
                placed = False
                break
    
    for r in range(size):
        for c in range(size):
            if not matrix[r][c]:
                matrix[r][c] = chr(65 + random.randint(0, 25))
    
    return GameBoard(matrix=matrix, size=size, words=word_placements, level=level, time_limit=config["time"])

# API Routes
@api_router.get("/")
async def root():
    return {"message": "AbdoulGame API - Educational Word Search", "version": "3.0"}

@api_router.get("/knowledge")
async def get_knowledge():
    return KNOWLEDGE_DB

@api_router.get("/categories")
async def get_categories():
    return CATEGORIES

@api_router.post("/game/generate", response_model=GameBoard)
async def generate_game(request: GameRequest):
    level = max(1, min(request.level, 10))
    language = request.language.upper() if request.language.upper() in ["ES", "EN", "FR"] else "ES"
    
    config = get_level_config(level)
    size = config["size"]
    num_words = config["words"]
    
    # Filter by category if specified
    if request.category and request.category != "all":
        available_words = [w for w in KNOWLEDGE_DB if w.get("category") == request.category]
    else:
        available_words = KNOWLEDGE_DB
    
    # Ensure we have enough words
    if len(available_words) < num_words:
        available_words = KNOWLEDGE_DB
    
    selected_words = random.sample(available_words, min(num_words, len(available_words)))
    
    return generate_board(size, selected_words, language, level)

@api_router.post("/ai/hint", response_model=AIHintResponse)
async def get_ai_hint(request: AIHintRequest):
    hints = {
        "ES": [
            "Busca en las diagonales, ¡ahí se esconden!",
            "Intenta leer de derecha a izquierda también",
            "Las letras brillantes te guían al tesoro",
            "Mira bien las esquinas del tablero",
            "A veces las palabras van hacia arriba",
            "Busca patrones de letras consecutivas",
            "La palabra puede estar en cualquier dirección"
        ],
        "EN": [
            "Search the diagonals, they hide there!",
            "Try reading right to left as well",
            "The glowing letters guide you to treasure",
            "Look carefully at the board corners",
            "Sometimes words go upward",
            "Look for patterns of consecutive letters",
            "The word can be in any direction"
        ],
        "FR": [
            "Cherchez dans les diagonales!",
            "Essayez de lire de droite à gauche",
            "Les lettres brillantes vous guident",
            "Regardez bien les coins du plateau",
            "Parfois les mots vont vers le haut",
            "Cherchez des motifs de lettres consécutives",
            "Le mot peut être dans n'importe quelle direction"
        ]
    }
    
    encouragements = {
        "ES": ["¡Tú puedes!", "¡Sigue así!", "¡Casi lo tienes!", "¡Eres increíble!", "¡No te rindas!", "¡Confía en ti!"],
        "EN": ["You can do it!", "Keep going!", "Almost there!", "You're amazing!", "Don't give up!", "Trust yourself!"],
        "FR": ["Tu peux le faire!", "Continue!", "Tu y es presque!", "Tu es incroyable!", "N'abandonne pas!", "Fais-toi confiance!"]
    }
    
    lang = request.language if request.language in hints else "ES"
    return AIHintResponse(hint=random.choice(hints[lang]), encouragement=random.choice(encouragements[lang]))

@api_router.post("/ai/encouragement")
async def get_ai_encouragement(language: str = "ES", words_found: int = 0, total_words: int = 0):
    progress = (words_found / total_words * 100) if total_words > 0 else 0
    
    messages = {
        "ES": {
            "start": "¡Comienza tu aventura de aprendizaje!",
            "progress": f"¡Excelente! {words_found} de {total_words} palabras. ¡Cada palabra te hace más sabio!",
            "almost": "¡Ya casi terminas! ¡Un último esfuerzo!",
            "done": "¡INCREÍBLE! ¡Has completado el nivel!"
        },
        "EN": {
            "start": "Start your learning adventure!",
            "progress": f"Excellent! {words_found} of {total_words} words. Each word makes you wiser!",
            "almost": "Almost done! One last push!",
            "done": "AMAZING! You've completed the level!"
        },
        "FR": {
            "start": "Commencez votre aventure d'apprentissage!",
            "progress": f"Excellent! {words_found} sur {total_words} mots. Chaque mot vous rend plus sage!",
            "almost": "Presque fini! Un dernier effort!",
            "done": "INCROYABLE! Vous avez terminé le niveau!"
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
    word_data = next((w for w in KNOWLEDGE_DB if w.get(language) == word), None)
    
    if word_data:
        info_key = f"info{language}"
        category_key = f"category{language}"
        wisdom = word_data.get(info_key, f"¡Encontraste: {word}!")
        category = word_data.get(category_key, "")
        return {"wisdom": wisdom, "category": category}
    
    return {"wisdom": f"¡Has descubierto: {word}!", "category": ""}

@api_router.post("/share/generate")
async def generate_share_text(data: ShareData):
    lang_templates = {
        "ES": f"🎓 ¡Acabo de completar el Nivel {data.level} en AbdoulGame!\n⭐ Puntuación: {data.score}\n📚 Palabras aprendidas: {data.words_found}\n\n¡Aprende jugando! 🧠\n#AbdoulGame #Aprendizaje #Polyglot",
        "EN": f"🎓 Just completed Level {data.level} in AbdoulGame!\n⭐ Score: {data.score}\n📚 Words learned: {data.words_found}\n\nLearn by playing! 🧠\n#AbdoulGame #Learning #Polyglot",
        "FR": f"🎓 Je viens de terminer le Niveau {data.level} dans AbdoulGame!\n⭐ Score: {data.score}\n📚 Mots appris: {data.words_found}\n\nApprenez en jouant! 🧠\n#AbdoulGame #Apprentissage #Polyglot"
    }
    return {"text": lang_templates.get(data.language, lang_templates["ES"])}

@api_router.post("/scores", response_model=ScoreRecord)
async def save_score(input: ScoreCreate):
    sanitized_name = sanitize_input(input.player_name, 50)
    if not sanitized_name:
        sanitized_name = "Jugador"
    
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
    validated_limit = max(1, min(limit, 100))
    scores = await db.scores.find({}, {"_id": 0}).sort("score", -1).limit(validated_limit).to_list(validated_limit)
    for score in scores:
        if isinstance(score['timestamp'], str):
            score['timestamp'] = datetime.fromisoformat(score['timestamp'])
    return scores

@api_router.get("/scores/player/{player_name}", response_model=List[ScoreRecord])
async def get_player_scores(player_name: str, limit: int = 20, skip: int = 0):
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
