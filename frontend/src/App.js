import React, { useState, useEffect, useCallback, useRef } from "react";
import "@/App.css";
import axios from "axios";
import { Settings, Lightbulb, X, Volume2, VolumeX, Trophy, RotateCcw, Play } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    hint: "PISTA",
    clear: "BORRAR",
    next: "SIGUIENTE",
    tap: "Toca una letra",
    goal: "¡GOOOOL!",
    levelComplete: "NIVEL COMPLETADO",
    timeUp: "TIEMPO AGOTADO",
    score: "PUNTOS",
    level: "NIVEL",
    wordsFound: "PALABRAS",
    playAgain: "JUGAR DE NUEVO",
    yes: "SÍ",
    no: "NO",
    on: "ON",
    off: "OFF"
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
    hint: "HINT",
    clear: "CLEAR",
    next: "NEXT",
    tap: "Tap a letter",
    goal: "GOOOAL!",
    levelComplete: "LEVEL COMPLETE",
    timeUp: "TIME'S UP",
    score: "SCORE",
    level: "LEVEL",
    wordsFound: "WORDS",
    playAgain: "PLAY AGAIN",
    yes: "YES",
    no: "NO",
    on: "ON",
    off: "OFF"
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
    hint: "INDICE",
    clear: "EFFACER",
    next: "SUIVANT",
    tap: "Touchez une lettre",
    goal: "BUUUT!",
    levelComplete: "NIVEAU TERMINÉ",
    timeUp: "TEMPS ÉCOULÉ",
    score: "POINTS",
    level: "NIVEAU",
    wordsFound: "MOTS",
    playAgain: "REJOUER",
    yes: "OUI",
    no: "NON",
    on: "ON",
    off: "OFF"
  }
};

const languageFlags = { ES: "🇪🇸", EN: "🇺🇸", FR: "🇫🇷" };
const themes = ["neon", "classic", "gold"];

function App() {
  // Game state
  const [gameState, setGameState] = useState("start"); // start, playing, win, lose
  const [matrix, setMatrix] = useState([]);
  const [words, setWords] = useState([]);
  const [foundWords, setFoundWords] = useState([]);
  const [selection, setSelection] = useState([]);
  const [hintCells, setHintCells] = useState([]);
  const [score, setScore] = useState(0);
  const [level, setLevel] = useState(1);
  const [timeLeft, setTimeLeft] = useState(120);
  const [knowledgeText, setKnowledgeText] = useState("");

  // Settings state
  const [showSettings, setShowSettings] = useState(false);
  const [showExit, setShowExit] = useState(false);
  const [lang, setLang] = useState("ES");
  const [theme, setTheme] = useState("neon");
  const [volume, setVolume] = useState(0.5);
  const [vibration, setVibration] = useState(true);
  const [muted, setMuted] = useState(false);

  // Refs
  const isSwiping = useRef(false);
  const timerRef = useRef(null);
  const audioRef = useRef(null);
  const correctSoundRef = useRef(null);
  const goalSoundRef = useRef(null);

  const t = i18n[lang];

  // Initialize audio
  useEffect(() => {
    audioRef.current = new Audio("https://cdn.pixabay.com/audio/2022/02/22/audio_d0c6ff1101.mp3");
    audioRef.current.loop = true;
    correctSoundRef.current = new Audio("https://assets.mixkit.co/active_storage/sfx/2012/2012-preview.mp3");
    goalSoundRef.current = new Audio("https://www.myinstants.com/media/sounds/gol-de-messi.mp3");
    
    return () => {
      if (audioRef.current) audioRef.current.pause();
    };
  }, []);

  // Update audio volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = muted ? 0 : volume * 0.2;
    }
    if (correctSoundRef.current) {
      correctSoundRef.current.volume = muted ? 0 : volume;
    }
    if (goalSoundRef.current) {
      goalSoundRef.current.volume = muted ? 0 : volume;
    }
  }, [volume, muted]);

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
      if (goalSoundRef.current) goalSoundRef.current.play().catch(() => {});
      triggerConfetti();
    }
  }, [foundWords, words, gameState]);

  const triggerConfetti = () => {
    if (window.confetti) {
      window.confetti({
        particleCount: 200,
        spread: 80,
        origin: { y: 0.6 }
      });
    }
  };

  const loadGame = useCallback(async () => {
    try {
      const response = await axios.post(`${API}/game/generate`, {
        level: level,
        language: lang
      });
      setMatrix(response.data.matrix);
      setWords(response.data.words);
      setFoundWords([]);
      setSelection([]);
      setHintCells([]);
      setTimeLeft(120);
      setKnowledgeText(t.welcome);
      setGameState("playing");
      
      if (audioRef.current) {
        audioRef.current.play().catch(() => {});
      }
    } catch (error) {
      console.error("Error loading game:", error);
    }
  }, [level, lang, t.welcome]);

  const startGame = () => {
    loadGame();
  };

  const nextLevel = () => {
    setLevel((prev) => prev + 1);
    loadGame();
  };

  const resetGame = () => {
    setLevel(1);
    setScore(0);
    setGameState("start");
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
    const key = `${r}-${c}`;
    const isFound = foundWords.some((w) =>
      w.coords.some((coord) => coord.r === r && coord.c === c)
    );
    if (isFound) return;

    const isSelected = selection.some((s) => s.r === r && s.c === c);
    if (!isSelected) {
      if (vibration && navigator.vibrate) navigator.vibrate(15);
      setSelection((prev) => [...prev, { r, c }]);
      checkWord([...selection, { r, c }]);
    }
  };

  const checkWord = (currentSelection) => {
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
      setKnowledgeText("💡 " + foundWord.info);
      if (correctSoundRef.current) correctSoundRef.current.play().catch(() => {});
    }
  };

  const clearSelection = () => {
    setSelection([]);
  };

  const useHint = () => {
    if (score < 100) return;
    const pendingWord = words.find((w) => !foundWords.some((fw) => fw.word === w.word));
    if (pendingWord) {
      setScore((prev) => prev - 100);
      setHintCells(pendingWord.coords.map((c) => `${c.r}-${c.c}`));
      setTimeout(() => setHintCells([]), 2000);
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

  return (
    <div
      className={`theme-${theme} relative w-full h-screen flex flex-col overflow-hidden`}
      style={{
        backgroundImage: `linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.8)), url(https://static.prod-images.emergentagent.com/jobs/ce42bd3d-1e24-4f1c-a96b-aa9453dd1466/images/23855e63fb470783e9c6782789c2475fb72af4df0e0a7a5e68b614a1db5d8f88.png)`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed"
      }}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
    >
      {/* Progress Bar */}
      {gameState === "playing" && (
        <div className="absolute top-0 left-0 w-full h-1.5 bg-white/10 z-50" data-testid="progress-container">
          <div
            className="h-full progress-fill"
            style={{ width: `${progress}%`, background: "linear-gradient(to right, var(--theme-secondary), var(--theme-primary))" }}
            data-testid="progress-bar"
          />
        </div>
      )}

      {/* Start Modal */}
      {gameState === "start" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-50 p-6" data-testid="start-modal">
          <h1 className="font-heading text-5xl md:text-6xl font-black text-glow mb-2" style={{ color: "var(--theme-primary)" }}>
            {t.title}
          </h1>
          <p className="font-mono text-sm opacity-70 mb-12 tracking-widest">{t.subtitle}</p>
          <button
            className="btn-game btn-primary text-lg px-10 py-4"
            onClick={startGame}
            data-testid="start-button"
          >
            <Play size={24} />
            {t.enterStadium}
          </button>
        </div>
      )}

      {/* Game UI */}
      {gameState === "playing" && (
        <>
          {/* Top Bar */}
          <div className="flex items-center justify-between p-4 pt-6 glass" data-testid="top-bar">
            <button className="btn-icon" onClick={() => setShowExit(true)} data-testid="exit-button">
              <X size={20} />
            </button>
            <div
              className={`font-mono text-2xl font-black ${timeLeft <= 10 ? "timer-critical" : ""}`}
              style={{ color: timeLeft <= 30 ? "var(--theme-error)" : "var(--theme-primary)" }}
              data-testid="timer-display"
            >
              ⏱️ {formatTime(timeLeft)}
            </div>
            <button className="btn-icon" onClick={() => setShowSettings(true)} data-testid="settings-button">
              <Settings size={20} />
            </button>
            <div className="font-mono text-xl font-black" style={{ color: "var(--theme-primary)" }} data-testid="score-display">
              ⭐ {score}
            </div>
          </div>

          {/* Selection Preview */}
          <div className="h-10 flex items-center justify-center glass-light" data-testid="selection-preview">
            <span className="selection-preview">
              {selectionText || t.tap}
            </span>
          </div>

          {/* Knowledge Banner */}
          <div className="mx-4 my-2 p-4 rounded-2xl knowledge-banner text-center" data-testid="knowledge-banner">
            <p className="text-sm text-white/90">{knowledgeText}</p>
          </div>

          {/* Game Grid */}
          <div className="flex-1 flex items-center justify-center p-4 overflow-hidden">
            <div
              className="glass-light rounded-2xl p-2 w-full max-w-md"
              style={{
                display: "grid",
                gridTemplateColumns: `repeat(${matrix.length}, 1fr)`,
                gap: "4px"
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
                      data-testid={`grid-cell-${r}-${c}`}
                    >
                      {cell}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Word Bank */}
          <div className="flex flex-wrap gap-2 justify-center px-4 py-2" data-testid="word-bank">
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

          {/* Bottom Controls */}
          <div className="flex items-center justify-center gap-4 p-4 pb-8" data-testid="controls">
            <button
              className="btn-game btn-primary"
              onClick={useHint}
              disabled={score < 100}
              style={{ opacity: score < 100 ? 0.5 : 1 }}
              data-testid="hint-button"
            >
              <Lightbulb size={18} />
              {t.hint}
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
        </>
      )}

      {/* Win Modal */}
      {gameState === "win" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-50 p-6 bg-black/80" data-testid="win-modal">
          <div className="modal-content glass rounded-3xl p-8 max-w-sm w-full text-center">
            <img
              src="https://static.prod-images.emergentagent.com/jobs/ce42bd3d-1e24-4f1c-a96b-aa9453dd1466/images/b7ec88058f6553222083ce9031d5058210508bbfd784ae36d72bc0b5ea8c2333.png"
              alt="Trophy"
              className="w-32 h-32 mx-auto mb-4 glow-primary"
            />
            <h2 className="font-heading text-4xl font-black mb-4" style={{ color: "var(--theme-success)" }}>
              {t.goal}
            </h2>
            <p className="text-lg mb-2">{t.levelComplete}</p>
            <div className="flex justify-center gap-6 my-6">
              <div>
                <p className="text-3xl font-black" style={{ color: "var(--theme-primary)" }}>{score}</p>
                <p className="text-xs opacity-70 uppercase">{t.score}</p>
              </div>
              <div>
                <p className="text-3xl font-black" style={{ color: "var(--theme-accent)" }}>{level}</p>
                <p className="text-xs opacity-70 uppercase">{t.level}</p>
              </div>
            </div>
            <button className="btn-game btn-primary w-full" onClick={nextLevel} data-testid="next-level-button">
              {t.next}
            </button>
          </div>
        </div>
      )}

      {/* Lose Modal */}
      {gameState === "lose" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-50 p-6 bg-black/80" data-testid="lose-modal">
          <div className="modal-content glass rounded-3xl p-8 max-w-sm w-full text-center">
            <h2 className="font-heading text-4xl font-black mb-4" style={{ color: "var(--theme-error)" }}>
              {t.timeUp}
            </h2>
            <div className="flex justify-center gap-6 my-6">
              <div>
                <p className="text-3xl font-black" style={{ color: "var(--theme-primary)" }}>{score}</p>
                <p className="text-xs opacity-70 uppercase">{t.score}</p>
              </div>
              <div>
                <p className="text-3xl font-black" style={{ color: "var(--theme-accent)" }}>{foundWords.length}/{words.length}</p>
                <p className="text-xs opacity-70 uppercase">{t.wordsFound}</p>
              </div>
            </div>
            <button className="btn-game btn-primary w-full" onClick={resetGame} data-testid="play-again-button">
              {t.playAgain}
            </button>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <div className="absolute inset-0 flex items-center justify-center z-50 p-6 bg-black/90" data-testid="settings-modal">
          <div className="modal-content glass rounded-3xl p-6 max-w-sm w-full">
            <h2 className="font-heading text-2xl font-bold mb-6 text-center" style={{ color: "var(--theme-primary)" }}>
              {t.settings}
            </h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span>{t.volume}</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={(e) => setVolume(parseFloat(e.target.value))}
                  className="w-24"
                  data-testid="volume-slider"
                />
              </div>
              
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span>{t.language}</span>
                <button
                  className="btn-icon text-2xl"
                  onClick={toggleLang}
                  data-testid="language-toggle"
                >
                  {languageFlags[lang]}
                </button>
              </div>
              
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span>{t.theme}</span>
                <button
                  className="btn-icon px-4 w-auto rounded-xl text-sm font-bold uppercase"
                  onClick={toggleTheme}
                  data-testid="theme-toggle"
                >
                  {theme}
                </button>
              </div>
              
              <div className="flex justify-between items-center py-3 border-b border-white/10">
                <span>{t.vibration}</span>
                <button
                  className={`btn-icon px-4 w-auto rounded-xl text-sm font-bold ${vibration ? "bg-green-500/30" : ""}`}
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

      {/* Exit Confirmation Modal */}
      {showExit && (
        <div className="absolute inset-0 flex items-center justify-center z-50 p-6 bg-black/95" data-testid="exit-modal">
          <div className="modal-content glass rounded-3xl p-6 max-w-sm w-full text-center">
            <h2 className="font-heading text-xl font-bold mb-6">{t.exit}</h2>
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

      {/* Confetti Canvas */}
      <canvas id="confetti-canvas" />
    </div>
  );
}

export default App;
