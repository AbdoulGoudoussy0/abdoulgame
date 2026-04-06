// Game Helper Utilities

// Undo/Rewind system
export class SelectionHistory {
  constructor(maxHistory = 10) {
    this.history = [];
    this.maxHistory = maxHistory;
  }
  
  push(selection) {
    this.history.push([...selection]);
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
  }
  
  undo() {
    if (this.history.length > 0) {
      this.history.pop(); // Remove current
      return this.history.length > 0 ? [...this.history[this.history.length - 1]] : [];
    }
    return [];
  }
  
  clear() {
    this.history = [];
  }
  
  canUndo() {
    return this.history.length > 0;
  }
}

// Word prediction while swiping
export const predictWord = (currentSelection, matrix, words) => {
  if (currentSelection.length < 2) return null;
  
  const currentWord = currentSelection.map(s => matrix[s.r][s.c]).join('');
  
  // Find words that start with current selection
  const matches = words.filter(w => 
    w.word.startsWith(currentWord) || 
    w.word.split('').reverse().join('').startsWith(currentWord)
  );
  
  if (matches.length === 1) {
    return {
      word: matches[0].word,
      confidence: currentWord.length / matches[0].word.length,
      remaining: matches[0].word.length - currentWord.length
    };
  }
  
  return matches.length > 0 ? { possibleWords: matches.length } : null;
};

// Calculate score multiplier based on performance
export const calculateScoreMultiplier = (timeLeft, timeLimit, comboCount, hintsUsed) => {
  let multiplier = 1.0;
  
  // Time bonus (up to 1.5x)
  const timeRatio = timeLeft / timeLimit;
  if (timeRatio > 0.75) multiplier += 0.5;
  else if (timeRatio > 0.5) multiplier += 0.3;
  else if (timeRatio > 0.25) multiplier += 0.1;
  
  // Combo bonus (up to 2x)
  if (comboCount >= 10) multiplier += 1.0;
  else if (comboCount >= 5) multiplier += 0.5;
  else if (comboCount >= 3) multiplier += 0.3;
  
  // No hints bonus
  if (hintsUsed === 0) multiplier += 0.5;
  
  return Math.round(multiplier * 10) / 10; // Round to 1 decimal
};

// Generate motivational message based on progress
export const getMotivationalMessage = (wordsFound, totalWords, timeLeft, lang = 'ES') => {
  const progress = wordsFound / totalWords;
  const messages = {
    ES: {
      start: ['¡Vamos! Tú puedes hacerlo', '¡A por todas!', '¡Demuestra tu habilidad!'],
      low: ['¡No te rindas!', '¡Sigue intentando!', '¡Cada palabra cuenta!'],
      medium: ['¡Buen trabajo!', '¡Vas por buen camino!', '¡Excelente progreso!'],
      high: ['¡Casi lo logras!', '¡Un último esfuerzo!', '¡Ya casi está!'],
      urgent: ['¡Rápido, el tiempo corre!', '¡Date prisa!', '¡Últimos segundos!']
    },
    EN: {
      start: ["Let's go! You can do it", 'Go for it!', 'Show your skills!'],
      low: ["Don't give up!", 'Keep trying!', 'Every word counts!'],
      medium: ['Good job!', "You're on the right track!", 'Excellent progress!'],
      high: ['Almost there!', 'One last push!', "You're so close!"],
      urgent: ['Quick, time is running out!', 'Hurry up!', 'Last seconds!']
    },
    FR: {
      start: ['Allons-y! Tu peux le faire', 'Vas-y!', 'Montre tes compétences!'],
      low: ['N\'abandonne pas!', 'Continue d\'essayer!', 'Chaque mot compte!'],
      medium: ['Bon travail!', 'Tu es sur la bonne voie!', 'Excellent progrès!'],
      high: ['Presque là!', 'Un dernier effort!', 'Tu es si proche!'],
      urgent: ['Vite, le temps passe!', 'Dépêche-toi!', 'Dernières secondes!']
    }
  };
  
  const langMessages = messages[lang] || messages.ES;
  
  if (timeLeft < 30) {
    return langMessages.urgent[Math.floor(Math.random() * langMessages.urgent.length)];
  }
  
  if (progress < 0.25) return langMessages.low[Math.floor(Math.random() * langMessages.low.length)];
  if (progress < 0.5) return langMessages.medium[Math.floor(Math.random() * langMessages.medium.length)];
  if (progress < 0.9) return langMessages.high[Math.floor(Math.random() * langMessages.high.length)];
  
  return langMessages.start[Math.floor(Math.random() * langMessages.start.length)];
};

// Format time with colors
export const getTimeColor = (timeLeft, timeLimit) => {
  const ratio = timeLeft / timeLimit;
  if (ratio > 0.5) return 'success';
  if (ratio > 0.25) return 'warning';
  return 'error';
};

// Calculate difficulty rating for a level
export const getDifficultyRating = (level) => {
  if (level <= 3) return { rating: 'Fácil', color: '#22C55E', stars: 1 };
  if (level <= 6) return { rating: 'Medio', color: '#F59E0B', stars: 2 };
  if (level <= 8) return { rating: 'Difícil', color: '#EF4444', stars: 3 };
  return { rating: 'Experto', color: '#8B5CF6', stars: 4 };
};

// Local storage helpers with compression
export const saveToStorage = (key, data) => {
  try {
    const compressed = JSON.stringify(data);
    localStorage.setItem(key, compressed);
    return true;
  } catch (e) {
    console.warn('Storage save failed:', e);
    return false;
  }
};

export const loadFromStorage = (key, defaultValue = null) => {
  try {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : defaultValue;
  } catch (e) {
    console.warn('Storage load failed:', e);
    return defaultValue;
  }
};

// Check if first time player
export const isFirstTimePlayer = () => {
  return !localStorage.getItem('hasPlayedBefore');
};

export const markAsPlayed = () => {
  localStorage.setItem('hasPlayedBefore', 'true');
};

// Performance monitoring
export class PerformanceTracker {
  constructor() {
    this.wordTimes = [];
    this.startTime = null;
  }
  
  startWord() {
    this.startTime = Date.now();
  }
  
  endWord() {
    if (this.startTime) {
      const duration = (Date.now() - this.startTime) / 1000;
      this.wordTimes.push(duration);
      this.startTime = null;
      return duration;
    }
    return 0;
  }
  
  getAverageTime() {
    if (this.wordTimes.length === 0) return 0;
    return this.wordTimes.reduce((a, b) => a + b, 0) / this.wordTimes.length;
  }
  
  getFastestTime() {
    return this.wordTimes.length > 0 ? Math.min(...this.wordTimes) : 0;
  }
  
  reset() {
    this.wordTimes = [];
    this.startTime = null;
  }
}

// Validate word selection path (must be continuous)
export const isValidPath = (selection) => {
  if (selection.length < 2) return true;
  
  for (let i = 1; i < selection.length; i++) {
    const prev = selection[i - 1];
    const curr = selection[i];
    
    const rowDiff = Math.abs(curr.r - prev.r);
    const colDiff = Math.abs(curr.c - prev.c);
    
    // Cells must be adjacent (including diagonals)
    if (rowDiff > 1 || colDiff > 1) return false;
    if (rowDiff === 0 && colDiff === 0) return false; // Same cell
  }
  
  return true;
};
