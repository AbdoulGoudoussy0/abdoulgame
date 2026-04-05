import React from 'react';
import { Target, BookOpen, Calendar, Sparkles } from 'lucide-react';

const GameModeSelector = ({ lang, categories, onSelectMode, onClose }) => {
  const t = {
    ES: {
      title: "SELECCIONA MODO",
      normal: "Normal",
      normalDesc: "Juego clásico con niveles progresivos",
      practice: "Práctica",
      practiceDesc: "Enfócate en una categoría específica",
      daily: "Desafío Diario",
      dailyDesc: "Mismo tablero para todos hoy",
      zen: "Modo Zen",
      zenDesc: "Sin temporizador, solo aprendizaje",
      selectCategory: "Selecciona categoría:",
      all: "Todas"
    },
    EN: {
      title: "SELECT MODE",
      normal: "Normal",
      normalDesc: "Classic game with progressive levels",
      practice: "Practice",
      practiceDesc: "Focus on a specific category",
      daily: "Daily Challenge",
      dailyDesc: "Same board for everyone today",
      zen: "Zen Mode",
      zenDesc: "No timer, just learning",
      selectCategory: "Select category:",
      all: "All"
    },
    FR: {
      title: "SÉLECTIONNER MODE",
      normal: "Normal",
      normalDesc: "Jeu classique avec niveaux progressifs",
      practice: "Pratique",
      practiceDesc: "Concentrez-vous sur une catégorie spécifique",
      daily: "Défi Quotidien",
      dailyDesc: "Même plateau pour tous aujourd'hui",
      zen: "Mode Zen",
      zenDesc: "Pas de minuterie, juste apprentissage",
      selectCategory: "Sélectionnez catégorie:",
      all: "Toutes"
    }
  };

  const text = t[lang] || t.ES;
  const [selectedCategory, setSelectedCategory] = React.useState("all");

  const modes = [
    { id: 'normal', name: text.normal, desc: text.normalDesc, icon: Target, color: 'var(--accent-primary)' },
    { id: 'practice', name: text.practice, desc: text.practiceDesc, icon: BookOpen, color: 'var(--success)' },
    { id: 'daily', name: text.daily, desc: text.dailyDesc, icon: Calendar, color: 'var(--warning)' },
    { id: 'zen', name: text.zen, desc: text.zenDesc, icon: Sparkles, color: 'var(--accent-secondary)' }
  ];

  const handleSelectMode = (modeId) => {
    if (modeId === 'practice') {
      onSelectMode(modeId, selectedCategory);
    } else {
      onSelectMode(modeId, null);
    }
  };

  return (
    <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4">
      <div className="modal-content glass-strong rounded-3xl p-6 max-w-md w-full">
        <h2 className="font-heading text-2xl mb-6 text-center" style={{ color: 'var(--accent-primary)' }}>
          {text.title}
        </h2>
        
        <div className="space-y-3">
          {modes.map((mode) => (
            <button
              key={mode.id}
              className="w-full p-4 rounded-2xl transition-all hover:scale-105"
              style={{ background: 'var(--bg-surface)', border: '2px solid var(--border-color)' }}
              onClick={() => handleSelectMode(mode.id)}
            >
              <div className="flex items-center gap-3">
                <mode.icon size={24} style={{ color: mode.color }} />
                <div className="text-left flex-1">
                  <div className="font-bold" style={{ color: 'var(--text-primary)' }}>{mode.name}</div>
                  <div className="text-sm" style={{ color: 'var(--text-muted)' }}>{mode.desc}</div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Category selector for practice mode */}
        <div className="mt-4 p-4 rounded-2xl" style={{ background: 'var(--bg-surface)' }}>
          <label className="text-sm font-bold mb-2 block" style={{ color: 'var(--text-secondary)' }}>
            {text.selectCategory}
          </label>
          <select
            className="w-full p-2 rounded-lg"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-color)' }}
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="all">{text.all}</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat[lang]}</option>
            ))}
          </select>
        </div>

        <button
          className="btn-game btn-secondary w-full mt-4"
          onClick={onClose}
        >
          {lang === 'ES' ? 'Cancelar' : lang === 'EN' ? 'Cancel' : 'Annuler'}
        </button>
      </div>
    </div>
  );
};

export default GameModeSelector;