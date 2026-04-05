// Achievement and Statistics Management System

export const initializePlayerStats = () => {
  const defaultStats = {
    totalWords: 0,
    totalGames: 0,
    totalScore: 0,
    bestScore: 0,
    bestTime: 0,
    categoryWords: {
      philosophy: 0,
      values: 0,
      emotions: 0,
      success: 0,
      strength: 0,
      relationships: 0,
      learning: 0,
      health: 0,
      nature: 0,
      spirituality: 0,
      creativity: 0,
      justice: 0
    },
    languagesPlayed: [],
    levelsCompleted: [],
    gamesWithoutHints: 0,
    currentStreak: 0,
    bestStreak: 0,
    fastestWord: 999,
    unlockedAchievements: [],
    totalXP: 0,
    level: 1
  };

  const saved = localStorage.getItem('playerStats');
  if (!saved) {
    localStorage.setItem('playerStats', JSON.stringify(defaultStats));
    return defaultStats;
  }
  return JSON.parse(saved);
};

export const getPlayerStats = () => {
  const stats = localStorage.getItem('playerStats');
  return stats ? JSON.parse(stats) : initializePlayerStats();
};

export const updatePlayerStats = (updates) => {
  const current = getPlayerStats();
  const updated = { ...current, ...updates };
  
  // Calculate XP and level
  updated.totalXP = updated.totalScore + (updated.totalWords * 50) + (updated.currentStreak * 100);
  updated.level = Math.floor(updated.totalXP / 1000) + 1;
  
  localStorage.setItem('playerStats', JSON.stringify(updated));
  return updated;
};

export const recordWord = (category, language, timeTaken) => {
  const stats = getPlayerStats();
  
  stats.totalWords++;
  stats.categoryWords[category] = (stats.categoryWords[category] || 0) + 1;
  
  if (!stats.languagesPlayed.includes(language)) {
    stats.languagesPlayed.push(language);
  }
  
  if (timeTaken && timeTaken < stats.fastestWord) {
    stats.fastestWord = timeTaken;
  }
  
  return updatePlayerStats(stats);
};

export const recordGameCompletion = (level, score, wordsFound, hintsUsed, timeRemaining, language) => {
  const stats = getPlayerStats();
  
  stats.totalGames++;
  stats.totalScore += score;
  
  if (score > stats.bestScore) {
    stats.bestScore = score;
  }
  
  if (timeRemaining > stats.bestTime) {
    stats.bestTime = timeRemaining;
  }
  
  if (!stats.levelsCompleted.includes(level)) {
    stats.levelsCompleted.push(level);
  }
  
  if (!stats.languagesPlayed.includes(language)) {
    stats.languagesPlayed.push(language);
  }
  
  if (hintsUsed === 0) {
    stats.gamesWithoutHints++;
  }
  
  return updatePlayerStats(stats);
};

export const updateStreak = (isCorrect) => {
  const stats = getPlayerStats();
  
  if (isCorrect) {
    stats.currentStreak++;
    if (stats.currentStreak > stats.bestStreak) {
      stats.bestStreak = stats.currentStreak;
    }
  } else {
    stats.currentStreak = 0;
  }
  
  return updatePlayerStats(stats);
};

export const checkAchievements = (stats, achievements) => {
  const newlyUnlocked = [];
  
  achievements.forEach(achievement => {
    if (stats.unlockedAchievements.includes(achievement.id)) {
      return; // Already unlocked
    }
    
    const req = achievement.requirement;
    let unlocked = false;
    
    switch (req.type) {
      case 'category_words':
        unlocked = (stats.categoryWords[req.category] || 0) >= req.count;
        break;
      case 'time_remaining':
        unlocked = stats.bestTime >= req.seconds;
        break;
      case 'languages_played':
        unlocked = stats.languagesPlayed.length >= req.count;
        break;
      case 'no_hints':
        unlocked = stats.gamesWithoutHints >= req.count;
        break;
      case 'total_words':
        unlocked = stats.totalWords >= req.count;
        break;
      case 'word_speed':
        unlocked = stats.fastestWord <= req.seconds;
        break;
      case 'level_completed':
        unlocked = stats.levelsCompleted.includes(req.level);
        break;
      case 'combo_streak':
        unlocked = stats.bestStreak >= req.count;
        break;
      case 'all_categories':
        const categoriesFound = Object.values(stats.categoryWords).filter(count => count > 0).length;
        unlocked = categoriesFound >= req.count;
        break;
    }
    
    if (unlocked) {
      stats.unlockedAchievements.push(achievement.id);
      newlyUnlocked.push(achievement);
    }
  });
  
  if (newlyUnlocked.length > 0) {
    updatePlayerStats(stats);
  }
  
  return newlyUnlocked;
};

export const exportStatsAsImage = async (stats, playerName) => {
  // This would generate a shareable image with stats
  // For now, we'll return formatted text that can be shared
  const text = `
🎮 ${playerName} - AbdoulGame Stats 🎮
━━━━━━━━━━━━━━━━━━━━
📊 Total Words: ${stats.totalWords}
🎯 Best Score: ${stats.bestScore}
⏱️ Best Time: ${Math.floor(stats.bestTime / 60)}:${(stats.bestTime % 60).toString().padStart(2, '0')}
🔥 Best Streak: ${stats.bestStreak}
⭐ Level: ${stats.level}
🏆 Achievements: ${stats.unlockedAchievements.length}
━━━━━━━━━━━━━━━━━━━━
Play at: ${window.location.origin}
  `.trim();
  
  return text;
};
