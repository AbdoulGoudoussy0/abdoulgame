import React, { useState, useEffect, useCallback, useRef } from "react";
import "@/App.css";
import axios from "axios";
import { 
  Settings, Lightbulb, X, Volume2, VolumeX, Trophy, RotateCcw, Play, 
  Share2, ChevronUp, ChevronDown, Sparkles, Zap, Globe, Palette,
  Smartphone, Monitor, Tablet
} from "lucide-react";
import confetti from "canvas-confetti";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Soft, pleasant sound effects (base64 encoded short beeps)
const SOUNDS = {
  // Soft chime for word found
  correct: "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdH2IkY2Fc2hqa3yGj5KKgHJpZWt4g42RjYN3bWhjbHeDjZGOhXlwamVpd4KLj42FenFsZ2p2gYqOjYZ7c25panWAiY2Mh3x0cGtrdH+IjIuHfXVxbW11f4eLi4h+dnJub3R+houKiH93c29vdH2Gi4qIf3d0cHB0fYaKioh/d3RwcHR9hoqKiH93dHBwdH2GioqIf3d0cHB0fYaKioh/d3RwcHR9hoqKiH93dHBwdH2GioqIf3d0cHB0fYaKioh/d3RwcHR9hoqKiH93dHBwdH2GioqIf3d0cHB0fYaKioh/d3RwcHR9hoqKiH93dHBwdH2GioqIf3d0cHB0fQ==",
  // Celebration sound for level complete
  goal: "data:audio/wav;base64,UklGRl9CAABXQVZFZm10IBAAAAABAAEAIlYAABKwAAACABAAZGF0YTs/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
  // Click sound
  click: "data:audio/wav;base64,UklGRiQEAABXQVZFZm10IBAAAAABAAEARKwAABCxAgACABAAZGF0YQAEAACAgICAgICAgICAgICAgICAgICAgICAgICA"
};

// i18n translations
const i18n = {
  ES: {
    title: "ABDOULGAME",
    subtitle: "POLYGLOT EDITION",
    settings: "AJUSTES",
    volume: "VOLUMEN",
    language: "IDIOMA", 
    theme: "TEMA",
    vibration: "VIBRACIÓN",
    save: "GUARDAR",
    start: "COMENZAR",
    enterStadium: "ENTRAR AL ESTADIO",
    welcome: "Encuentra las palabras de sabiduría",
    exit: "¿SALIR DEL PARTIDO?",
    hint: "PISTA IA",
    clear: "BORRAR",
    next: "SIGUIENTE",
    tap: "TOCA UNA LETRA",
    goal: "¡GOOOOL!",
    levelComplete: "¡NIVEL COMPLETADO!",
    timeUp: "¡TIEMPO AGOTADO!",
    score: "PUNTOS",
    level: "NIVEL",
    wordsFound: "PALABRAS",
    playAgain: "JUGAR DE NUEVO",
    yes: "SÍ",
    no: "NO",
    on: "ON",
    off: "OFF",
    share: "COMPARTIR",
    shareTitle: "¡Comparte tu logro!",
    aiThinking: "IA pensando...",
    levelSelect: "Seleccionar Nivel",
    copied: "¡Copiado!",
    encouragement: "¡Sigue así, campeón!"
  },
  EN: {
    title: "ABDOULGAME",
    subtitle: "POLYGLOT EDITION",
    settings: "SETTINGS",
    volume: "VOLUME",
    language: "LANGUAGE",
    theme: "THEME",
    vibration: "VIBRATION",
    save: "SAVE",
    start: "START",
    enterStadium: "ENTER STADIUM",
    welcome: "Find the words of wisdom",
    exit: "QUIT MATCH?",
    hint: "AI HINT",
    clear: "CLEAR",
    next: "NEXT",
    tap: "TAP A LETTER",
    goal: "GOOOAL!",
    levelComplete: "LEVEL COMPLETE!",
    timeUp: "TIME'S UP!",
    score: "SCORE",
    level: "LEVEL",
    wordsFound: "WORDS",
    playAgain: "PLAY AGAIN",
    yes: "YES",
    no: "NO",
    on: "ON",
    off: "OFF",
    share: "SHARE",
    shareTitle: "Share your achievement!",
    aiThinking: "AI thinking...",
    levelSelect: "Select Level",
    copied: "Copied!",
    encouragement: "Keep going, champion!"
  },
  FR: {
    title: "ABDOULGAME",
    subtitle: "ÉDITION POLYGLOTTE",
    settings: "RÉGLAGES",
    volume: "VOLUME",
    language: "LANGUE",
    theme: "THÈME",
    vibration: "VIBRATION",
    save: "ENREGISTRER",
    start: "COMMENCER",
    enterStadium: "ENTRER AU STADE",
    welcome: "Trouvez les mots de sagesse",
    exit: "QUITTER LE MATCH?",
    hint: "INDICE IA",
    clear: "EFFACER",
    next: "SUIVANT",
    tap: "TOUCHEZ UNE LETTRE",
    goal: "BUUUT!",
    levelComplete: "NIVEAU TERMINÉ!",
    timeUp: "TEMPS ÉCOULÉ!",
    score: "POINTS",
    level: "NIVEAU",
    wordsFound: "MOTS",
    playAgain: "REJOUER",
    yes: "OUI",
    no: "NON",
    on: "ON",
    off: "OFF",
    share: "PARTAGER",
    shareTitle: "Partagez votre exploit!",
    aiThinking: "IA réfléchit...",
    levelSelect: "Sélectionner Niveau",
    copied: "Copié!",
    encouragement: "Continue comme ça, champion!"
  }
};

const languageFlags = { ES: "🇪🇸", EN: "🇺🇸", FR: "🇫🇷" };
const themes = ["neon", "classic", "gold"];
const themeIcons = { neon: "⚡", classic: "🎯", gold: "🏆" };

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
  const [timeLeft, setTimeLeft] = useState(150);
  const [timeLimit, setTimeLimit] = useState(150);
  const [knowledgeText, setKnowledgeText] = useState("");

  // Settings state
  const [showSettings, setShowSettings] = useState(false);
  const [showExit, setShowExit] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [showLevelSelect, setShowLevelSelect] = useState(false);
  const [lang, setLang] = useState("ES");
  const [theme, setTheme] = useState("neon");
  const [volume, setVolume] = useState(0.5);
  const [vibration, setVibration] = useState(true);
  const [muted, setMuted] = useState(false);

  // UI state
  const [orientation, setOrientation] = useState("portrait");
  const [deviceType, setDeviceType] = useState("mobile");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiHint, setAiHint] = useState("");
  const [scoreAnimating, setScoreAnimating] = useState(false);
  const [copied, setCopied] = useState(false);

  // Refs
  const isSwiping = useRef(false);
  const timerRef = useRef(null);
  const audioRefs = useRef({});

  const t = i18n[lang];

  // Initialize audio
  useEffect(() => {
    audioRefs.current = {
      correct: new Audio(SOUNDS.correct),
      goal: new Audio(SOUNDS.goal),
      click: new Audio(SOUNDS.click)
    };
    
    Object.values(audioRefs.current).forEach(audio => {
      audio.volume = volume;
    });
  }, []);

  // Update audio volume
  useEffect(() => {
    Object.values(audioRefs.current).forEach(audio => {
      if (audio) audio.volume = muted ? 0 : volume;
    });
  }, [volume, muted]);

  // Detect device and orientation
  useEffect(() => {
    const checkDevice = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      const isLandscapeMode = width > height;
      setOrientation(isLandscapeMode ? "landscape" : "portrait");
      
      // For landscape, check by the smaller dimension (height)
      // For portrait, check by width
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

  // Timer effect
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

  // Check for win
  useEffect(() => {
    if (gameState === "playing" && words.length > 0 && foundWords.length === words.length) {
      clearInterval(timerRef.current);
      setGameState("win");
      playSound("goal");
      triggerConfetti();
      
      // Unlock next level
      if (level >= maxUnlockedLevel) {
        setMaxUnlockedLevel(Math.min(level + 1, 10));
      }
    }
  }, [foundWords, words, gameState, level, maxUnlockedLevel]);

  const playSound = (type) => {
    if (!muted && audioRefs.current[type]) {
      audioRefs.current[type].currentTime = 0;
      audioRefs.current[type].play().catch(() => {});
    }
  };

  const triggerConfetti = () => {
    const duration = 3000;
    const end = Date.now() + duration;

    const frame = () => {
      confetti({
        particleCount: 3,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ['#00F2FF', '#7000FF', '#FF00C8', '#39FF14', '#FFD700']
      });
      confetti({
        particleCount: 3,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ['#00F2FF', '#7000FF', '#FF00C8', '#39FF14', '#FFD700']
      });

      if (Date.now() < end) {
        requestAnimationFrame(frame);
      }
    };
    frame();
  };

  const loadGame = useCallback(async (selectedLevel = level) => {
    try {
      const response = await axios.post(`${API}/game/generate`, {
        level: selectedLevel,
        language: lang
      });
      
      setMatrix(response.data.matrix);
      setWords(response.data.words);
      setTimeLimit(response.data.time_limit);
      setTimeLeft(response.data.time_limit);
      setFoundWords([]);
      setSelection([]);
      setHintCells([]);
      setKnowledgeText(t.welcome);
      setAiHint("");
      setLevel(selectedLevel);
      setGameState("playing");
    } catch (error) {
      console.error("Error loading game:", error);
    }
  }, [lang, t.welcome, level]);

  const startGame = () => {
    loadGame(level);
  };

  const nextLevel = () => {
    const nextLvl = Math.min(level + 1, 10);
    loadGame(nextLvl);
  };

  const resetGame = () => {
    setLevel(1);
    setScore(0);
    setGameState("start");
    setShowExit(false);
  };

  const selectLevel = (newLevel) => {
    if (newLevel <= maxUnlockedLevel) {
      setLevel(newLevel);
      setShowLevelSelect(false);
      if (gameState === "playing") {
        loadGame(newLevel);
      }
    }
  };

  const handleCellPointerDown = (r, c, e) => {
    e.preventDefault();
    isSwiping.current = true;
    selectCell(r, c);
  };

  const handleCellPointerEnter = (r, c) => {
    if (isSwiping.current) {
      selectCell(r, c);
    }
  };

  const handlePointerUp = () => {
    isSwiping.current = false;
  };

  const selectCell = (r, c) => {
    const isFound = foundWords.some((w) =>
      w.coords.some((coord) => coord.r === r && coord.c === c)
    );
    if (isFound) return;

    const isSelected = selection.some((s) => s.r === r && s.c === c);
    if (!isSelected) {
      if (vibration && navigator.vibrate) navigator.vibrate(10);
      playSound("click");
      setSelection((prev) => [...prev, { r, c }]);
      checkWord([...selection, { r, c }]);
    }
  };

  const checkWord = async (currentSelection) => {
    const selectedWord = currentSelection.map((s) => matrix[s.r][s.c]).join("");
    const reversedWord = selectedWord.split("").reverse().join("");

    const foundWord = words.find(
      (w) =>
        (w.word === selectedWord || w.word === reversedWord) &&
        !foundWords.some((fw) => fw.word === w.word)
    );

    if (foundWord) {
      setFoundWords((prev) => [...prev, foundWord]);
      setSelection([]);
      setScore((prev) => prev + 200);
      setScoreAnimating(true);
      setTimeout(() => setScoreAnimating(false), 400);
      
      playSound("correct");
      
      // Get AI wisdom
      try {
        const response = await axios.post(`${API}/ai/wisdom`, null, {
          params: { word: foundWord.word, language: lang }
        });
        setKnowledgeText("💡 " + response.data.wisdom);
      } catch {
        setKnowledgeText("💡 " + foundWord.info);
      }
    }
  };

  const clearSelection = () => {
    setSelection([]);
    playSound("click");
  };

  const useAIHint = async () => {
    if (score < 100 || aiLoading) return;
    
    const pendingWord = words.find((w) => !foundWords.some((fw) => fw.word === w.word));
    if (!pendingWord) return;

    setScore((prev) => prev - 100);
    setAiLoading(true);
    
    // Show visual hint on cells
    setHintCells(pendingWord.coords.map((c) => `${c.r}-${c.c}`));
    
    try {
      const response = await axios.post(`${API}/ai/hint`, {
        word: pendingWord.word,
        language: lang,
        found_letters: []
      });
      setAiHint(response.data.hint);
      setKnowledgeText("🤖 " + response.data.encouragement);
    } catch {
      setAiHint(t.encouragement);
    }
    
    setAiLoading(false);
    setTimeout(() => {
      setHintCells([]);
      setAiHint("");
    }, 3000);
  };

  const handleShare = async () => {
    try {
      const response = await axios.post(`${API}/share/generate`, {
        score,
        level,
        words_found: foundWords.length,
        language: lang
      });
      
      const shareText = response.data.text;
      
      if (navigator.share) {
        await navigator.share({
          title: "AbdoulGame",
          text: shareText,
          url: window.location.href
        });
      } else {
        await navigator.clipboard.writeText(shareText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch (error) {
      console.error("Share error:", error);
    }
  };

  const toggleLang = () => {
    const order = ["ES", "EN", "FR"];
    const nextIdx = (order.indexOf(lang) + 1) % order.length;
    setLang(order[nextIdx]);
  };

  const toggleTheme = () => {
    const nextIdx = (themes.indexOf(theme) + 1) % themes.length;
    setTheme(themes[nextIdx]);
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  const progress = words.length > 0 ? (foundWords.length / words.length) * 100 : 0;
  const selectionText = selection.map((s) => matrix[s.r]?.[s.c] || "").join("");
  const isLandscape = orientation === "landscape";
  const isMobile = deviceType === "mobile";
  const isLandscapeMobile = isLandscape && isMobile;

  // Render game content based on layout
  const renderGameGrid = () => (
    <div
      className="glass-light rounded-2xl p-2 w-full game-grid-wrapper"
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${matrix.length}, 1fr)`,
        gap: isMobile ? "3px" : "5px",
        maxWidth: isLandscapeMobile ? "calc(100vh - 40px)" : "100%",
        maxHeight: isLandscapeMobile ? "calc(100vh - 40px)" : undefined
      }}
      data-testid="game-board"
    >
      {matrix.map((row, r) =>
        row.map((cell, c) => {
          const key = `${r}-${c}`;
          const isSelected = selection.some((s) => s.r === r && s.c === c);
          const isFound = foundWords.some((w) =>
            w.coords.some((coord) => coord.r === r && coord.c === c)
          );
          const isHint = hintCells.includes(key);

          return (
            <div
              key={key}
              className={`grid-cell ${isSelected ? "selected" : ""} ${isFound ? "found" : ""} ${isHint ? "hint" : ""}`}
              onPointerDown={(e) => handleCellPointerDown(r, c, e)}
              onPointerEnter={() => handleCellPointerEnter(r, c)}
              style={{ animationDelay: `${(r * matrix.length + c) * 15}ms` }}
              data-testid={`grid-cell-${r}-${c}`}
            >
              {cell}
            </div>
          );
        })
      )}
    </div>
  );

  const renderWordBank = () => (
    <div className={`word-bank flex gap-2 justify-center px-4 py-2 ${isMobile ? "flex-nowrap overflow-x-auto" : "flex-wrap"}`} data-testid="word-bank">
      {words.map((w) => (
        <span
          key={w.word}
          className={`word-tag ${foundWords.some((fw) => fw.word === w.word) ? "found" : ""}`}
          data-testid={`word-tag-${w.word}`}
        >
          {w.word}
        </span>
      ))}
    </div>
  );

  const renderControls = () => (
    <div className={`controls-bottom flex items-center justify-center gap-3 p-4 ${isLandscape && isMobile ? "flex-col" : ""}`} data-testid="controls">
      <button
        className={`btn-game btn-primary ${aiLoading ? "ai-thinking" : ""}`}
        onClick={useAIHint}
        disabled={score < 100 || aiLoading}
        style={{ opacity: score < 100 ? 0.5 : 1 }}
        data-testid="hint-button"
      >
        <Sparkles size={18} />
        {aiLoading ? t.aiThinking : t.hint}
      </button>
      <button className="btn-game btn-danger" onClick={clearSelection} data-testid="clear-button">
        <RotateCcw size={18} />
        {t.clear}
      </button>
      <button
        className="btn-icon"
        onClick={() => setMuted(!muted)}
        data-testid="mute-button"
      >
        {muted ? <VolumeX size={20} /> : <Volume2 size={20} />}
      </button>
    </div>
  );

  return (
    <div
      className={`theme-${theme} relative w-full h-screen flex flex-col overflow-hidden`}
      style={{
        backgroundImage: `linear-gradient(rgba(3,3,5,0.85), rgba(3,3,5,0.9)), url(https://static.prod-images.emergentagent.com/jobs/ce42bd3d-1e24-4f1c-a96b-aa9453dd1466/images/23855e63fb470783e9c6782789c2475fb72af4df0e0a7a5e68b614a1db5d8f88.png)`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed"
      }}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
    >
      {/* Progress Bar */}
      {gameState === "playing" && (
        <div className="progress-container absolute top-0 left-0 w-full h-1.5 bg-white/10 z-50" data-testid="progress-container">
          <div
            className="h-full progress-fill"
            style={{ width: `${progress}%`, background: "linear-gradient(to right, var(--theme-secondary), var(--theme-primary))" }}
            data-testid="progress-bar"
          />
        </div>
      )}

      {/* Start Modal */}
      {gameState === "start" && (
        <div className="modal-backdrop absolute inset-0 flex flex-col items-center justify-center z-50 p-6" data-testid="start-modal">
          <div className="modal-content text-center">
            <h1 className="font-heading text-4xl md:text-6xl font-black text-glow mb-2 animate-float" style={{ color: "var(--theme-primary)" }}>
              {t.title}
            </h1>
            <p className="font-mono text-xs md:text-sm opacity-70 mb-8 tracking-widest">{t.subtitle}</p>
            
            {/* Level Selector */}
            <div className="level-selector mb-8 mx-auto" style={{ width: "fit-content" }}>
              <button 
                className="level-btn"
                onClick={() => setLevel(Math.max(1, level - 1))}
                disabled={level <= 1}
              >
                <ChevronDown size={18} />
              </button>
              <div className="text-center">
                <span className="font-heading text-3xl font-black" style={{ color: "var(--theme-primary)" }}>
                  {level}
                </span>
                <p className="text-xs opacity-60 uppercase">{t.level}</p>
              </div>
              <button 
                className="level-btn"
                onClick={() => setLevel(Math.min(maxUnlockedLevel, level + 1))}
                disabled={level >= maxUnlockedLevel}
              >
                <ChevronUp size={18} />
              </button>
            </div>

            <button
              className="btn-game btn-primary text-base md:text-lg px-8 md:px-10 py-4"
              onClick={startGame}
              data-testid="start-button"
            >
              <Play size={24} />
              {t.enterStadium}
            </button>
            
            <div className="flex justify-center gap-4 mt-6">
              <button className="btn-icon" onClick={toggleLang} data-testid="lang-toggle-start">
                <span className="text-xl">{languageFlags[lang]}</span>
              </button>
              <button className="btn-icon" onClick={toggleTheme} data-testid="theme-toggle-start">
                <span className="text-xl">{themeIcons[theme]}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Game UI - Adaptive Layout */}
      {gameState === "playing" && (
        <div className={`game-container flex h-full ${isLandscapeMobile ? "flex-row" : "flex-col"}`}>
          {isLandscapeMobile ? (
            // Landscape mobile layout - sidebar on left
            <>
              <div className="w-40 flex-shrink-0 flex flex-col justify-between p-2 glass">
                {/* Top controls */}
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between items-center">
                    <button className="btn-icon w-10 h-10" onClick={() => setShowExit(true)} data-testid="exit-button">
                      <X size={16} />
                    </button>
                    <button className="btn-icon w-10 h-10" onClick={() => setShowSettings(true)} data-testid="settings-button">
                      <Settings size={16} />
                    </button>
                  </div>
                  
                  <div className={`font-mono text-lg font-black text-center ${timeLeft <= 10 ? "timer-critical" : timeLeft <= 30 ? "timer-warning" : ""}`}
                    style={{ color: timeLeft <= 30 ? undefined : "var(--theme-primary)" }}
                    data-testid="timer-display">
                    ⏱️ {formatTime(timeLeft)}
                  </div>
                  
                  <div className={`font-mono text-base font-black text-center ${scoreAnimating ? "score-pop" : ""}`} 
                    style={{ color: "var(--theme-primary)" }} 
                    data-testid="score-display">
                    ⭐ {score}
                  </div>
                </div>
                
                {/* Word bank vertical */}
                <div className="flex flex-col gap-1 my-2 overflow-y-auto flex-1">
                  {words.map((w) => (
                    <span
                      key={w.word}
                      className={`word-tag text-center text-xs py-1 px-2 ${foundWords.some((fw) => fw.word === w.word) ? "found" : ""}`}
                    >
                      {w.word}
                    </span>
                  ))}
                </div>
                
                {/* Controls vertical */}
                <div className="flex flex-col gap-2">
                  <button
                    className={`btn-game btn-primary py-2 px-3 text-xs ${aiLoading ? "ai-thinking" : ""}`}
                    onClick={useAIHint}
                    disabled={score < 100 || aiLoading}
                    style={{ opacity: score < 100 ? 0.5 : 1 }}
                    data-testid="hint-button"
                  >
                    <Sparkles size={14} />
                    {t.hint}
                  </button>
                  <button className="btn-game btn-danger py-2 px-3 text-xs" onClick={clearSelection} data-testid="clear-button">
                    <RotateCcw size={14} />
                    {t.clear}
                  </button>
                </div>
              </div>
              
              <div className="flex-1 flex items-center justify-center p-2 overflow-hidden">
                {renderGameGrid()}
              </div>
            </>
          ) : (
            // Portrait / Desktop layout
            <>
              {/* Top Bar */}
              <div className="top-bar flex items-center justify-between p-3 md:p-4 pt-5 md:pt-6 glass" data-testid="top-bar">
                <button className="btn-icon" onClick={() => setShowExit(true)} data-testid="exit-button">
                  <X size={18} />
                </button>
                
                <div
                  className={`font-mono text-xl md:text-2xl font-black ${timeLeft <= 10 ? "timer-critical" : timeLeft <= 30 ? "timer-warning" : ""}`}
                  style={{ color: timeLeft <= 30 ? undefined : "var(--theme-primary)" }}
                  data-testid="timer-display"
                >
                  ⏱️ {formatTime(timeLeft)}
                </div>
                
                {/* Level selector in game */}
                <button 
                  className="btn-icon text-sm font-bold"
                  onClick={() => setShowLevelSelect(true)}
                  data-testid="level-selector"
                >
                  L{level}
                </button>
                
                <button className="btn-icon" onClick={() => setShowSettings(true)} data-testid="settings-button">
                  <Settings size={18} />
                </button>
                
                <div className={`font-mono text-lg md:text-xl font-black ${scoreAnimating ? "score-pop" : ""}`} 
                  style={{ color: "var(--theme-primary)" }} 
                  data-testid="score-display">
                  ⭐ {score}
                </div>
              </div>

              {/* Selection Preview */}
              <div className="h-10 md:h-12 flex items-center justify-center glass-light" data-testid="selection-preview">
                <span className="selection-preview">
                  {selectionText || t.tap}
                </span>
              </div>

              {/* Knowledge Banner / AI Hint */}
              <div className="knowledge-banner mx-3 md:mx-4 my-2 p-3 md:p-4 rounded-2xl text-center" data-testid="knowledge-banner">
                <p className="text-xs md:text-sm text-white/90 relative z-10">
                  {aiHint || knowledgeText}
                </p>
              </div>

              {/* Game Grid */}
              <div className="flex-1 flex items-center justify-center p-3 md:p-4 overflow-hidden">
                {renderGameGrid()}
              </div>

              {/* Word Bank */}
              {renderWordBank()}

              {/* Bottom Controls */}
              {renderControls()}
            </>
          )}
        </div>
      )}

      {/* Win Modal */}
      {gameState === "win" && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6 bg-black/85" data-testid="win-modal">
          <div className="modal-content-bounce glass-strong rounded-3xl p-6 md:p-8 max-w-sm w-full text-center">
            <img
              src="https://static.prod-images.emergentagent.com/jobs/ce42bd3d-1e24-4f1c-a96b-aa9453dd1466/images/b7ec88058f6553222083ce9031d5058210508bbfd784ae36d72bc0b5ea8c2333.png"
              alt="Trophy"
              className="w-24 h-24 md:w-32 md:h-32 mx-auto mb-4 trophy-animate glow-primary"
            />
            <h2 className="font-heading text-3xl md:text-4xl font-black mb-2" style={{ color: "var(--theme-success)" }}>
              {t.goal}
            </h2>
            <p className="text-base md:text-lg mb-4 opacity-80">{t.levelComplete}</p>
            
            <div className="flex justify-center gap-6 my-6">
              <div>
                <p className="text-2xl md:text-3xl font-black" style={{ color: "var(--theme-primary)" }}>{score}</p>
                <p className="text-xs opacity-70 uppercase">{t.score}</p>
              </div>
              <div>
                <p className="text-2xl md:text-3xl font-black" style={{ color: "var(--theme-accent)" }}>{level}</p>
                <p className="text-xs opacity-70 uppercase">{t.level}</p>
              </div>
              <div>
                <p className="text-2xl md:text-3xl font-black" style={{ color: "var(--theme-success)" }}>{foundWords.length}</p>
                <p className="text-xs opacity-70 uppercase">{t.wordsFound}</p>
              </div>
            </div>
            
            <div className="flex flex-col gap-3">
              <button className="btn-game btn-primary w-full" onClick={nextLevel} data-testid="next-level-button">
                <Zap size={18} />
                {t.next}
              </button>
              <button className="share-btn w-full justify-center" onClick={handleShare} data-testid="share-button">
                <Share2 size={18} />
                {copied ? t.copied : t.share}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Lose Modal */}
      {gameState === "lose" && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6 bg-black/85" data-testid="lose-modal">
          <div className="modal-content glass-strong rounded-3xl p-6 md:p-8 max-w-sm w-full text-center">
            <h2 className="font-heading text-3xl md:text-4xl font-black mb-4" style={{ color: "var(--theme-error)" }}>
              {t.timeUp}
            </h2>
            <div className="flex justify-center gap-6 my-6">
              <div>
                <p className="text-2xl md:text-3xl font-black" style={{ color: "var(--theme-primary)" }}>{score}</p>
                <p className="text-xs opacity-70 uppercase">{t.score}</p>
              </div>
              <div>
                <p className="text-2xl md:text-3xl font-black" style={{ color: "var(--theme-accent)" }}>{foundWords.length}/{words.length}</p>
                <p className="text-xs opacity-70 uppercase">{t.wordsFound}</p>
              </div>
            </div>
            <div className="flex flex-col gap-3">
              <button className="btn-game btn-primary w-full" onClick={() => loadGame(level)} data-testid="retry-button">
                <RotateCcw size={18} />
                {t.playAgain}
              </button>
              <button className="share-btn w-full justify-center" onClick={handleShare} data-testid="share-lose-button">
                <Share2 size={18} />
                {copied ? t.copied : t.share}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6 bg-black/90" data-testid="settings-modal">
          <div className="modal-content glass-strong rounded-3xl p-5 md:p-6 max-w-sm w-full">
            <h2 className="font-heading text-xl md:text-2xl font-bold mb-6 text-center" style={{ color: "var(--theme-primary)" }}>
              {t.settings}
            </h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span className="flex items-center gap-2">
                  <Volume2 size={18} />
                  {t.volume}
                </span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={(e) => setVolume(parseFloat(e.target.value))}
                  className="w-24 accent-cyan-400"
                  data-testid="volume-slider"
                />
              </div>
              
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span className="flex items-center gap-2">
                  <Globe size={18} />
                  {t.language}
                </span>
                <button
                  className="btn-icon text-2xl"
                  onClick={toggleLang}
                  data-testid="language-toggle"
                >
                  {languageFlags[lang]}
                </button>
              </div>
              
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span className="flex items-center gap-2">
                  <Palette size={18} />
                  {t.theme}
                </span>
                <button
                  className="btn-icon px-4 w-auto rounded-xl text-sm font-bold uppercase"
                  onClick={toggleTheme}
                  data-testid="theme-toggle"
                >
                  {themeIcons[theme]} {theme}
                </button>
              </div>
              
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span className="flex items-center gap-2">
                  <Smartphone size={18} />
                  {t.vibration}
                </span>
                <button
                  className={`btn-icon px-4 w-auto rounded-xl text-sm font-bold transition-colors ${vibration ? "bg-green-500/30 border-green-500" : ""}`}
                  onClick={() => setVibration(!vibration)}
                  data-testid="vibration-toggle"
                >
                  {vibration ? t.on : t.off}
                </button>
              </div>
            </div>
            
            <button
              className="btn-game btn-primary w-full mt-6"
              onClick={() => setShowSettings(false)}
              data-testid="save-settings-button"
            >
              {t.save}
            </button>
          </div>
        </div>
      )}

      {/* Level Select Modal */}
      {showLevelSelect && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6 bg-black/90" data-testid="level-select-modal">
          <div className="modal-content glass-strong rounded-3xl p-5 md:p-6 max-w-sm w-full">
            <h2 className="font-heading text-xl md:text-2xl font-bold mb-6 text-center" style={{ color: "var(--theme-primary)" }}>
              {t.levelSelect}
            </h2>
            
            <div className="grid grid-cols-5 gap-3">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((lvl) => (
                <button
                  key={lvl}
                  className={`level-btn w-full aspect-square text-lg ${lvl === level ? "bg-cyan-500 text-black" : ""} ${lvl > maxUnlockedLevel ? "opacity-30" : ""}`}
                  onClick={() => selectLevel(lvl)}
                  disabled={lvl > maxUnlockedLevel}
                  data-testid={`level-btn-${lvl}`}
                >
                  {lvl <= maxUnlockedLevel ? lvl : "🔒"}
                </button>
              ))}
            </div>
            
            <button
              className="btn-game btn-danger w-full mt-6"
              onClick={() => setShowLevelSelect(false)}
              data-testid="close-level-select"
            >
              <X size={18} />
            </button>
          </div>
        </div>
      )}

      {/* Exit Confirmation Modal */}
      {showExit && (
        <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4 md:p-6 bg-black/95" data-testid="exit-modal">
          <div className="modal-content glass-strong rounded-3xl p-5 md:p-6 max-w-sm w-full text-center">
            <h2 className="font-heading text-lg md:text-xl font-bold mb-6">{t.exit}</h2>
            <div className="flex gap-4 justify-center">
              <button
                className="btn-game btn-danger"
                onClick={resetGame}
                data-testid="confirm-exit-button"
              >
                {t.yes}
              </button>
              <button
                className="btn-game btn-primary"
                onClick={() => setShowExit(false)}
                data-testid="cancel-exit-button"
              >
                {t.no}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
