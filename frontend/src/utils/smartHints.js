// Smart Contextual Hints System

export const generateSmartHint = (word, foundLetters, category, language) => {
  const hints = {
    ES: {
      // Hints by category
      philosophy: [
        `🧠 Esta palabra sobre ${category} tiene ${word.length} letras`,
        `💭 Busca un concepto filosófico que empiece con "${word[0]}"`,
        `📖 Los antiguos griegos valoraban mucho esta palabra`
      ],
      values: [
        `💎 Un valor esencial que empieza con "${word[0]}"`,
        `⚖️ Esta palabra define la integridad moral`,
        `🌟 Busca una virtud fundamental de ${word.length} letras`
      ],
      emotions: [
        `❤️ Un sentimiento poderoso con ${word.length} letras`,
        `😊 Esta emoción hace vibrar el corazón`,
        `💫 Empieza con "${word[0]}" y llena el alma`
      ],
      success: [
        `⭐ La clave del éxito está en esta palabra de ${word.length} letras`,
        `🎯 Busca lo que necesitas para alcanzar tus metas`,
        `🏆 Esta palabra impulsa a los campeones`
      ],
      strength: [
        `💪 Una cualidad de los fuertes: ${word.length} letras`,
        `🦁 Esta palabra representa poder interior`,
        `⚡ Empieza con "${word[0]}" y fortalece el espíritu`
      ],
      relationships: [
        `🤝 Lo que une a las personas: ${word.length} letras`,
        `👨‍👩‍👧‍👦 Busca un concepto sobre conexiones humanas`,
        `💞 Esta palabra fortalece los lazos`
      ],
      learning: [
        `📚 La base del aprendizaje: ${word.length} letras`,
        `🎓 Esta palabra abre las puertas del conocimiento`,
        `🔍 Busca lo que impulsa a descubrir`
      ],
      health: [
        `💚 Esencial para el bienestar: ${word.length} letras`,
        `🧘 Esta palabra representa armonía vital`,
        `🌱 Busca equilibrio y salud`
      ],
      nature: [
        `🌿 Un concepto de la naturaleza: ${word.length} letras`,
        `🌍 Esta palabra nos conecta con lo esencial`,
        `⏰ Busca algo que fluye eternamente`
      ],
      spirituality: [
        `✨ Un concepto espiritual de ${word.length} letras`,
        `🙏 Esta palabra eleva el alma`,
        `💫 Busca luz interior`
      ],
      creativity: [
        `🎨 La esencia de la creación: ${word.length} letras`,
        `💡 Esta palabra despierta la imaginación`,
        `🎭 Busca expresión única`
      ],
      justice: [
        `⚖️ Un principio de justicia: ${word.length} letras`,
        `🗽 Esta palabra defiende derechos`,
        `👥 Busca equidad y balance`
      ]
    },
    EN: {
      philosophy: [
        `🧠 This word about ${category} has ${word.length} letters`,
        `💭 Look for a philosophical concept starting with "${word[0]}"`,
        `📖 Ancient Greeks valued this word greatly`
      ],
      values: [
        `💎 An essential value starting with "${word[0]}"`,
        `⚖️ This word defines moral integrity`,
        `🌟 Look for a fundamental virtue of ${word.length} letters`
      ],
      emotions: [
        `❤️ A powerful feeling with ${word.length} letters`,
        `😊 This emotion makes the heart vibrate`,
        `💫 Starts with "${word[0]}" and fills the soul`
      ],
      success: [
        `⭐ The key to success is in this ${word.length}-letter word`,
        `🎯 Look for what you need to achieve your goals`,
        `🏆 This word drives champions`
      ],
      strength: [
        `💪 A quality of the strong: ${word.length} letters`,
        `🦁 This word represents inner power`,
        `⚡ Starts with "${word[0]}" and strengthens the spirit`
      ],
      relationships: [
        `🤝 What unites people: ${word.length} letters`,
        `👨‍👩‍👧‍👦 Look for a concept about human connections`,
        `💞 This word strengthens bonds`
      ],
      learning: [
        `📚 The basis of learning: ${word.length} letters`,
        `🎓 This word opens the doors of knowledge`,
        `🔍 Look for what drives discovery`
      ],
      health: [
        `💚 Essential for wellbeing: ${word.length} letters`,
        `🧘 This word represents vital harmony`,
        `🌱 Look for balance and health`
      ],
      nature: [
        `🌿 A concept from nature: ${word.length} letters`,
        `🌍 This word connects us with the essential`,
        `⏰ Look for something that flows eternally`
      ],
      spirituality: [
        `✨ A spiritual concept of ${word.length} letters`,
        `🙏 This word elevates the soul`,
        `💫 Look for inner light`
      ],
      creativity: [
        `🎨 The essence of creation: ${word.length} letters`,
        `💡 This word awakens imagination`,
        `🎭 Look for unique expression`
      ],
      justice: [
        `⚖️ A principle of justice: ${word.length} letters`,
        `🗽 This word defends rights`,
        `👥 Look for equity and balance`
      ]
    },
    FR: {
      philosophy: [
        `🧠 Ce mot sur ${category} a ${word.length} lettres`,
        `💭 Cherchez un concept philosophique commençant par "${word[0]}"`,
        `📖 Les anciens Grecs valorisaient beaucoup ce mot`
      ],
      values: [
        `💎 Une valeur essentielle commençant par "${word[0]}"`,
        `⚖️ Ce mot définit l'intégrité morale`,
        `🌟 Cherchez une vertu fondamentale de ${word.length} lettres`
      ],
      emotions: [
        `❤️ Un sentiment puissant avec ${word.length} lettres`,
        `😊 Cette émotion fait vibrer le cœur`,
        `💫 Commence par "${word[0]}" et remplit l'âme`
      ],
      success: [
        `⭐ La clé du succès est dans ce mot de ${word.length} lettres`,
        `🎯 Cherchez ce dont vous avez besoin pour atteindre vos objectifs`,
        `🏆 Ce mot propulse les champions`
      ],
      strength: [
        `💪 Une qualité des forts: ${word.length} lettres`,
        `🦁 Ce mot représente la puissance intérieure`,
        `⚡ Commence par "${word[0]}" et renforce l'esprit`
      ],
      relationships: [
        `🤝 Ce qui unit les gens: ${word.length} lettres`,
        `👨‍👩‍👧‍👦 Cherchez un concept sur les connexions humaines`,
        `💞 Ce mot renforce les liens`
      ],
      learning: [
        `📚 La base de l'apprentissage: ${word.length} lettres`,
        `🎓 Ce mot ouvre les portes de la connaissance`,
        `🔍 Cherchez ce qui pousse à découvrir`
      ],
      health: [
        `💚 Essentiel pour le bien-être: ${word.length} lettres`,
        `🧘 Ce mot représente l'harmonie vitale`,
        `🌱 Cherchez équilibre et santé`
      ],
      nature: [
        `🌿 Un concept de la nature: ${word.length} lettres`,
        `🌍 Ce mot nous connecte à l'essentiel`,
        `⏰ Cherchez quelque chose qui coule éternellement`
      ],
      spirituality: [
        `✨ Un concept spirituel de ${word.length} lettres`,
        `🙏 Ce mot élève l'âme`,
        `💫 Cherchez lumière intérieure`
      ],
      creativity: [
        `🎨 L'essence de la création: ${word.length} lettres`,
        `💡 Ce mot réveille l'imagination`,
        `🎭 Cherchez expression unique`
      ],
      justice: [
        `⚖️ Un principe de justice: ${word.length} lettres`,
        `🗽 Ce mot défend les droits`,
        `👥 Cherchez équité et équilibre`
      ]
    }
  };

  const categoryHints = hints[language]?.[category] || hints[language]?.success || hints.ES.success;
  
  // Select random hint from category
  const randomHint = categoryHints[Math.floor(Math.random() * categoryHints.length)];
  
  // Add position hint if some letters are found
  if (foundLetters && foundLetters.length > 0) {
    const positionHint = {
      ES: ` Algunas letras ya están reveladas.`,
      EN: ` Some letters are already revealed.`,
      FR: ` Certaines lettres sont déjà révélées.`
    };
    return randomHint + positionHint[language];
  }
  
  return randomHint;
};

// Visual hint system - highlights general area without giving exact position
export const generateVisualHint = (wordCoords, gridSize) => {
  // Determine the quadrant or region where the word is
  const avgRow = wordCoords.reduce((sum, coord) => sum + coord.r, 0) / wordCoords.length;
  const avgCol = wordCoords.reduce((sum, coord) => sum + coord.c, 0) / wordCoords.length;
  
  const midRow = gridSize / 2;
  const midCol = gridSize / 2;
  
  // Return general region hints (not exact cells)
  const region = {
    vertical: avgRow < midRow ? 'top' : 'bottom',
    horizontal: avgCol < midCol ? 'left' : 'right'
  };
  
  return {
    region,
    message: {
      ES: `💡 Busca en la zona ${region.vertical === 'top' ? 'superior' : 'inferior'}-${region.horizontal === 'left' ? 'izquierda' : 'derecha'}`,
      EN: `💡 Look in the ${region.vertical}-${region.horizontal} area`,
      FR: `💡 Cherchez dans la zone ${region.vertical === 'top' ? 'supérieure' : 'inférieure'}-${region.horizontal === 'left' ? 'gauche' : 'droite'}`
    }
  };
};
