import React, { useState, useEffect, useCallback, useRef } from "react";
import "@/App.css";
import axios from "axios";
import { 
  Settings, X, Volume2, VolumeX, RotateCcw, Play, 
  Share2, ChevronUp, ChevronDown, Sparkles, Zap, Globe, Palette,
  Smartphone, HelpCircle, Hand, Target, Check, Sun, Moon, BookOpen,
  Heart, Brain, Users, Leaf, Star, Shield, TrendingUp, Award, Calendar,
  BarChart3, Download
} from "lucide-react";
import confetti from "canvas-confetti";
import {
  initializePlayerStats,
  getPlayerStats,
  updatePlayerStats,
  recordWord,
  recordGameCompletion,
  updateStreak,
  checkAchievements,
  exportStatsAsImage
} from "./utils/achievements";
import {
  createCategoryParticles,
  createWordRevealEffect,
  createComboEffect,
  createLevelUpEffect,
  createAchievementToast
} from "./utils/particles";
import {
  playCategorySound,
  playErrorSound,
  playComboSound,
  playLevelUpSound,
  playAchievementSound
} from "./utils/sounds";
import {
  generateSmartHint,
  generateVisualHint
} from "./utils/smartHints";
import {
  fireCategoryConfetti,
  flashScreen,
  wordRevealWave,
  showFloatingText,
  shakeElement
} from "./utils/visualFeedback";
import {
  SelectionHistory,
  predictWord,
  calculateScoreMultiplier,
  getMotivationalMessage,
  isFirstTimePlayer,
  markAsPlayed,
  PerformanceTracker
} from "./utils/gameHelpers";
import StatsModal from "./components/StatsModal";
import AchievementsModal from "./components/AchievementsModal";
import GameModeSelector from "./components/GameModeSelector";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sound effects
const createSoftSound = (frequency, duration, type = 'sine') => {
  return () => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      oscillator.frequency.value = frequency;
      oscillator.type = type;
      gainNode.gain.setValueAtTime(0.12, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + duration);
    } catch (e) {}
  };
};

const playClickSound = createSoftSound(700, 0.06, 'sine');
const playSelectSound = createSoftSound(500, 0.08, 'triangle');
const playCorrectSound = () => {
  [523, 659, 784].forEach((freq, i) => {
    setTimeout(() => createSoftSound(freq, 0.25, 'sine')(), i * 70);
  });
};
const playWinSound = () => {
  [523, 659, 784, 1047].forEach((freq, i) => {
    setTimeout(() => createSoftSound(freq, 0.35, 'sine')(), i * 100);
  });
};

// i18n with updated guide
const i18n = {
  ES: {
    title: "ABDOULGAME",
    subtitle: "APRENDE JUGANDO",
    settings: "AJUSTES",
    volume: "VOLUMEN",
    language: "IDIOMA", 
    theme: "COLORES",
    vibration: "VIBRACIÓN",
    darkMode: "MODO OSCURO",
    lightMode: "MODO CLARO",
    autoMode: "AUTOMÁTICO",
    save: "GUARDAR",
    enterStadium: "COMENZAR A JUGAR",
    welcome: "Descubre palabras que enriquecen tu vida",
    exit: "¿SALIR DEL JUEGO?",
    hint: "PISTA",
    clear: "BORRAR",
    next: "SIGUIENTE NIVEL",
    tap: "TOCA O DESLIZA",
    goal: "¡EXCELENTE!",
    levelComplete: "¡NIVEL COMPLETADO!",
    timeUp: "¡TIEMPO AGOTADO!",
    score: "PUNTOS",
    level: "NIVEL",
    wordsFound: "PALABRAS",
    playAgain: "REINTENTAR",
    yes: "SÍ",
    no: "NO",
    on: "SÍ",
    off: "NO",
    share: "COMPARTIR",
    copied: "¡COPIADO!",
    guide: "CÓMO JUGAR",
    guideTitle: "GUÍA DEL JUEGO",
    guideClose: "¡ENTENDIDO!",
    guideObjective: "OBJETIVO",
    guideObjectiveText: "Encuentra las palabras ocultas antes de que termine el tiempo. Cada palabra descubierta te enseña algo valioso sobre la vida, los valores, las emociones y más.",
    guideControls: "CONTROLES",
    guideControlsText: "TOCAR: Pulsa letra por letra. DESLIZAR: Arrastra el dedo sobre las letras. Las palabras van en horizontal, vertical, diagonal y en cualquier sentido.",
    guideFeatures: "FUNCIONES",
    guideFeaturesText: "💡 PISTA: Te ayuda a encontrar una palabra (-100 puntos). ⏱️ TIEMPO: Completa antes de que llegue a cero. ⭐ PUNTOS: +200 por cada palabra. 🔥 COMBOS: Palabras consecutivas multiplican tu puntuación.",
    guideModes: "MODOS DE JUEGO",
    guideModesText: "🎯 NORMAL: Juego clásico con niveles progresivos. 📚 PRÁCTICA: Enfócate en una categoría específica. 📅 DIARIO: Desafío del día para todos. 🧘 ZEN: Sin temporizador, solo aprendizaje.",
    guideProgress: "PROGRESIÓN",
    guideProgressText: "Gana XP por cada palabra encontrada. Sube de nivel y desbloquea logros. Consulta tus estadísticas para ver tu progreso en las 12 categorías educativas.",
    guideThemes: "PERSONALIZACIÓN",
    guideThemesText: "🌙/☀️ Modo oscuro o claro (automático o manual). 🎨 Tres temas de colores. 🌍 Tres idiomas disponibles.",
    guideLearning: "APRENDIZAJE",
    guideLearningText: "Las palabras cubren: Filosofía, Valores, Emociones, Éxito, Fortaleza, Relaciones, Aprendizaje, Salud, Naturaleza, Espiritualidad, Creatividad y Justicia. Cada palabra viene con frases inspiradoras de grandes pensadores.",
    guideAchievements: "LOGROS",
    guideAchievementsText: "Desbloquea 10 logros únicos: desde Filósofo hasta Campeón. Cada logro premia tu dedicación y habilidad.",
    guideShare: "COMPARTIR",
    guideShareText: "Comparte tus logros en redes sociales y reta a tus amigos a superar tu puntuación.",
    displayMode: "PANTALLA"
  },
  EN: {
    title: "ABDOULGAME",
    subtitle: "LEARN BY PLAYING",
    settings: "SETTINGS",
    volume: "VOLUME",
    language: "LANGUAGE",
    theme: "COLORS",
    vibration: "VIBRATION",
    darkMode: "DARK MODE",
    lightMode: "LIGHT MODE",
    autoMode: "AUTO",
    save: "SAVE",
    enterStadium: "START PLAYING",
    welcome: "Discover words that enrich your life",
    exit: "QUIT GAME?",
    hint: "HINT",
    clear: "CLEAR",
    next: "NEXT LEVEL",
    tap: "TAP OR SWIPE",
    goal: "EXCELLENT!",
    levelComplete: "LEVEL COMPLETE!",
    timeUp: "TIME'S UP!",
    score: "SCORE",
    level: "LEVEL",
    wordsFound: "WORDS",
    playAgain: "TRY AGAIN",
    yes: "YES",
    no: "NO",
    on: "YES",
    off: "NO",
    share: "SHARE",
    copied: "COPIED!",
    guide: "HOW TO PLAY",
    guideTitle: "GAME GUIDE",
    guideClose: "GOT IT!",
    guideObjective: "OBJECTIVE",
    guideObjectiveText: "Find the hidden words before time runs out. Each word teaches you something valuable about life, values, emotions, and more.",
    guideControls: "CONTROLS",
    guideControlsText: "TAP: Press letter by letter. SWIPE: Drag finger over letters. Words go horizontal, vertical, diagonal in any direction.",
    guideFeatures: "FEATURES",
    guideFeaturesText: "💡 HINT: Helps find a word (-100 points). ⏱️ TIME: Complete before it reaches zero. ⭐ POINTS: +200 per word. 🔥 COMBOS: Consecutive words multiply your score.",
    guideModes: "GAME MODES",
    guideModesText: "🎯 NORMAL: Classic game with progressive levels. 📚 PRACTICE: Focus on a specific category. 📅 DAILY: Challenge of the day for everyone. 🧘 ZEN: No timer, just learning.",
    guideProgress: "PROGRESSION",
    guideProgressText: "Earn XP for each word found. Level up and unlock achievements. Check your stats to see your progress across 12 educational categories.",
    guideThemes: "CUSTOMIZATION",
    guideThemesText: "🌙/☀️ Dark or light mode (auto or manual). 🎨 Three color themes. 🌍 Three languages available.",
    guideLearning: "LEARNING",
    guideLearningText: "Words cover: Philosophy, Values, Emotions, Success, Strength, Relationships, Learning, Health, Nature, Spirituality, Creativity, and Justice. Each word comes with inspirational quotes from great thinkers.",
    guideAchievements: "ACHIEVEMENTS",
    guideAchievementsText: "Unlock 10 unique achievements: from Philosopher to Champion. Each achievement rewards your dedication and skill.",
    guideShare: "SHARE",
    guideShareText: "Share your achievements on social media and challenge friends to beat your score.",
    displayMode: "DISPLAY"
  },
  FR: {
    title: "ABDOULGAME",
    subtitle: "APPRENDRE EN JOUANT",
    settings: "RÉGLAGES",
    volume: "VOLUME",
    language: "LANGUE",
    theme: "COULEURS",
    vibration: "VIBRATION",
    darkMode: "MODE SOMBRE",
    lightMode: "MODE CLAIR",
    autoMode: "AUTO",
    save: "ENREGISTRER",
    enterStadium: "COMMENCER À JOUER",
    welcome: "Découvrez des mots qui enrichissent votre vie",
    exit: "QUITTER LE JEU?",
    hint: "INDICE",
    clear: "EFFACER",
    next: "NIVEAU SUIVANT",
    tap: "TOUCHEZ OU GLISSEZ",
    goal: "EXCELLENT!",
    levelComplete: "NIVEAU TERMINÉ!",
    timeUp: "TEMPS ÉCOULÉ!",
    score: "POINTS",
    level: "NIVEAU",
    wordsFound: "MOTS",
    playAgain: "RÉESSAYER",
    yes: "OUI",
    no: "NON",
    on: "OUI",
    off: "NON",
    share: "PARTAGER",
    copied: "COPIÉ!",
    guide: "COMMENT JOUER",
    guideTitle: "GUIDE DU JEU",
    guideClose: "COMPRIS!",
    guideObjective: "OBJECTIF",
    guideObjectiveText: "Trouvez les mots cachés avant la fin du temps. Chaque mot vous enseigne quelque chose de précieux sur la vie, les valeurs, les émotions et plus.",
    guideControls: "CONTRÔLES",
    guideControlsText: "TOUCHER: Appuyez lettre par lettre. GLISSER: Faites glisser sur les lettres. Les mots vont horizontal, vertical, diagonal dans n'importe quelle direction.",
    guideFeatures: "FONCTIONNALITÉS",
    guideFeaturesText: "💡 INDICE: Aide à trouver un mot (-100 points). ⏱️ TEMPS: Terminez avant qu'il n'atteigne zéro. ⭐ POINTS: +200 par mot. 🔥 COMBOS: Les mots consécutifs multiplient votre score.",
    guideModes: "MODES DE JEU",
    guideModesText: "🎯 NORMAL: Jeu classique avec niveaux progressifs. 📚 PRATIQUE: Concentrez-vous sur une catégorie. 📅 QUOTIDIEN: Défi du jour pour tous. 🧘 ZEN: Pas de minuterie, juste apprentissage.",
    guideProgress: "PROGRESSION",
    guideProgressText: "Gagnez XP pour chaque mot trouvé. Montez de niveau et débloquez des succès. Consultez vos stats pour voir votre progrès dans 12 catégories éducatives.",
    guideThemes: "PERSONNALISATION",
    guideThemesText: "🌙/☀️ Mode sombre ou clair (auto ou manuel). 🎨 Trois thèmes de couleurs. 🌍 Trois langues disponibles.",
    guideLearning: "APPRENTISSAGE",
    guideLearningText: "Les mots couvrent: Philosophie, Valeurs, Émotions, Succès, Force, Relations, Apprentissage, Santé, Nature, Spiritualité, Créativité et Justice. Chaque mot vient avec citations inspirantes de grands penseurs.",
    guideAchievements: "SUCCÈS",
    guideAchievementsText: "Débloquez 10 succès uniques: de Philosophe à Champion. Chaque succès récompense votre dévouement et compétence.",
    guideShare: "PARTAGER",
    guideShareText: "Partagez vos exploits sur les réseaux sociaux et défiez vos amis de battre votre score.",
    displayMode: "AFFICHAGE"
  }
};

const languageFlags = { ES: "🇪🇸", EN: "🇺🇸", FR: "🇫🇷" };
const themes = ["neon", "classic", "gold"];
const themeNames = { neon: "Neón", classic: "Clásico", gold: "Dorado" };

function App() {
  // Game state
  const [gameState, setGameState] = useState("start");
  const [matrix, setMatrix] = useState([]);
  const [words, setWords] = useState([]);
  const [foundWords, setFoundWords] = useState([]);
  const [selection, setSelection] = useState([]);
  const [hintCells, setHintCells] = useState([]);
  const [score, setScore] = useState(0);
  const [level, setLevel] = useState(1);
  const [maxUnlockedLevel, setMaxUnlockedLevel] = useState(1);
  const [timeLeft, setTimeLeft] = useState(180);
  const [timeLimit, setTimeLimit] = useState(180);
  const [knowledgeText, setKnowledgeText] = useState("");
  const [currentCategory, setCurrentCategory] = useState("");

  // Settings
  const [showSettings, setShowSettings] = useState(false);
  const [showExit, setShowExit] = useState(false);
  const [showLevelSelect, setShowLevelSelect] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [lang, setLang] = useState("ES");
  const [theme, setTheme] = useState("neon");
  const [displayMode, setDisplayMode] = useState("auto"); // auto, dark, light
  const [volume, setVolume] = useState(0.5);
  const [vibration, setVibration] = useState(true);
  const [muted, setMuted] = useState(false);

  // NEW STATES - Advanced Features
  const [playerStats, setPlayerStats] = useState(initializePlayerStats());
  const [achievements, setAchievements] = useState([]);
  const [showStats, setShowStats] = useState(false);
  const [showAchievements, setShowAchievements] = useState(false);
  const [showTutorial, setShowTutorial] = useState(false);
  const [tutorialStep, setTutorialStep] = useState(0);
  const [gameMode, setGameMode] = useState("normal"); // normal, practice, daily, zen
  const [practiceCategory, setPracticeCategory] = useState("all");
  const [categories, setCategories] = useState([]);
  const [comboCount, setComboCount] = useState(0);
  const [lastWordTime, setLastWordTime] = useState(null);
  const [hintsUsedThisGame, setHintsUsedThisGame] = useState(0);
  const [inspirationalQuote, setInspirationalQuote] = useState("");
  const [showModeSelector, setShowModeSelector] = useState(false);

  // Refs for advanced features
  const selectionHistoryRef = useRef(new SelectionHistory(10));
  const performanceTrackerRef = useRef(new PerformanceTracker());
  const gridRef = useRef(null);

  // Load achievements and categories on mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Load achievements
        const achievementsRes = await axios.get(`${API}/achievements?language=${lang}`);
        setAchievements(achievementsRes.data);

        // Load categories
        const categoriesRes = await axios.get(`${API}/categories?language=${lang}`);
        setCategories(categoriesRes.data);

        // Load player stats
        const stats = getPlayerStats();
        setPlayerStats(stats);

        // Check if first time player
        if (isFirstTimePlayer()) {
          setShowTutorial(true);
        }
      } catch (error) {
        console.error("Error loading initial data:", error);
      }
    };

    loadInitialData();
  }, [lang]);

  // Check for level up
  useEffect(() => {
    const currentLevel = Math.floor(playerStats.totalXP / 1000) + 1;
    if (currentLevel > playerStats.level && gameState === "playing") {
      createLevelUpEffect(currentLevel);
      playLevelUpSound(muted);
      const updatedStats = updatePlayerStats({ level: currentLevel });
      setPlayerStats(updatedStats);
    }
  }, [playerStats.totalXP, gameState, muted]);

  // UI state
  const [orientation, setOrientation] = useState("portrait");
  const [deviceType, setDeviceType] = useState("mobile");
  const [aiLoading, setAiLoading] = useState(false);
  const [scoreAnimating, setScoreAnimating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Refs
  const isSwiping = useRef(false);
  const timerRef = useRef(null);
  const lastCell = useRef(null);

  const t = i18n[lang];

  // Dark/Light mode detection and application
  useEffect(() => {
    const applyTheme = () => {
      let dark = true;
      if (displayMode === "auto") {
        dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      } else {
        dark = displayMode === "dark";
      }
      setIsDarkMode(dark);
      document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
    };

    applyTheme();

    if (displayMode === "auto") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      mediaQuery.addEventListener("change", applyTheme);
      return () => mediaQuery.removeEventListener("change", applyTheme);
    }
  }, [displayMode]);

  // Apply color theme class
  useEffect(() => {
    document.documentElement.className = `theme-${theme}`;
  }, [theme]);

  // Device detection
  useEffect(() => {
    const checkDevice = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      const isLandscapeMode = width > height;
      setOrientation(isLandscapeMode ? "landscape" : "portrait");
      const checkDimension = isLandscapeMode ? height : width;
      if (checkDimension < 500) setDeviceType("mobile");
      else if (checkDimension < 900) setDeviceType("tablet");
      else setDeviceType("desktop");
    };
    checkDevice();
    window.addEventListener("resize", checkDevice);
    window.addEventListener("orientationchange", () => setTimeout(checkDevice, 100));
    return () => {
      window.removeEventListener("resize", checkDevice);
      window.removeEventListener("orientationchange", checkDevice);
    };
  }, []);

  // Timer
  useEffect(() => {
    if (gameState === "playing" && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current);
            setGameState("lose");
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timerRef.current);
  }, [gameState]);

  // Win check
  useEffect(() => {
    if (gameState === "playing" && words.length > 0 && foundWords.length === words.length) {
      clearInterval(timerRef.current);
      setGameState("win");
      if (!muted) playWinSound();
      triggerConfetti();
      
      // Record game completion
      const updatedStats = recordGameCompletion(
        level,
        score,
        foundWords.length,
        hintsUsedThisGame,
        timeLeft,
        lang
      );
      setPlayerStats(updatedStats);
      
      // Check for new achievements
      const newAchievements = checkAchievements(updatedStats, achievements);
      if (newAchievements.length > 0) {
        newAchievements.forEach((achievement, index) => {
          setTimeout(() => {
            createAchievementToast(achievement);
            playAchievementSound(muted);
          }, index * 600);
        });
      }
      
      // Mark as played
      markAsPlayed();
      
      if (level >= maxUnlockedLevel) {
        setMaxUnlockedLevel(Math.min(level + 1, 10));
      }
      
      // Reset combo and hints
      setComboCount(0);
      setHintsUsedThisGame(0);
      performanceTrackerRef.current.reset();
    }
  }, [foundWords, words, gameState, level, score, timeLeft, lang, hintsUsedThisGame, maxUnlockedLevel, muted, achievements]);

  const triggerConfetti = () => {
    const end = Date.now() + 2500;
    const frame = () => {
      confetti({ particleCount: 4, angle: 60, spread: 55, origin: { x: 0 }, colors: ['#00D4FF', '#8B5CF6', '#F472B6', '#22C55E'] });
      confetti({ particleCount: 4, angle: 120, spread: 55, origin: { x: 1 }, colors: ['#00D4FF', '#8B5CF6', '#F472B6', '#22C55E'] });
      if (Date.now() < end) requestAnimationFrame(frame);
    };
    frame();
  };

  const loadGame = useCallback(async (selectedLevel = level) => {
    try {
      const response = await axios.post(`${API}/game/generate`, { level: selectedLevel, language: lang });
      setMatrix(response.data.matrix);
      setWords(response.data.words);
      setTimeLimit(response.data.time_limit);
      setTimeLeft(response.data.time_limit);
      setFoundWords([]);
      setSelection([]);
      setHintCells([]);
      setKnowledgeText(t.welcome);
      setCurrentCategory("");
      setLevel(selectedLevel);
      setGameState("playing");
    } catch (error) {
      console.error("Error loading game:", error);
    }
  }, [lang, t.welcome, level]);

  const startGame = () => loadGame(level);
  const nextLevel = () => loadGame(Math.min(level + 1, 10));
  const resetGame = () => { setLevel(1); setScore(0); setGameState("start"); setShowExit(false); };
  const selectLevel = (newLevel) => { if (newLevel <= maxUnlockedLevel) { setLevel(newLevel); setShowLevelSelect(false); if (gameState === "playing") loadGame(newLevel); } };

  const handleCellPointerDown = (r, c, e) => { e.preventDefault(); isSwiping.current = true; lastCell.current = `${r}-${c}`; selectCell(r, c); };
  const handleCellPointerEnter = (r, c) => { const cellKey = `${r}-${c}`; if (isSwiping.current && lastCell.current !== cellKey) { lastCell.current = cellKey; selectCell(r, c); } };
  const handlePointerUp = () => { isSwiping.current = false; lastCell.current = null; };

  const selectCell = (r, c) => {
    const isSelected = selection.some((s) => s.r === r && s.c === c);
    if (!isSelected) {
      if (vibration && navigator.vibrate) navigator.vibrate(8);
      if (!muted) playSelectSound();
      const newSelection = [...selection, { r, c }];
      setSelection(newSelection);
      checkWord(newSelection);
    } else if (!isSwiping.current) {
      if (!muted) playClickSound();
      setSelection(selection.filter(s => !(s.r === r && s.c === c)));
    }
  };

  const checkWord = async (currentSelection) => {
    const selectedWord = currentSelection.map((s) => matrix[s.r][s.c]).join("");
    const reversedWord = selectedWord.split("").reverse().join("");
    const foundWord = words.find((w) => (w.word === selectedWord || w.word === reversedWord) && !foundWords.some((fw) => fw.word === w.word));

    if (foundWord) {
      // Stop performance tracking
      const wordTime = performanceTrackerRef.current.endWord();
      
      // Update found words and score
      setFoundWords((prev) => [...prev, foundWord]);
      setSelection([]);
      
      // Calculate multiplier
      const multiplier = calculateScoreMultiplier(timeLeft, timeLimit, comboCount, hintsUsedThisGame);
      const baseScore = 200;
      const finalScore = Math.round(baseScore * multiplier);
      setScore((prev) => prev + finalScore);
      setScoreAnimating(true);
      setTimeout(() => setScoreAnimating(false), 400);
      
      // Update combo
      const newCombo = comboCount + 1;
      setComboCount(newCombo);
      updateStreak(true);
      
      // Play category sound
      playCategorySound(foundWord.category, muted);
      
      // Vibration feedback
      if (vibration && navigator.vibrate) navigator.vibrate([40, 20, 40]);

      // Visual effects
      const cells = currentSelection.map(s => document.querySelector(`[data-cell="${s.r}-${s.c}"]`));
      wordRevealWave(cells, foundWord.category);
      createCategoryParticles(foundWord.category, window.innerWidth / 2, window.innerHeight / 2);
      fireCategoryConfetti(foundWord.category);
      flashScreen('#22C55E', 150);
      
      // Show score multiplier if > 1
      if (multiplier > 1) {
        showFloatingText(`+${finalScore} (${multiplier}x)`, window.innerWidth / 2, window.innerHeight / 3, '#F59E0B');
      }
      
      // Combo effect
      if (newCombo >= 3) {
        createComboEffect(newCombo, window.innerWidth / 2, window.innerHeight / 2);
        playComboSound(newCombo, muted);
      }

      // Record word in stats
      const updatedStats = recordWord(foundWord.category, lang, wordTime);
      setPlayerStats(updatedStats);
      
      // Check achievements
      const newAchievements = checkAchievements(updatedStats, achievements);
      if (newAchievements.length > 0) {
        newAchievements.forEach((achievement, index) => {
          setTimeout(() => {
            createAchievementToast(achievement);
            playAchievementSound(muted);
          }, index * 500);
        });
      }

      // Get inspirational quote
      try {
        const quoteRes = await axios.get(`${API}/inspirational-quote`, {
          params: { category: foundWord.category, language: lang }
        });
        setInspirationalQuote(quoteRes.data.quote);
        setKnowledgeText("✨ " + quoteRes.data.quote);
        setCurrentCategory(foundWord.categoryName);
      } catch {
        setKnowledgeText("💡 " + foundWord.info);
        setCurrentCategory(foundWord.categoryName);
      }

      // Clear hint cells
      setHintCells([]);
      
      // Start tracking next word
      performanceTrackerRef.current.startWord();
    }
  };

  const clearSelection = () => { setSelection([]); if (!muted) playClickSound(); };

  const useAIHint = async () => {
    if (score < 100 || aiLoading) return;
    const pendingWord = words.find((w) => !foundWords.some((fw) => fw.word === w.word));
    if (!pendingWord) return;
    
    setScore((prev) => prev - 100);
    setHintsUsedThisGame((prev) => prev + 1);
    setAiLoading(true);
    
    // Generate smart contextual hint
    const smartHint = generateSmartHint(pendingWord.word, [], pendingWord.category, lang);
    setKnowledgeText(smartHint);
    
    // Visual hint - show general region
    const visualHint = generateVisualHint(pendingWord.coords, matrix.length);
    setTimeout(() => {
      setKnowledgeText(visualHint.message[lang] || visualHint.message.ES);
    }, 2000);
    
    // Subtle hint cells (don't give exact position)
    setHintCells(pendingWord.coords.slice(0, 2).map((c) => `${c.r}-${c.c}`));
    setAiLoading(false);
    
    // Reset combo on hint use
    setComboCount(0);
    updateStreak(false);
    
    setTimeout(() => setHintCells([]), 4000);
  };

  const handleShare = async () => {
    try {
      const response = await axios.post(`${API}/share/generate`, { score, level, words_found: foundWords.length, language: lang });
      const shareText = response.data.text;
      if (navigator.share) {
        await navigator.share({ title: "AbdoulGame", text: shareText, url: window.location.href });
      } else {
        await navigator.clipboard.writeText(shareText + "\n" + window.location.href);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch (error) {}
  };

  const toggleLang = () => { const order = ["ES", "EN", "FR"]; setLang(order[(order.indexOf(lang) + 1) % order.length]); if (!muted) playClickSound(); };
  const toggleTheme = () => { setTheme(themes[(themes.indexOf(theme) + 1) % themes.length]); if (!muted) playClickSound(); };
  const cycleDisplayMode = () => { const modes = ["auto", "dark", "light"]; setDisplayMode(modes[(modes.indexOf(displayMode) + 1) % modes.length]); if (!muted) playClickSound(); };

  const formatTime = (seconds) => { const m = Math.floor(seconds / 60).toString().padStart(2, "0"); const s = (seconds % 60).toString().padStart(2, "0"); return `${m}:${s}`; };

  const progress = words.length > 0 ? (foundWords.length / words.length) * 100 : 0;
  const selectionText = selection.map((s) => matrix[s.r]?.[s.c] || "").join("");
  const isLandscape = orientation === "landscape";
  const isMobile = deviceType === "mobile";
  const isLandscapeMobile = isLandscape && isMobile;

  const renderGameGrid = () => (
    <div className="glass-light rounded-2xl p-2 w-full game-grid-wrapper" style={{ display: "grid", gridTemplateColumns: `repeat(${matrix.length}, 1fr)`, gap: isMobile ? "4px" : "6px", maxWidth: isLandscapeMobile ? "calc(100vh - 40px)" : "100%", maxHeight: isLandscapeMobile ? "calc(100vh - 40px)" : undefined }} data-testid="game-board">
      {matrix.map((row, r) => row.map((cell, c) => {
        const key = `${r}-${c}`;
        const isSelected = selection.some((s) => s.r === r && s.c === c);
        const isFound = foundWords.some((w) => w.coords.some((coord) => coord.r === r && coord.c === c));
        const isHint = hintCells.includes(key);
        return (
          <div key={key} className={`grid-cell ${isSelected ? "selected" : ""} ${isFound ? "found" : ""} ${isHint ? "hint" : ""}`}
            onPointerDown={(e) => handleCellPointerDown(r, c, e)} onPointerEnter={() => handleCellPointerEnter(r, c)}
            style={{ animationDelay: `${(r * matrix.length + c) * 10}ms` }} 
            data-testid={`grid-cell-${r}-${c}`}
            data-cell={`${r}-${c}`}>
            {cell}
          </div>
        );
      }))}
    </div>
  );

  const renderWordBank = () => (
    <div className={`word-bank flex gap-2 justify-center px-4 py-2 ${isMobile ? "flex-nowrap overflow-x-auto" : "flex-wrap"}`} data-testid="word-bank">
      {words.map((w) => (
        <span key={w.word} className={`word-tag ${foundWords.some((fw) => fw.word === w.word) ? "found" : ""}`} data-testid={`word-tag-${w.word}`}>
          {w.word}
        </span>
      ))}
    </div>
  );

  const renderControls = () => (
    <div className={`controls-bottom flex items-center justify-center gap-3 p-4 ${isLandscapeMobile ? "flex-col" : ""}`} data-testid="controls">
      <button className={`btn-game btn-primary ${aiLoading ? "ai-thinking" : ""}`} onClick={useAIHint} disabled={score < 100 || aiLoading} style={{ opacity: score < 100 ? 0.5 : 1 }} data-testid="hint-button">
        <Sparkles size={18} />{t.hint}
      </button>
      <button className="btn-game btn-danger" onClick={clearSelection} data-testid="clear-button">
        <RotateCcw size={18} />{t.clear}
      </button>
      <button className="btn-icon" onClick={() => setMuted(!muted)} data-testid="mute-button">
        {muted ? <VolumeX size={20} /> : <Volume2 size={20} />}
      </button>
    </div>
  );

  const GuideModal = () => (
    <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4" data-testid="guide-modal">
      <div className="modal-content glass-strong rounded-3xl p-5 md:p-6 max-w-md w-full max-h-[90vh] overflow-hidden">
        <h2 className="font-heading text-xl md:text-2xl mb-4 text-center" style={{ color: "var(--accent-primary)" }}>{t.guideTitle}</h2>
        <div className="guide-scroll">
          <div className="guide-section"><div className="flex items-start gap-3"><div className="guide-icon"><Target size={22} /></div><div><h3 className="guide-title">{t.guideObjective}</h3><p className="guide-text">{t.guideObjectiveText}</p></div></div></div>
          <div className="guide-section"><div className="flex items-start gap-3"><div className="guide-icon"><Hand size={22} /></div><div><h3 className="guide-title">{t.guideControls}</h3><p className="guide-text">{t.guideControlsText}</p></div></div></div>
          <div className="guide-section"><div className="flex items-start gap-3"><div className="guide-icon"><Star size={22} /></div><div><h3 className="guide-title">{t.guideFeatures}</h3><p className="guide-text">{t.guideFeaturesText}</p></div></div></div>
          <div className="guide-section"><div className="flex items-start gap-3"><div className="guide-icon"><Palette size={22} /></div><div><h3 className="guide-title">{t.guideThemes}</h3><p className="guide-text">{t.guideThemesText}</p></div></div></div>
          <div className="guide-section"><div className="flex items-start gap-3"><div className="guide-icon"><BookOpen size={22} /></div><div><h3 className="guide-title">{t.guideLearning}</h3><p className="guide-text">{t.guideLearningText}</p></div></div></div>
          <div className="guide-section"><div className="flex items-start gap-3"><div className="guide-icon"><Share2 size={22} /></div><div><h3 className="guide-title">{t.guideShare}</h3><p className="guide-text">{t.guideShareText}</p></div></div></div>
        </div>
        <button className="btn-game btn-primary w-full mt-4" onClick={() => setShowGuide(false)} data-testid="close-guide-button"><Check size={18} />{t.guideClose}</button>
      </div>
    </div>
  );

  const displayModeIcon = displayMode === "auto" ? (isDarkMode ? <Moon size={18} /> : <Sun size={18} />) : displayMode === "dark" ? <Moon size={18} /> : <Sun size={18} />;
  const displayModeText = displayMode === "auto" ? t.autoMode : displayMode === "dark" ? t.darkMode : t.lightMode;

  // Game mode handlers
  const handleSelectGameMode = async (mode, category) => {
    setGameMode(mode);
    setPracticeCategory(category || "all");
    setShowModeSelector(false);
    
    if (mode === "daily") {
      // Load daily challenge
      try {
        const response = await axios.get(`${API}/daily-challenge?language=${lang}`);
        setMatrix(response.data.board.matrix);
        setWords(response.data.board.words);
        setTimeLimit(response.data.board.time_limit);
        setTimeLeft(response.data.board.time_limit);
        setFoundWords([]);
        setSelection([]);
        setLevel(response.data.level);
        setGameState("playing");
      } catch (error) {
        console.error("Error loading daily challenge:", error);
      }
    } else {
      // Normal, practice, or zen mode
      loadGame(level);
    }
  };

  return (
    <div className={`theme-${theme} relative w-full h-screen flex flex-col overflow-hidden`}
      style={{ backgroundColor: "var(--bg-primary)", backgroundImage: isDarkMode ? `radial-gradient(ellipse at top, color-mix(in srgb, var(--accent-secondary) 8%, transparent), transparent)` : "none" }}
      onPointerUp={handlePointerUp} onPointerLeave={handlePointerUp}>

      {/* Modals */}
      {showStats && (
        <StatsModal 
          stats={playerStats}
          lang={lang}
          onClose={() => setShowStats(false)}
        />
      )}
      
      {showAchievements && (
        <AchievementsModal
          achievements={achievements}
          unlockedIds={playerStats.unlockedAchievements}
          lang={lang}
          onClose={() => setShowAchievements(false)}
        />
      )}
      
      {showModeSelector && (
        <GameModeSelector
          lang={lang}
          categories={categories}
          onSelectMode={handleSelectGameMode}
          onClose={() => setShowModeSelector(false)}
        />
      )}

      {/* Progress Bar */}
      {gameState === "playing" && (
        <div className="progress-container absolute top-0 left-0 w-full h-1.5 z-50" data-testid="progress-container">
          <div className="h-full progress-fill" style={{ width: `${progress}%` }} data-testid="progress-bar" />
        </div>
      )}

      {/* Start Modal */}
      {gameState === "start" && (
        <div className="modal-backdrop absolute inset-0 flex flex-col items-center justify-center z-50 p-6" style={{ background: "transparent" }} data-testid="start-modal">
          <div className="modal-content text-center">
            <h1 className="font-heading text-4xl md:text-5xl text-glow mb-1 animate-float" style={{ color: "var(--accent-primary)" }}>{t.title}</h1>
            <p className="font-mono text-xs md:text-sm mb-6 tracking-widest" style={{ color: "var(--text-muted)" }}>{t.subtitle}</p>
            
            <div className="level-selector mb-6 mx-auto" style={{ width: "fit-content" }}>
              <button className="level-btn" onClick={() => { setLevel(Math.max(1, level - 1)); if(!muted) playClickSound(); }} disabled={level <= 1}><ChevronDown size={18} /></button>
              <div className="text-center px-4">
                <span className="font-heading text-3xl" style={{ color: "var(--accent-primary)" }}>{level}</span>
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t.level}</p>
              </div>
              <button className="level-btn" onClick={() => { setLevel(Math.min(maxUnlockedLevel, level + 1)); if(!muted) playClickSound(); }} disabled={level >= maxUnlockedLevel}><ChevronUp size={18} /></button>
            </div>

            <button className="btn-game btn-primary text-base md:text-lg px-8 md:px-10 py-4 mb-4" onClick={startGame} data-testid="start-button"><Play size={22} />{t.enterStadium}</button>
            <button className="btn-game btn-secondary mb-4" onClick={() => setShowModeSelector(true)} data-testid="mode-selector-button"><Target size={18} />{lang === 'ES' ? 'Modos de Juego' : lang === 'EN' ? 'Game Modes' : 'Modes de Jeu'}</button>
            <button className="btn-game btn-secondary mb-6" onClick={() => setShowGuide(true)} data-testid="guide-button"><HelpCircle size={18} />{t.guide}</button>
            
            <div className="flex justify-center gap-3 flex-wrap mb-4">
              <button className="btn-game btn-secondary py-2 px-4" onClick={() => setShowStats(true)} data-testid="stats-button">
                <BarChart3 size={18} />{lang === 'ES' ? 'Estadísticas' : lang === 'EN' ? 'Stats' : 'Statistiques'}
              </button>
              <button className="btn-game btn-secondary py-2 px-4" onClick={() => setShowAchievements(true)} data-testid="achievements-button">
                <Award size={18} />{lang === 'ES' ? 'Logros' : lang === 'EN' ? 'Achievements' : 'Succès'}
              </button>
            </div>
            
            <div className="flex justify-center gap-3 flex-wrap">
              <button className="btn-icon" onClick={toggleLang} data-testid="lang-toggle-start"><span className="text-xl">{languageFlags[lang]}</span></button>
              <button className="btn-icon" onClick={toggleTheme} data-testid="theme-toggle-start" title={themeNames[theme]}><Palette size={20} /></button>
              <button className="mode-toggle" onClick={cycleDisplayMode} data-testid="mode-toggle">{displayModeIcon}<span className="text-sm">{displayModeText}</span></button>
            </div>
            
            {/* XP Bar */}
            <div className="mt-6 w-full max-w-xs">
              <div className="flex justify-between text-sm mb-1" style={{ color: 'var(--text-secondary)' }}>
                <span>{lang === 'ES' ? 'Nivel' : lang === 'EN' ? 'Level' : 'Niveau'} {playerStats.level}</span>
                <span>{playerStats.totalXP % 1000}/1000 XP</span>
              </div>
              <div className="xp-bar">
                <div className="xp-fill" style={{ width: `${(playerStats.totalXP % 1000) / 10}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Game UI */}
      {gameState === "playing" && (
        <div className={`game-container flex h-full ${isLandscapeMobile ? "flex-row game-layout-landscape" : "flex-col"}`}>
          {isLandscapeMobile ? (
            <>
              <div className="sidebar-landscape glass">
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between items-center">
                    <button className="btn-icon w-9 h-9" onClick={() => setShowExit(true)} data-testid="exit-button"><X size={16} /></button>
                    <button className="btn-icon w-9 h-9" onClick={() => setShowGuide(true)} data-testid="guide-button-game"><HelpCircle size={16} /></button>
                    <button className="btn-icon w-9 h-9" onClick={() => setShowSettings(true)} data-testid="settings-button"><Settings size={16} /></button>
                  </div>
                  <div className={`font-mono text-lg font-bold text-center ${timeLeft <= 10 ? "timer-critical" : timeLeft <= 30 ? "timer-warning" : ""}`} style={{ color: timeLeft <= 30 ? undefined : "var(--accent-primary)" }} data-testid="timer-display">⏱️ {formatTime(timeLeft)}</div>
                  <div className={`font-mono text-base font-bold text-center ${scoreAnimating ? "score-pop" : ""}`} style={{ color: "var(--accent-primary)" }} data-testid="score-display">⭐ {score}</div>
                  {comboCount >= 3 && (
                    <div className="text-center font-bold text-sm" style={{ color: 'var(--warning)' }}>
                      🔥 {comboCount}x {lang === 'ES' ? 'COMBO' : 'COMBO'}
                    </div>
                  )}
                </div>
                <div className="flex flex-col gap-1 my-2 overflow-y-auto flex-1">
                  {words.map((w) => (<span key={w.word} className={`word-tag text-center text-xs py-1 px-2 ${foundWords.some((fw) => fw.word === w.word) ? "found" : ""}`}>{w.word}</span>))}
                </div>
                <div className="flex flex-col gap-2">
                  <button className={`btn-game btn-primary py-2 px-3 text-xs ${aiLoading ? "ai-thinking" : ""}`} onClick={useAIHint} disabled={score < 100 || aiLoading} style={{ opacity: score < 100 ? 0.5 : 1 }} data-testid="hint-button"><Sparkles size={14} />{t.hint}</button>
                  <button className="btn-game btn-danger py-2 px-3 text-xs" onClick={clearSelection} data-testid="clear-button"><RotateCcw size={14} />{t.clear}</button>
                </div>
              </div>
              <div className="main-landscape flex-1 flex items-center justify-center p-2 overflow-hidden">{renderGameGrid()}</div>
            </>
          ) : (
            <>
              <div className="top-bar flex items-center justify-between p-3 md:p-4 pt-5 md:pt-6 glass" data-testid="top-bar">
                <button className="btn-icon" onClick={() => setShowExit(true)} data-testid="exit-button"><X size={18} /></button>
                <div className={`font-mono text-xl md:text-2xl font-bold ${timeLeft <= 10 ? "timer-critical" : timeLeft <= 30 ? "timer-warning" : ""}`} style={{ color: timeLeft <= 30 ? undefined : "var(--accent-primary)" }} data-testid="timer-display">⏱️ {formatTime(timeLeft)}</div>
                <button className="btn-icon text-sm font-bold" onClick={() => setShowLevelSelect(true)} data-testid="level-selector">L{level}</button>
                <button className="btn-icon" onClick={() => setShowGuide(true)} data-testid="guide-button-game"><HelpCircle size={18} /></button>
                <button className="btn-icon" onClick={() => setShowSettings(true)} data-testid="settings-button"><Settings size={18} /></button>
                <div className={`font-mono text-lg md:text-xl font-bold ${scoreAnimating ? "score-pop" : ""}`} style={{ color: "var(--accent-primary)" }} data-testid="score-display">⭐ {score}</div>
              </div>
              <div className="h-10 md:h-12 flex items-center justify-center glass-light" data-testid="selection-preview"><span className="selection-preview">{selectionText || t.tap}</span></div>
              <div className="knowledge-banner mx-3 md:mx-4 my-2 p-3 md:p-4 rounded-2xl text-center" data-testid="knowledge-banner">
                {currentCategory && <span className="category-badge mb-2">{currentCategory}</span>}
                <p className="text-sm" style={{ color: "var(--text-primary)" }}>{knowledgeText}</p>
              </div>
              <div className="flex-1 flex items-center justify-center p-3 md:p-4 overflow-hidden">{renderGameGrid()}</div>
              {renderWordBank()}
              {renderControls()}
            </>
          )}
        </div>
      )}

      {/* Win Modal */}
      {gameState === "win" && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6" data-testid="win-modal">
          <div className="modal-content glass-strong rounded-3xl p-6 md:p-8 max-w-sm w-full text-center">
            <div className="trophy-animate text-6xl mb-4">🏆</div>
            <h2 className="font-heading text-3xl md:text-4xl mb-2" style={{ color: "var(--success)" }}>{t.goal}</h2>
            <p className="text-base md:text-lg mb-4" style={{ color: "var(--text-secondary)" }}>{t.levelComplete}</p>
            <div className="flex justify-center gap-6 my-6">
              <div><p className="text-2xl md:text-3xl font-bold" style={{ color: "var(--accent-primary)" }}>{score}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>{t.score}</p></div>
              <div><p className="text-2xl md:text-3xl font-bold" style={{ color: "var(--accent-secondary)" }}>{level}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>{t.level}</p></div>
              <div><p className="text-2xl md:text-3xl font-bold" style={{ color: "var(--success)" }}>{foundWords.length}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>{t.wordsFound}</p></div>
            </div>
            <div className="flex flex-col gap-3">
              <button className="btn-game btn-primary w-full" onClick={nextLevel} data-testid="next-level-button"><Zap size={18} />{t.next}</button>
              <button className="share-btn w-full justify-center" onClick={handleShare} data-testid="share-button"><Share2 size={18} />{copied ? t.copied : t.share}</button>
            </div>
          </div>
        </div>
      )}

      {/* Lose Modal */}
      {gameState === "lose" && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6" data-testid="lose-modal">
          <div className="modal-content glass-strong rounded-3xl p-6 md:p-8 max-w-sm w-full text-center">
            <h2 className="font-heading text-3xl md:text-4xl mb-4" style={{ color: "var(--error)" }}>{t.timeUp}</h2>
            <div className="flex justify-center gap-6 my-6">
              <div><p className="text-2xl md:text-3xl font-bold" style={{ color: "var(--accent-primary)" }}>{score}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>{t.score}</p></div>
              <div><p className="text-2xl md:text-3xl font-bold" style={{ color: "var(--accent-secondary)" }}>{foundWords.length}/{words.length}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>{t.wordsFound}</p></div>
            </div>
            <div className="flex flex-col gap-3">
              <button className="btn-game btn-primary w-full" onClick={() => loadGame(level)} data-testid="retry-button"><RotateCcw size={18} />{t.playAgain}</button>
              <button className="share-btn w-full justify-center" onClick={handleShare} data-testid="share-lose-button"><Share2 size={18} />{copied ? t.copied : t.share}</button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6" data-testid="settings-modal">
          <div className="modal-content glass-strong rounded-3xl p-5 md:p-6 max-w-sm w-full">
            <h2 className="font-heading text-xl md:text-2xl mb-6 text-center" style={{ color: "var(--accent-primary)" }}>{t.settings}</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b" style={{ borderColor: "var(--border-color)" }}><span className="flex items-center gap-2"><Volume2 size={18} />{t.volume}</span><input type="range" min="0" max="1" step="0.1" value={volume} onChange={(e) => setVolume(parseFloat(e.target.value))} className="w-24" data-testid="volume-slider" /></div>
              <div className="flex justify-between items-center py-3 border-b" style={{ borderColor: "var(--border-color)" }}><span className="flex items-center gap-2"><Globe size={18} />{t.language}</span><button className="btn-icon text-xl" onClick={toggleLang} data-testid="language-toggle">{languageFlags[lang]}</button></div>
              <div className="flex justify-between items-center py-3 border-b" style={{ borderColor: "var(--border-color)" }}><span className="flex items-center gap-2"><Palette size={18} />{t.theme}</span><button className="btn-icon px-3 w-auto rounded-xl text-sm font-bold" onClick={toggleTheme} data-testid="theme-toggle">{themeNames[theme]}</button></div>
              <div className="flex justify-between items-center py-3 border-b" style={{ borderColor: "var(--border-color)" }}><span className="flex items-center gap-2">{isDarkMode ? <Moon size={18} /> : <Sun size={18} />}{t.displayMode}</span><button className="btn-icon px-3 w-auto rounded-xl text-sm font-bold" onClick={cycleDisplayMode} data-testid="display-mode-toggle">{displayModeText}</button></div>
              <div className="flex justify-between items-center py-3 border-b" style={{ borderColor: "var(--border-color)" }}><span className="flex items-center gap-2"><Smartphone size={18} />{t.vibration}</span><button className={`btn-icon px-3 w-auto rounded-xl text-sm font-bold ${vibration ? "" : ""}`} style={{ background: vibration ? "var(--success)" : undefined, color: vibration ? "white" : undefined }} onClick={() => setVibration(!vibration)} data-testid="vibration-toggle">{vibration ? t.on : t.off}</button></div>
            </div>
            <button className="btn-game btn-primary w-full mt-6" onClick={() => setShowSettings(false)} data-testid="save-settings-button">{t.save}</button>
          </div>
        </div>
      )}

      {/* Level Select Modal */}
      {showLevelSelect && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6" data-testid="level-select-modal">
          <div className="modal-content glass-strong rounded-3xl p-5 md:p-6 max-w-sm w-full">
            <h2 className="font-heading text-xl md:text-2xl mb-6 text-center" style={{ color: "var(--accent-primary)" }}>{t.level}</h2>
            <div className="grid grid-cols-5 gap-3">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((lvl) => (<button key={lvl} className={`level-btn w-full aspect-square text-lg ${lvl === level ? "" : ""}`} style={{ background: lvl === level ? "var(--accent-primary)" : undefined, color: lvl === level ? "white" : undefined }} onClick={() => selectLevel(lvl)} disabled={lvl > maxUnlockedLevel} data-testid={`level-btn-${lvl}`}>{lvl <= maxUnlockedLevel ? lvl : "🔒"}</button>))}
            </div>
            <button className="btn-game btn-secondary w-full mt-6" onClick={() => setShowLevelSelect(false)} data-testid="close-level-select"><X size={18} /></button>
          </div>
        </div>
      )}

      {/* Exit Modal */}
      {showExit && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6" data-testid="exit-modal">
          <div className="modal-content glass-strong rounded-3xl p-5 md:p-6 max-w-sm w-full text-center">
            <h2 className="font-heading text-lg md:text-xl mb-6">{t.exit}</h2>
            <div className="flex gap-4 justify-center">
              <button className="btn-game btn-danger" onClick={resetGame} data-testid="confirm-exit-button">{t.yes}</button>
              <button className="btn-game btn-primary" onClick={() => setShowExit(false)} data-testid="cancel-exit-button">{t.no}</button>
            </div>
          </div>
        </div>
      )}

      {showGuide && <GuideModal />}
    </div>
  );
}

export default App;
