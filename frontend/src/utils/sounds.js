// Enhanced Sound System - Different sounds per category

const audioContext = typeof window !== 'undefined' ? new (window.AudioContext || window.webkitAudioContext)() : null;

// Sound profiles by category - each has unique frequency signature
const CATEGORY_SOUNDS = {
  philosophy: {
    frequencies: [523.25, 659.25, 783.99], // C, E, G (thoughtful chord)
    type: 'sine',
    duration: 0.4,
    volume: 0.15
  },
  values: {
    frequencies: [440, 554.37, 659.25], // A, C#, E (noble chord)
    type: 'triangle',
    duration: 0.35,
    volume: 0.14
  },
  emotions: {
    frequencies: [392, 493.88, 587.33], // G, B, D (warm chord)
    type: 'sine',
    duration: 0.45,
    volume: 0.16
  },
  success: {
    frequencies: [523.25, 698.46, 830.61], // C, F, G# (triumphant)
    type: 'triangle',
    duration: 0.3,
    volume: 0.17
  },
  strength: {
    frequencies: [329.63, 415.30, 523.25], // E, G#, C (powerful)
    type: 'square',
    duration: 0.35,
    volume: 0.13
  },
  relationships: {
    frequencies: [440, 554.37, 659.25, 783.99], // A, C#, E, G (harmonious)
    type: 'sine',
    duration: 0.5,
    volume: 0.15
  },
  learning: {
    frequencies: [493.88, 587.33, 698.46], // B, D, F (curious)
    type: 'triangle',
    duration: 0.4,
    volume: 0.14
  },
  health: {
    frequencies: [392, 523.25, 659.25], // G, C, E (healing)
    type: 'sine',
    duration: 0.45,
    volume: 0.15
  },
  nature: {
    frequencies: [349.23, 440, 523.25], // F, A, C (organic)
    type: 'triangle',
    duration: 0.5,
    volume: 0.16
  },
  spirituality: {
    frequencies: [261.63, 392, 523.25, 659.25], // C, G, C, E (ethereal)
    type: 'sine',
    duration: 0.6,
    volume: 0.14
  },
  creativity: {
    frequencies: [587.33, 739.99, 880], // D, F#, A (imaginative)
    type: 'sawtooth',
    duration: 0.35,
    volume: 0.13
  },
  justice: {
    frequencies: [329.63, 523.25, 659.25], // E, C, E (balanced)
    type: 'triangle',
    duration: 0.4,
    volume: 0.15
  }
};

export const playCategorySound = (category, muted = false) => {
  if (muted || !audioContext) return;
  
  const soundProfile = CATEGORY_SOUNDS[category] || CATEGORY_SOUNDS.success;
  
  soundProfile.frequencies.forEach((freq, index) => {
    setTimeout(() => {
      try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = freq;
        oscillator.type = soundProfile.type;
        
        gainNode.gain.setValueAtTime(soundProfile.volume, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + soundProfile.duration);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + soundProfile.duration);
      } catch (e) {
        console.warn('Audio playback error:', e);
      }
    }, index * 80);
  });
};

export const playErrorSound = (muted = false) => {
  if (muted || !audioContext) return;
  
  try {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Descending tone for error
    oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.2);
    oscillator.type = 'sawtooth';
    
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.2);
  } catch (e) {
    console.warn('Error sound failed:', e);
  }
};

export const playComboSound = (comboLevel, muted = false) => {
  if (muted || !audioContext) return;
  
  const baseFreq = 523.25; // C5
  const comboFreqs = [
    baseFreq,
    baseFreq * 1.25, // E5
    baseFreq * 1.5,  // G5
    baseFreq * 2     // C6
  ];
  
  comboFreqs.slice(0, Math.min(comboLevel, 4)).forEach((freq, index) => {
    setTimeout(() => {
      try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = freq;
        oscillator.type = 'triangle';
        
        gainNode.gain.setValueAtTime(0.15, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
      } catch (e) {}
    }, index * 60);
  });
};

export const playLevelUpSound = (muted = false) => {
  if (muted || !audioContext) return;
  
  // Ascending arpeggio
  const frequencies = [261.63, 329.63, 392, 523.25, 659.25];
  
  frequencies.forEach((freq, index) => {
    setTimeout(() => {
      try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = freq;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.12, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.4);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.4);
      } catch (e) {}
    }, index * 100);
  });
};

export const playAchievementSound = (muted = false) => {
  if (muted || !audioContext) return;
  
  // Fanfare
  const pattern = [
    { freq: 523.25, duration: 0.15, delay: 0 },
    { freq: 659.25, duration: 0.15, delay: 0.15 },
    { freq: 783.99, duration: 0.2, delay: 0.3 },
    { freq: 1046.5, duration: 0.4, delay: 0.5 }
  ];
  
  pattern.forEach(note => {
    setTimeout(() => {
      try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = note.freq;
        oscillator.type = 'triangle';
        
        gainNode.gain.setValueAtTime(0.18, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + note.duration);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + note.duration);
      } catch (e) {}
    }, note.delay * 1000);
  });
};
