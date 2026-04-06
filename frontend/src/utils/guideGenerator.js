/**
 * Sistema de Generación Automática de Guía
 * 
 * Este sistema detecta las funcionalidades disponibles en la app
 * y genera dinámicamente las secciones de la guía del juego
 */

export const detectAvailableFeatures = () => {
  const features = {
    basicControls: true, // Siempre disponible
    swipeControl: true,  // Siempre disponible
    hints: true,         // Siempre disponible
    timer: true,         // Siempre disponible
    
    // Detectar nuevas features
    achievements: typeof localStorage !== 'undefined',
    statistics: typeof localStorage !== 'undefined',
    gameModes: true, // Si tenemos los componentes
    combos: true,
    inspirationalQuotes: true,
    darkMode: true,
    themes: true,
    multilanguage: true,
    
    // Features futuras que podríamos agregar
    multiplayer: false,
    voiceControl: false,
    ar: false,
  };
  
  return features;
};

export const generateGuideSections = (features, lang = 'ES') => {
  const sections = [];
  
  // Sección básica - siempre presente
  sections.push({
    id: 'objective',
    icon: '🎯',
    title: {
      ES: 'OBJETIVO',
      EN: 'OBJECTIVE',
      FR: 'OBJECTIF'
    },
    content: {
      ES: 'Encuentra las palabras ocultas antes de que termine el tiempo.',
      EN: 'Find the hidden words before time runs out.',
      FR: 'Trouvez les mots cachés avant la fin du temps.'
    }
  });
  
  // Controles
  sections.push({
    id: 'controls',
    icon: '👆',
    title: {
      ES: 'CONTROLES',
      EN: 'CONTROLS',
      FR: 'CONTRÔLES'
    },
    content: {
      ES: features.swipeControl 
        ? 'TOCAR: Pulsa letra por letra. DESLIZAR: Arrastra el dedo sobre las letras.'
        : 'TOCAR: Pulsa letra por letra para seleccionar.',
      EN: features.swipeControl
        ? 'TAP: Press letter by letter. SWIPE: Drag finger over letters.'
        : 'TAP: Press letter by letter to select.',
      FR: features.swipeControl
        ? 'TOUCHER: Appuyez lettre par lettre. GLISSER: Faites glisser sur les lettres.'
        : 'TOUCHER: Appuyez lettre par lettre pour sélectionner.'
    }
  });
  
  // Features básicas
  const featuresList = [];
  if (features.hints) {
    featuresList.push({
      ES: '💡 PISTA: Ayuda (-100 puntos)',
      EN: '💡 HINT: Helps (-100 points)',
      FR: '💡 INDICE: Aide (-100 points)'
    });
  }
  if (features.timer) {
    featuresList.push({
      ES: '⏱️ TIEMPO: Completa a tiempo',
      EN: '⏱️ TIME: Complete in time',
      FR: '⏱️ TEMPS: Terminez à temps'
    });
  }
  if (features.combos) {
    featuresList.push({
      ES: '🔥 COMBOS: Multiplica puntos',
      EN: '🔥 COMBOS: Multiply points',
      FR: '🔥 COMBOS: Multipliez points'
    });
  }
  
  sections.push({
    id: 'features',
    icon: '⭐',
    title: {
      ES: 'FUNCIONES',
      EN: 'FEATURES',
      FR: 'FONCTIONNALITÉS'
    },
    content: {
      ES: featuresList.map(f => f.ES).join('. '),
      EN: featuresList.map(f => f.EN).join('. '),
      FR: featuresList.map(f => f.FR).join('. ')
    }
  });
  
  // Modos de juego - solo si están disponibles
  if (features.gameModes) {
    sections.push({
      id: 'modes',
      icon: '🎮',
      title: {
        ES: 'MODOS DE JUEGO',
        EN: 'GAME MODES',
        FR: 'MODES DE JEU'
      },
      content: {
        ES: '🎯 NORMAL • 📚 PRÁCTICA • 📅 DIARIO • 🧘 ZEN',
        EN: '🎯 NORMAL • 📚 PRACTICE • 📅 DAILY • 🧘 ZEN',
        FR: '🎯 NORMAL • 📚 PRATIQUE • 📅 QUOTIDIEN • 🧘 ZEN'
      }
    });
  }
  
  // Progresión - solo si hay achievements/stats
  if (features.achievements || features.statistics) {
    sections.push({
      id: 'progress',
      icon: '📈',
      title: {
        ES: 'PROGRESIÓN',
        EN: 'PROGRESSION',
        FR: 'PROGRESSION'
      },
      content: {
        ES: 'Gana XP, sube de nivel y desbloquea logros. Consulta tus estadísticas.',
        EN: 'Earn XP, level up and unlock achievements. Check your statistics.',
        FR: 'Gagnez XP, montez de niveau et débloquez succès. Consultez vos stats.'
      }
    });
  }
  
  // Personalización
  const customizationFeatures = [];
  if (features.darkMode) customizationFeatures.push('🌙/☀️ Modo oscuro/claro');
  if (features.themes) customizationFeatures.push('🎨 Temas');
  if (features.multilanguage) customizationFeatures.push('🌍 3 idiomas');
  
  if (customizationFeatures.length > 0) {
    sections.push({
      id: 'customization',
      icon: '🎨',
      title: {
        ES: 'PERSONALIZACIÓN',
        EN: 'CUSTOMIZATION',
        FR: 'PERSONNALISATION'
      },
      content: {
        ES: customizationFeatures.join(' • '),
        EN: customizationFeatures.join(' • ').replace('Modo', 'Mode').replace('Temas', 'Themes').replace('idiomas', 'languages'),
        FR: customizationFeatures.join(' • ').replace('Modo', 'Mode').replace('Temas', 'Thèmes').replace('idiomas', 'langues')
      }
    });
  }
  
  // Aprendizaje
  sections.push({
    id: 'learning',
    icon: '📚',
    title: {
      ES: 'APRENDIZAJE',
      EN: 'LEARNING',
      FR: 'APPRENTISSAGE'
    },
    content: {
      ES: features.inspirationalQuotes
        ? 'Palabras educativas en 12 categorías con frases inspiradoras de grandes pensadores.'
        : 'Palabras educativas en 12 categorías sobre vida, valores y más.',
      EN: features.inspirationalQuotes
        ? 'Educational words in 12 categories with inspirational quotes from great thinkers.'
        : 'Educational words in 12 categories about life, values and more.',
      FR: features.inspirationalQuotes
        ? 'Mots éducatifs en 12 catégories avec citations inspirantes de grands penseurs.'
        : 'Mots éducatifs en 12 catégories sur vie, valeurs et plus.'
    }
  });
  
  return sections;
};

// Hook para usar en el componente
export const useGuideContent = (lang = 'ES') => {
  const features = detectAvailableFeatures();
  const sections = generateGuideSections(features, lang);
  
  return {
    features,
    sections,
    hasNewFeatures: features.achievements || features.gameModes || features.combos
  };
};
