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
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, date
import re
import hashlib

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

# Inspirational quotes by category
INSPIRATIONAL_QUOTES = {
    "philosophy": {
        "ES": [
            "Como dijo Sócrates: Solo sé que no sé nada",
            "La duda es el principio de la sabiduría - Aristóteles",
            "Pienso, luego existo - René Descartes",
            "El que no conoce su historia está condenado a repetirla",
            "La verdad es hija del tiempo, no de la autoridad"
        ],
        "EN": [
            "As Socrates said: I know that I know nothing",
            "Doubt is the beginning of wisdom - Aristotle",
            "I think, therefore I am - René Descartes",
            "Those who don't know history are doomed to repeat it",
            "Truth is the daughter of time, not of authority"
        ],
        "FR": [
            "Comme disait Socrate: Je sais que je ne sais rien",
            "Le doute est le début de la sagesse - Aristote",
            "Je pense, donc je suis - René Descartes",
            "Celui qui ne connaît pas son histoire est condamné à la répéter",
            "La vérité est fille du temps, non de l'autorité"
        ]
    },
    "values": {
        "ES": [
            "La integridad es hacer lo correcto, incluso cuando nadie mira",
            "Tus valores definen quién eres realmente",
            "El carácter es como un árbol y la reputación su sombra",
            "Sé el cambio que quieres ver en el mundo - Gandhi",
            "La honestidad es el primer capítulo del libro de la sabiduría"
        ],
        "EN": [
            "Integrity is doing the right thing, even when no one is watching",
            "Your values define who you really are",
            "Character is like a tree and reputation its shadow",
            "Be the change you wish to see in the world - Gandhi",
            "Honesty is the first chapter in the book of wisdom"
        ],
        "FR": [
            "L'intégrité c'est faire ce qui est juste, même quand personne ne regarde",
            "Vos valeurs définissent qui vous êtes vraiment",
            "Le caractère est comme un arbre et la réputation son ombre",
            "Soyez le changement que vous voulez voir dans le monde - Gandhi",
            "L'honnêteté est le premier chapitre du livre de la sagesse"
        ]
    },
    "emotions": {
        "ES": [
            "Las emociones no son buenas ni malas, simplemente son",
            "El amor todo lo puede, todo lo cree, todo lo espera",
            "La alegría compartida se multiplica, el dolor compartido se divide",
            "La paz interior comienza cuando decides no permitir que otros controlen tus emociones",
            "La esperanza es el sueño del hombre despierto - Aristóteles"
        ],
        "EN": [
            "Emotions are neither good nor bad, they simply are",
            "Love can do all things, believe all things, hope all things",
            "Shared joy is multiplied, shared pain is divided",
            "Inner peace begins when you decide not to let others control your emotions",
            "Hope is the dream of a man awake - Aristotle"
        ],
        "FR": [
            "Les émotions ne sont ni bonnes ni mauvaises, elles sont simplement",
            "L'amour peut tout, croit tout, espère tout",
            "La joie partagée se multiplie, la douleur partagée se divise",
            "La paix intérieure commence quand vous décidez de ne pas laisser les autres contrôler vos émotions",
            "L'espoir est le rêve d'un homme éveillé - Aristote"
        ]
    },
    "success": {
        "ES": [
            "El éxito es la suma de pequeños esfuerzos repetidos día tras día",
            "No cuentes los días, haz que los días cuenten - Muhammad Ali",
            "El fracaso es solo la oportunidad de comenzar de nuevo con más inteligencia",
            "La disciplina es el puente entre metas y logros",
            "Los sueños no funcionan a menos que tú lo hagas"
        ],
        "EN": [
            "Success is the sum of small efforts repeated day after day",
            "Don't count the days, make the days count - Muhammad Ali",
            "Failure is only the opportunity to begin again more intelligently",
            "Discipline is the bridge between goals and accomplishments",
            "Dreams don't work unless you do"
        ],
        "FR": [
            "Le succès est la somme de petits efforts répétés jour après jour",
            "Ne comptez pas les jours, faites que les jours comptent - Muhammad Ali",
            "L'échec n'est que l'opportunité de recommencer plus intelligemment",
            "La discipline est le pont entre les objectifs et les accomplissements",
            "Les rêves ne fonctionnent pas à moins que vous ne le fassiez"
        ]
    },
    "strength": {
        "ES": [
            "Lo que no te mata te hace más fuerte - Nietzsche",
            "La verdadera fuerza está en levantarse cada vez que caes",
            "El coraje no es la ausencia de miedo, sino el triunfo sobre él",
            "Las dificultades preparan a personas comunes para destinos extraordinarios",
            "La resiliencia es aceptar tu nueva realidad, incluso si es menos buena que la anterior"
        ],
        "EN": [
            "What doesn't kill you makes you stronger - Nietzsche",
            "True strength is rising every time you fall",
            "Courage is not the absence of fear, but the triumph over it",
            "Difficulties prepare ordinary people for extraordinary destinies",
            "Resilience is accepting your new reality, even if it's less good than before"
        ],
        "FR": [
            "Ce qui ne te tue pas te rend plus fort - Nietzsche",
            "La vraie force est de se relever chaque fois que tu tombes",
            "Le courage n'est pas l'absence de peur, mais le triomphe sur elle",
            "Les difficultés préparent des gens ordinaires pour des destins extraordinaires",
            "La résilience c'est accepter votre nouvelle réalité, même si elle est moins bonne qu'avant"
        ]
    },
    "relationships": {
        "ES": [
            "La familia no es algo importante, lo es todo - Michael J. Fox",
            "Un amigo verdadero es quien te toma de la mano y te toca el corazón",
            "Solos podemos hacer tan poco, juntos podemos hacer tanto - Helen Keller",
            "Las relaciones son como el vidrio, a veces es mejor dejarlas rotas que lastimarse tratando de repararlas",
            "La mejor forma de encontrar un amigo es ser uno"
        ],
        "EN": [
            "Family is not something important, it's everything - Michael J. Fox",
            "A true friend is someone who takes your hand and touches your heart",
            "Alone we can do so little, together we can do so much - Helen Keller",
            "Relationships are like glass, sometimes it's better to leave them broken than hurt yourself trying to fix them",
            "The best way to find a friend is to be one"
        ],
        "FR": [
            "La famille n'est pas quelque chose d'important, c'est tout - Michael J. Fox",
            "Un vrai ami est quelqu'un qui prend votre main et touche votre cœur",
            "Seuls nous pouvons faire si peu, ensemble nous pouvons faire tant - Helen Keller",
            "Les relations sont comme le verre, parfois il vaut mieux les laisser cassées que se blesser en essayant de les réparer",
            "La meilleure façon de trouver un ami est d'en être un"
        ]
    },
    "learning": {
        "ES": [
            "La educación es el arma más poderosa para cambiar el mundo - Nelson Mandela",
            "Dime y lo olvido, enséñame y lo recuerdo, involúcrame y lo aprendo",
            "La curiosidad es la mecha en la vela del aprendizaje",
            "Nunca es tarde para ser lo que podrías haber sido - George Eliot",
            "Aprender es un tesoro que seguirá a su dueño a todas partes"
        ],
        "EN": [
            "Education is the most powerful weapon to change the world - Nelson Mandela",
            "Tell me and I forget, teach me and I remember, involve me and I learn",
            "Curiosity is the wick in the candle of learning",
            "It's never too late to be what you might have been - George Eliot",
            "Learning is a treasure that will follow its owner everywhere"
        ],
        "FR": [
            "L'éducation est l'arme la plus puissante pour changer le monde - Nelson Mandela",
            "Dis-moi et j'oublie, enseigne-moi et je me souviens, implique-moi et j'apprends",
            "La curiosité est la mèche dans la bougie de l'apprentissage",
            "Il n'est jamais trop tard pour être ce que vous auriez pu être - George Eliot",
            "L'apprentissage est un trésor qui suivra son propriétaire partout"
        ]
    },
    "health": {
        "ES": [
            "La salud es riqueza real, no piezas de oro y plata - Gandhi",
            "Cuida tu cuerpo, es el único lugar que tienes para vivir",
            "Un cuerpo sano es una habitación para el alma, un cuerpo enfermo es una prisión",
            "La mejor medicina es un ánimo alegre",
            "El equilibrio es la clave de todo bienestar"
        ],
        "EN": [
            "Health is real wealth, not pieces of gold and silver - Gandhi",
            "Take care of your body, it's the only place you have to live",
            "A healthy body is a room for the soul, a sick body is a prison",
            "The best medicine is a cheerful spirit",
            "Balance is the key to all wellbeing"
        ],
        "FR": [
            "La santé est la vraie richesse, pas les pièces d'or et d'argent - Gandhi",
            "Prenez soin de votre corps, c'est le seul endroit où vous devez vivre",
            "Un corps sain est une chambre pour l'âme, un corps malade est une prison",
            "Le meilleur médicament est un esprit joyeux",
            "L'équilibre est la clé de tout bien-être"
        ]
    },
    "nature": {
        "ES": [
            "En cada paseo por la naturaleza, uno recibe mucho más de lo que busca",
            "La naturaleza no hace nada incompleto ni nada en vano - Aristóteles",
            "Mira profundamente en la naturaleza y entenderás todo mejor - Einstein",
            "El tiempo es la moneda de tu vida, gástala sabiamente",
            "La vida es lo que pasa mientras estás ocupado haciendo otros planes"
        ],
        "EN": [
            "In every walk with nature, one receives far more than he seeks",
            "Nature does nothing incomplete and nothing in vain - Aristotle",
            "Look deep into nature and you will understand everything better - Einstein",
            "Time is the coin of your life, spend it wisely",
            "Life is what happens while you're busy making other plans"
        ],
        "FR": [
            "Dans chaque promenade avec la nature, on reçoit bien plus qu'on ne cherche",
            "La nature ne fait rien d'incomplet et rien en vain - Aristote",
            "Regardez profondément dans la nature et vous comprendrez tout mieux - Einstein",
            "Le temps est la monnaie de votre vie, dépensez-le sagement",
            "La vie est ce qui arrive pendant que vous êtes occupé à faire d'autres plans"
        ]
    },
    "spirituality": {
        "ES": [
            "La gratitud convierte lo que tenemos en suficiente",
            "La fe es dar el primer paso incluso cuando no ves toda la escalera - MLK",
            "El alma que puede hablar con los ojos, también puede besar con la mirada",
            "La espiritualidad es reconocer la luz que está en uno mismo",
            "No busques, encuentra - Picasso"
        ],
        "EN": [
            "Gratitude turns what we have into enough",
            "Faith is taking the first step even when you don't see the whole staircase - MLK",
            "The soul that can speak with the eyes can also kiss with the gaze",
            "Spirituality is recognizing the light that is within oneself",
            "Don't seek, find - Picasso"
        ],
        "FR": [
            "La gratitude transforme ce que nous avons en suffisant",
            "La foi c'est faire le premier pas même quand vous ne voyez pas tout l'escalier - MLK",
            "L'âme qui peut parler avec les yeux peut aussi embrasser avec le regard",
            "La spiritualité c'est reconnaître la lumière qui est en soi",
            "Ne cherchez pas, trouvez - Picasso"
        ]
    },
    "creativity": {
        "ES": [
            "La creatividad es la inteligencia divirtiéndose - Einstein",
            "El arte lava del alma el polvo de la vida cotidiana - Picasso",
            "Todo niño es un artista, el problema es seguir siendo artista al crecer",
            "La belleza perece en la vida, pero es inmortal en el arte",
            "La imaginación es más importante que el conocimiento - Einstein"
        ],
        "EN": [
            "Creativity is intelligence having fun - Einstein",
            "Art washes from the soul the dust of everyday life - Picasso",
            "Every child is an artist, the problem is staying an artist when you grow up",
            "Beauty perishes in life, but is immortal in art",
            "Imagination is more important than knowledge - Einstein"
        ],
        "FR": [
            "La créativité c'est l'intelligence qui s'amuse - Einstein",
            "L'art lave de l'âme la poussière de la vie quotidienne - Picasso",
            "Chaque enfant est un artiste, le problème est de rester artiste en grandissant",
            "La beauté périt dans la vie, mais est immortelle dans l'art",
            "L'imagination est plus importante que la connaissance - Einstein"
        ]
    },
    "justice": {
        "ES": [
            "La injusticia en cualquier lugar es una amenaza a la justicia en todas partes - MLK",
            "La libertad no es hacer lo que quieras, sino querer lo que haces",
            "Todos los hombres nacen iguales, pero es la última vez que lo son",
            "La justicia retardada es justicia denegada",
            "No hay camino para la paz, la paz es el camino - Gandhi"
        ],
        "EN": [
            "Injustice anywhere is a threat to justice everywhere - MLK",
            "Freedom is not doing what you want, but wanting what you do",
            "All men are born equal, but it's the last time they are",
            "Justice delayed is justice denied",
            "There is no path to peace, peace is the path - Gandhi"
        ],
        "FR": [
            "L'injustice n'importe où est une menace pour la justice partout - MLK",
            "La liberté n'est pas faire ce que vous voulez, mais vouloir ce que vous faites",
            "Tous les hommes naissent égaux, mais c'est la dernière fois qu'ils le sont",
            "La justice retardée est la justice refusée",
            "Il n'y a pas de chemin vers la paix, la paix est le chemin - Gandhi"
        ]
    }
}

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

# Achievements definitions
ACHIEVEMENTS = [
    {
        "id": "philosopher",
        "icon": "🧠",
        "nameES": "Filósofo",
        "nameEN": "Philosopher",
        "nameFR": "Philosophe",
        "descES": "Encuentra 10 palabras de Filosofía",
        "descEN": "Find 10 Philosophy words",
        "descFR": "Trouvez 10 mots de Philosophie",
        "requirement": {"type": "category_words", "category": "philosophy", "count": 10}
    },
    {
        "id": "time_master",
        "icon": "⏱️",
        "nameES": "Maestro del Tiempo",
        "nameEN": "Time Master",
        "nameFR": "Maître du Temps",
        "descES": "Completa un nivel con más de 2 minutos restantes",
        "descEN": "Complete a level with more than 2 minutes remaining",
        "descFR": "Complétez un niveau avec plus de 2 minutes restantes",
        "requirement": {"type": "time_remaining", "seconds": 120}
    },
    {
        "id": "polyglot",
        "icon": "🌍",
        "nameES": "Políglota",
        "nameEN": "Polyglot",
        "nameFR": "Polyglotte",
        "descES": "Juega en los 3 idiomas (ES/EN/FR)",
        "descEN": "Play in all 3 languages (ES/EN/FR)",
        "descFR": "Jouez dans les 3 langues (ES/EN/FR)",
        "requirement": {"type": "languages_played", "count": 3}
    },
    {
        "id": "perfectionist",
        "icon": "💯",
        "nameES": "Perfeccionista",
        "nameEN": "Perfectionist",
        "nameFR": "Perfectionniste",
        "descES": "Completa un nivel sin usar pistas",
        "descEN": "Complete a level without using hints",
        "descFR": "Complétez un niveau sans utiliser d'indices",
        "requirement": {"type": "no_hints", "count": 1}
    },
    {
        "id": "wisdom_seeker",
        "icon": "✨",
        "nameES": "Buscador de Sabiduría",
        "nameEN": "Wisdom Seeker",
        "nameFR": "Chercheur de Sagesse",
        "descES": "Encuentra 50 palabras en total",
        "descEN": "Find 50 words in total",
        "descFR": "Trouvez 50 mots au total",
        "requirement": {"type": "total_words", "count": 50}
    },
    {
        "id": "speed_demon",
        "icon": "⚡",
        "nameES": "Demonio de la Velocidad",
        "nameEN": "Speed Demon",
        "nameFR": "Démon de Vitesse",
        "descES": "Encuentra una palabra en menos de 5 segundos",
        "descEN": "Find a word in less than 5 seconds",
        "descFR": "Trouvez un mot en moins de 5 secondes",
        "requirement": {"type": "word_speed", "seconds": 5}
    },
    {
        "id": "champion",
        "icon": "🏆",
        "nameES": "Campeón",
        "nameEN": "Champion",
        "nameFR": "Champion",
        "descES": "Completa el nivel 10",
        "descEN": "Complete level 10",
        "descFR": "Complétez le niveau 10",
        "requirement": {"type": "level_completed", "level": 10}
    },
    {
        "id": "combo_master",
        "icon": "🔥",
        "nameES": "Maestro del Combo",
        "nameEN": "Combo Master",
        "nameFR": "Maître du Combo",
        "descES": "Encuentra 5 palabras seguidas sin errores",
        "descEN": "Find 5 words in a row without errors",
        "descFR": "Trouvez 5 mots d'affilée sans erreurs",
        "requirement": {"type": "combo_streak", "count": 5}
    },
    {
        "id": "heart_explorer",
        "icon": "❤️",
        "nameES": "Explorador del Corazón",
        "nameEN": "Heart Explorer",
        "nameFR": "Explorateur du Cœur",
        "descES": "Encuentra 10 palabras de Emociones",
        "descEN": "Find 10 Emotions words",
        "descFR": "Trouvez 10 mots d'Émotions",
        "requirement": {"type": "category_words", "category": "emotions", "count": 10}
    },
    {
        "id": "all_rounder",
        "icon": "🌟",
        "nameES": "Todoterreno",
        "nameEN": "All-Rounder",
        "nameFR": "Touche-à-tout",
        "descES": "Encuentra palabras de todas las 12 categorías",
        "descEN": "Find words from all 12 categories",
        "descFR": "Trouvez des mots de toutes les 12 catégories",
        "requirement": {"type": "all_categories", "count": 12}
    }
]

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
    """
    Improved word placement algorithm with length filtering
    - Filters words by appropriate length for grid size
    - Increased placement attempts for better success rate
    - Prioritizes shorter words for smaller grids
    """
    directions = [(0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)]
    word_placements = []
    config = get_level_config(level)
    
    # Filter words by length based on grid size
    max_word_length = max(4, size - 2)  # At least 4 letters, max grid_size - 2
    filtered_words = []
    
    for word_data in words:
        word_text = word_data[language]
        word_len = len(word_text)
        # Accept words that fit well in the grid
        if 3 <= word_len <= max_word_length:
            filtered_words.append(word_data)
    
    # If filtering removed too many words, use original list
    if len(filtered_words) < len(words) * 0.5:
        filtered_words = words
    
    # Sort by length to place shorter words first (easier to place)
    filtered_words.sort(key=lambda w: len(w[language]))
    
    placed = False
    attempts = 0
    max_attempts = 150  # Increased from 100
    
    while not placed and attempts < max_attempts:
        attempts += 1
        matrix = [['' for _ in range(size)] for _ in range(size)]
        placed = True
        word_placements = []
        
        for word_data in filtered_words:
            word = word_data[language]
            info = word_data.get(f"info{language}", "")
            category = word_data.get("category", "general")
            categoryName = word_data.get(f"category{language}", category)
            word_placed = False
            
            # Increased attempts per word from 200 to 500
            for _ in range(500):
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
    
    # Fill empty cells with random letters
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

# NEW ENDPOINTS - Achievements & Daily Challenge
@api_router.get("/achievements")
async def get_achievements(language: str = "ES"):
    """Get all available achievements"""
    lang = language.upper() if language.upper() in ["ES", "EN", "FR"] else "ES"
    achievements_localized = []
    
    for achievement in ACHIEVEMENTS:
        achievements_localized.append({
            "id": achievement["id"],
            "icon": achievement["icon"],
            "name": achievement[f"name{lang}"],
            "description": achievement[f"desc{lang}"],
            "requirement": achievement["requirement"]
        })
    
    return achievements_localized

@api_router.get("/inspirational-quote")
async def get_inspirational_quote(category: str, language: str = "ES"):
    """Get a random inspirational quote for a category"""
    lang = language.upper() if language.upper() in ["ES", "EN", "FR"] else "ES"
    
    if category in INSPIRATIONAL_QUOTES:
        quotes = INSPIRATIONAL_QUOTES[category][lang]
        return {"quote": random.choice(quotes), "category": category}
    
    # Fallback
    return {"quote": "¡Sigue aprendiendo!", "category": category}

@api_router.get("/daily-challenge")
async def get_daily_challenge(language: str = "ES"):
    """
    Generate daily challenge - same board for everyone each day
    Uses date as seed for reproducible randomization
    """
    lang = language.upper() if language.upper() in ["ES", "EN", "FR"] else "ES"
    
    # Get today's date as seed
    today = date.today()
    seed_string = f"{today.isoformat()}"
    seed_value = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (10 ** 8)
    
    # Set random seed for reproducible generation
    random.seed(seed_value)
    
    # Daily challenge is always level 5 (medium difficulty)
    level = 5
    config = get_level_config(level)
    size = config["size"]
    num_words = config["words"]
    
    # Select words based on seeded random
    selected_words = random.sample(KNOWLEDGE_DB, min(num_words, len(KNOWLEDGE_DB)))
    
    # Generate board with seeded random
    board = generate_board(size, selected_words, lang, level)
    
    # Reset random seed
    random.seed()
    
    return {
        "date": today.isoformat(),
        "level": level,
        "board": board,
        "message": {
            "ES": "¡Desafío del día! Todos juegan el mismo tablero hoy.",
            "EN": "Daily Challenge! Everyone plays the same board today.",
            "FR": "Défi du jour! Tout le monde joue le même plateau aujourd'hui."
        }[lang]
    }

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
