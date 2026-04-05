import React from 'react';
import { X, TrendingUp, Star, Target, Zap, Award } from 'lucide-react';

const StatsModal = ({ stats, lang, onClose }) => {
  const t = {
    ES: {
      title: "ESTADÍSTICAS",
      totalWords: "Palabras Totales",
      bestScore: "Mejor Puntuación",
      bestTime: "Mejor Tiempo",
      bestStreak: "Mejor Racha",
      level: "Nivel",
      xp: "Experiencia",
      gamesPlayed: "Partidas Jugadas",
      fastestWord: "Palabra Más Rápida",
      categories: "Por Categoría"
    },
    EN: {
      title: "STATISTICS",
      totalWords: "Total Words",
      bestScore: "Best Score",
      bestTime: "Best Time",
      bestStreak: "Best Streak",
      level: "Level",
      xp: "Experience",
      gamesPlayed: "Games Played",
      fastestWord: "Fastest Word",
      categories: "By Category"
    },
    FR: {
      title: "STATISTIQUES",
      totalWords: "Mots Totaux",
      bestScore: "Meilleur Score",
      bestTime: "Meilleur Temps",
      bestStreak: "Meilleure Série",
      level: "Niveau",
      xp: "Expérience",
      gamesPlayed: "Parties Jouées",
      fastestWord: "Mot Le Plus Rapide",
      categories: "Par Catégorie"
    }
  };

  const text = t[lang] || t.ES;
  const formatTime = (secs) => `${Math.floor(secs / 60)}:${(secs % 60).toString().padStart(2, '0')}`;

  return (
    <div className="modal-backdrop absolute inset-0 flex items-center justify-center z-50 p-4">
      <div className="modal-content glass-strong rounded-3xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-heading text-2xl" style={{ color: 'var(--accent-primary)' }}>{text.title}</h2>
          <button className="btn-icon w-10 h-10" onClick={onClose}><X size={18} /></button>
        </div>
        
        {/* Level & XP */}
        <div className="mb-6 p-4 rounded-2xl" style={{ background: 'linear-gradient(135deg, var(--accent-secondary), var(--accent-primary))' }}>
          <div className="flex items-center justify-between text-white">
            <div>
              <div className="text-sm opacity-80">{text.level}</div>
              <div className="text-4xl font-bold">{stats.level}</div>
            </div>
            <div className="text-right">
              <div className="text-sm opacity-80">{text.xp}</div>
              <div className="text-2xl font-bold">{stats.totalXP}</div>
            </div>
          </div>
          <div className="mt-2 h-2 bg-white/20 rounded-full overflow-hidden">
            <div className="h-full bg-white rounded-full" style={{ width: `${(stats.totalXP % 1000) / 10}%` }}></div>
          </div>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="stat-card">
            <Star size={20} style={{ color: 'var(--accent-primary)' }} />
            <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats.totalWords}</div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{text.totalWords}</div>
          </div>
          <div className="stat-card">
            <Target size={20} style={{ color: 'var(--success)' }} />
            <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats.bestScore}</div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{text.bestScore}</div>
          </div>
          <div className="stat-card">
            <Zap size={20} style={{ color: 'var(--warning)' }} />
            <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats.bestStreak}</div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{text.bestStreak}</div>
          </div>
          <div className="stat-card">
            <TrendingUp size={20} style={{ color: 'var(--accent-secondary)' }} />
            <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats.totalGames}</div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{text.gamesPlayed}</div>
          </div>
        </div>

        {/* Category Stats */}
        <div className="mt-4">
          <h3 className="font-bold mb-2" style={{ color: 'var(--text-secondary)' }}>{text.categories}</h3>
          <div className="grid grid-cols-3 gap-2 text-sm">
            {Object.entries(stats.categoryWords).map(([cat, count]) => (
              <div key={cat} className="p-2 rounded-lg" style={{ background: 'var(--bg-surface)' }}>
                <div className="font-bold" style={{ color: 'var(--accent-primary)' }}>{count}</div>
                <div className="text-xs capitalize" style={{ color: 'var(--text-muted)' }}>{cat}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsModal;