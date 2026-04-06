/**
 * SISTEMA MAESTRO DE SINCRONIZACIÓN
 * 
 * Coordina todos los efectos del juego para crear una experiencia fluida y moderna
 * - Timing perfecto entre efectos
 * - Sincronización de audio, visuales y vibración
 * - Performance optimizado (GPU acceleration)
 * - Nada exagerado, todo equilibrado
 */

// Duraciones estándar del sistema (en ms)
export const TIMINGS = {
  // Muy rápido
  instant: 100,
  veryFast: 200,
  fast: 300,
  
  // Normal
  normal: 400,
  medium: 600,
  
  // Lento
  slow: 800,
  verySlow: 1000,
  
  // Efectos específicos (optimizados)
  blur: 400,          // Blur de fondo
  particle: 1500,     // Duración de partículas
  confetti: 2000,     // Duración de confetti
  toast: 3000,        // Notificaciones
  hint: 5000,         // Duración de hints
  
  // Intensidades de blur (px)
  blurSubtle: 3,      // Palabra encontrada
  blurMedium: 4,      // Combo
  blurStrong: 5,      // Pista
  blurIntense: 6,     // Victoria
};

// Sistema de vibración coordinado
export const VIBRATIONS = {
  tap: [10],                    // Seleccionar celda
  wordFound: [30, 10, 30],      // Palabra encontrada
  combo: [40, 20, 40, 20, 40],  // Combo
  hint: [50, 30, 50],           // Pista usada
  win: [60, 30, 60, 30, 60],    // Victoria
  error: [20],                  // Error
};

// Ejecutar vibración con fallback
export const triggerVibration = (pattern, enabled = true) => {
  if (!enabled || !navigator.vibrate) return;
  try {
    navigator.vibrate(pattern);
  } catch (e) {
    console.warn('Vibration not supported');
  }
};

// Sistema de coordinación de efectos
export class EffectCoordinator {
  constructor() {
    this.queue = [];
    this.isProcessing = false;
  }
  
  // Ejecutar efecto con timing preciso
  async executeEffect(effect, delay = 0) {
    return new Promise((resolve) => {
      setTimeout(() => {
        try {
          effect();
          resolve();
        } catch (e) {
          console.warn('Effect execution error:', e);
          resolve();
        }
      }, delay);
    });
  }
  
  // Ejecutar múltiples efectos en secuencia
  async executeSequence(effects) {
    for (const { effect, delay } of effects) {
      await this.executeEffect(effect, delay);
    }
  }
  
  // Ejecutar múltiples efectos en paralelo
  executeParallel(effects) {
    effects.forEach(({ effect, delay = 0 }) => {
      this.executeEffect(effect, delay);
    });
  }
}

// Instancia global
export const effectCoordinator = new EffectCoordinator();

// Sistema de transiciones suaves
export const smoothTransition = (element, property, from, to, duration = TIMINGS.normal) => {
  if (!element) return;
  
  element.style.transition = `${property} ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
  element.style[property] = from;
  
  requestAnimationFrame(() => {
    element.style[property] = to;
  });
  
  setTimeout(() => {
    element.style.transition = '';
  }, duration);
};

// Performance optimizado - usar GPU acceleration
export const optimizeForPerformance = (element) => {
  if (!element) return;
  
  element.style.willChange = 'transform, opacity';
  element.style.transform = 'translateZ(0)'; // Force GPU
  
  // Cleanup después de animación
  setTimeout(() => {
    element.style.willChange = 'auto';
  }, 1000);
};

/**
 * MÚSICA DE FONDO ADAPTATIVA
 * 
 * Sistema de música dinámica que cambia según el estado del juego.
 * Requiere archivos de audio (MP3/OGG) que deben subirse al proyecto.
 */

export class AdaptiveMusicSystem {
  constructor() {
    this.audioContext = null;
    this.tracks = {
      ambient: null,      // Música suave de fondo (inicio, menú)
      gameplay: null,     // Música de juego normal
      tension: null,      // Música intensa (tiempo bajo)
      victory: null,      // Música de victoria
      combo: null,        // Stinger para combos
    };
    this.currentTrack = null;
    this.masterVolume = 0.3;
    this.enabled = true;
  }
  
  // Inicializar sistema (llamar al inicio)
  async init() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      console.log('🎵 Adaptive Music System initialized');
    } catch (e) {
      console.warn('Audio Context not supported:', e);
    }
  }
  
  // Cargar pista de audio
  async loadTrack(name, url) {
    if (!this.audioContext) return;
    
    try {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      this.tracks[name] = audioBuffer;
      console.log(`✅ Track loaded: ${name}`);
    } catch (e) {
      console.warn(`Failed to load track ${name}:`, e);
    }
  }
  
  // Reproducir pista con fade in/out
  play(trackName, loop = true, fadeIn = 1000) {
    if (!this.enabled || !this.audioContext || !this.tracks[trackName]) return;
    
    // Fade out current track
    if (this.currentTrack) {
      this.fadeOut(this.currentTrack, 500);
    }
    
    // Create new source
    const source = this.audioContext.createBufferSource();
    source.buffer = this.tracks[trackName];
    source.loop = loop;
    
    const gainNode = this.audioContext.createGain();
    gainNode.gain.value = 0;
    
    source.connect(gainNode);
    gainNode.connect(this.audioContext.destination);
    
    // Fade in
    gainNode.gain.linearRampToValueAtTime(
      this.masterVolume,
      this.audioContext.currentTime + fadeIn / 1000
    );
    
    source.start(0);
    this.currentTrack = { source, gainNode };
  }
  
  // Fade out
  fadeOut(track, duration = 500) {
    if (!track) return;
    
    track.gainNode.gain.linearRampToValueAtTime(
      0,
      this.audioContext.currentTime + duration / 1000
    );
    
    setTimeout(() => {
      track.source.stop();
    }, duration);
  }
  
  // Cambiar música según estado del juego
  updateGameState(state, timeLeft = 999, comboCount = 0) {
    if (!this.enabled) return;
    
    // Lógica adaptativa
    if (state === 'menu') {
      this.play('ambient');
    } else if (state === 'playing') {
      if (timeLeft < 30) {
        this.play('tension'); // Música intensa
      } else {
        this.play('gameplay');
      }
    } else if (state === 'win') {
      this.play('victory', false);
    }
    
    // Stinger para combos altos
    if (comboCount >= 5) {
      this.playStinger('combo');
    }
  }
  
  // Reproducir sonido corto (stinger) sin interrumpir música
  playStinger(name) {
    if (!this.audioContext || !this.tracks[name]) return;
    
    const source = this.audioContext.createBufferSource();
    source.buffer = this.tracks[name];
    
    const gainNode = this.audioContext.createGain();
    gainNode.gain.value = this.masterVolume * 0.8;
    
    source.connect(gainNode);
    gainNode.connect(this.audioContext.destination);
    source.start(0);
  }
  
  // Control de volumen
  setVolume(volume) {
    this.masterVolume = Math.max(0, Math.min(1, volume));
    if (this.currentTrack) {
      this.currentTrack.gainNode.gain.value = this.masterVolume;
    }
  }
  
  // Activar/desactivar
  toggle(enabled) {
    this.enabled = enabled;
    if (!enabled && this.currentTrack) {
      this.fadeOut(this.currentTrack);
      this.currentTrack = null;
    }
  }
}

// Instancia global de música
export const musicSystem = new AdaptiveMusicSystem();

/**
 * GUÍA DE IMPLEMENTACIÓN DE MÚSICA
 * 
 * 1. Conseguir archivos de audio (royalty-free):
 *    - Ambient: Música suave, atmosférica (loop)
 *    - Gameplay: Música energética pero no intensa (loop)
 *    - Tension: Música intensa, urgente (loop)
 *    - Victory: Fanfarria corta de victoria (no loop)
 *    - Combo: Stinger corto (1-2 seg) para celebrar
 * 
 * 2. Formatos recomendados:
 *    - MP3 (mejor compatibilidad)
 *    - OGG (mejor calidad/tamaño)
 *    - Tamaño: 1-3MB por pista
 * 
 * 3. Sitios para música gratis:
 *    - Incompetech.com
 *    - FreeMusicArchive.org
 *    - Bensound.com
 *    - YouTube Audio Library
 * 
 * 4. Implementación en App.js:
 * 
 *    useEffect(() => {
 *      musicSystem.init();
 *      musicSystem.loadTrack('ambient', '/audio/ambient.mp3');
 *      musicSystem.loadTrack('gameplay', '/audio/gameplay.mp3');
 *      musicSystem.loadTrack('tension', '/audio/tension.mp3');
 *      musicSystem.loadTrack('victory', '/audio/victory.mp3');
 *      musicSystem.play('ambient');
 *    }, []);
 * 
 *    // Cambiar música según estado
 *    useEffect(() => {
 *      musicSystem.updateGameState(gameState, timeLeft, comboCount);
 *    }, [gameState, timeLeft, comboCount]);
 * 
 * 5. Características:
 *    - Transiciones suaves (fade in/out)
 *    - Música adaptativa según tiempo/combos
 *    - Volumen controlable
 *    - No interrumpe efectos de sonido
 *    - Performance optimizado
 */
