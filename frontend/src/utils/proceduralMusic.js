/**
 * SISTEMA DE MÚSICA PROCEDURAL
 * Genera música en tiempo real usando Web Audio API
 * No requiere archivos - todo generado por código
 */

class ProceduralMusicEngine {
  constructor() {
    this.audioContext = null;
    this.masterGain = null;
    this.isPlaying = false;
    this.currentOscillators = [];
    this.enabled = true;
    this.volume = 0.15; // Muy sutil
  }

  init() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.masterGain = this.audioContext.createGain();
      this.masterGain.gain.value = this.volume;
      this.masterGain.connect(this.audioContext.destination);
      console.log('🎵 Procedural Music Engine initialized');
    } catch (e) {
      console.warn('Audio Context not supported');
    }
  }

  // Crear tono con envolvente (ADSR)
  createTone(frequency, duration, type = 'sine', volume = 0.3) {
    if (!this.audioContext || !this.enabled) return null;

    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();
    
    oscillator.type = type;
    oscillator.frequency.value = frequency;
    
    // ADSR envelope (Attack, Decay, Sustain, Release)
    const now = this.audioContext.currentTime;
    const attack = 0.1;
    const decay = 0.1;
    const sustain = volume * 0.7;
    const release = 0.3;
    
    gainNode.gain.setValueAtTime(0, now);
    gainNode.gain.linearRampToValueAtTime(volume, now + attack);
    gainNode.gain.linearRampToValueAtTime(sustain, now + attack + decay);
    gainNode.gain.setValueAtTime(sustain, now + duration - release);
    gainNode.gain.linearRampToValueAtTime(0, now + duration);
    
    oscillator.connect(gainNode);
    gainNode.connect(this.masterGain);
    
    oscillator.start(now);
    oscillator.stop(now + duration);
    
    return { oscillator, gainNode };
  }

  // Música ambiente (acordes suaves)
  playAmbient() {
    if (!this.enabled) return;
    this.stopAll();
    
    // Acorde Am7 (La menor séptima) - muy relajante
    const chordNotes = [
      { freq: 220, type: 'sine' },    // A
      { freq: 261.63, type: 'sine' }, // C
      { freq: 329.63, type: 'sine' }, // E
      { freq: 392, type: 'sine' }     // G
    ];
    
    const playChord = () => {
      if (!this.enabled) return;
      
      chordNotes.forEach((note, i) => {
        setTimeout(() => {
          const tone = this.createTone(note.freq, 4, note.type, 0.08);
          if (tone) this.currentOscillators.push(tone);
        }, i * 200); // Arpeggio
      });
      
      // Repetir cada 8 segundos
      if (this.enabled) {
        setTimeout(playChord, 8000);
      }
    };
    
    playChord();
    this.isPlaying = true;
  }

  // Música de juego (más energética)
  playGameplay() {
    if (!this.enabled) return;
    this.stopAll();
    
    const melodyNotes = [
      { freq: 523.25, duration: 0.4 }, // C5
      { freq: 587.33, duration: 0.4 }, // D5
      { freq: 659.25, duration: 0.4 }, // E5
      { freq: 523.25, duration: 0.4 }, // C5
      { freq: 659.25, duration: 0.6 }, // E5
      { freq: 587.33, duration: 0.6 }, // D5
    ];
    
    const playMelody = (offset = 0) => {
      if (!this.enabled) return;
      
      melodyNotes.forEach((note, i) => {
        setTimeout(() => {
          const tone = this.createTone(note.freq, note.duration, 'triangle', 0.12);
          if (tone) this.currentOscillators.push(tone);
        }, offset + i * 500);
      });
      
      // Repetir
      if (this.enabled) {
        setTimeout(() => playMelody(0), 4000);
      }
    };
    
    playMelody();
    this.isPlaying = true;
  }

  // Música de tensión (urgente)
  playTension() {
    if (!this.enabled) return;
    this.stopAll();
    
    const playPulse = () => {
      if (!this.enabled) return;
      
      // Pulso rápido y bajo
      this.createTone(110, 0.15, 'sawtooth', 0.15); // A2
      
      setTimeout(() => {
        this.createTone(130.81, 0.15, 'sawtooth', 0.15); // C3
      }, 150);
      
      setTimeout(playPulse, 300);
    };
    
    playPulse();
    this.isPlaying = true;
  }

  // Fanfarria de victoria
  playVictory() {
    if (!this.enabled) return;
    
    const victoryMelody = [
      { freq: 523.25, duration: 0.3, delay: 0 },     // C5
      { freq: 659.25, duration: 0.3, delay: 300 },   // E5
      { freq: 783.99, duration: 0.3, delay: 600 },   // G5
      { freq: 1046.5, duration: 0.6, delay: 900 },   // C6
    ];
    
    victoryMelody.forEach(note => {
      setTimeout(() => {
        this.createTone(note.freq, note.duration, 'triangle', 0.2);
      }, note.delay);
    });
  }

  // Stinger de combo
  playComboStinger() {
    if (!this.enabled) return;
    
    // Ascenso rápido
    [440, 554.37, 659.25].forEach((freq, i) => {
      setTimeout(() => {
        this.createTone(freq, 0.2, 'square', 0.15);
      }, i * 80);
    });
  }

  // Detener todo
  stopAll() {
    this.currentOscillators.forEach(({ oscillator }) => {
      try {
        oscillator.stop();
      } catch (e) {}
    });
    this.currentOscillators = [];
    this.isPlaying = false;
  }

  // Control
  setVolume(vol) {
    this.volume = Math.max(0, Math.min(1, vol));
    if (this.masterGain) {
      this.masterGain.gain.value = this.volume;
    }
  }

  toggle(enabled) {
    this.enabled = enabled;
    if (!enabled) {
      this.stopAll();
    }
  }
}

export const proceduralMusic = new ProceduralMusicEngine();
