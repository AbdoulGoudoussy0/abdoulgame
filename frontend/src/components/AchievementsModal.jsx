import React from 'react';
import { X, Lock } from 'lucide-react';

const AchievementsModal = ({ achievements, unlockedIds, lang, onClose }) => {
  const t = {
    ES: { title: "LOGROS", locked: "Bloqueado", unlocked: "Desbloqueados" },
    EN: { title: "ACHIEVEMENTS", locked: "Locked", unlocked: "Unlocked" },
    FR: { title: "SUCCÈS", locked: "Verrouillé", unlocked: "Débloqués" }
  };

  const text = t[lang] || t.ES;
  const unlockedCount = unlockedIds.length;

  return (
    <div className="modal-backdrop fixed inset-0 flex items-center justify-center z-[9999] p-4" onClick={onClose} style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}>
      <div className="modal-content glass-strong rounded-3xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="font-heading text-2xl" style={{ color: 'var(--accent-primary)' }}>{text.title}</h2>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              {text.unlocked}: {unlockedCount}/{achievements.length}
            </p>
          </div>
          <button className="btn-icon w-10 h-10" onClick={onClose}><X size={18} /></button>
        </div>
        
        <div className="space-y-3">
          {achievements.map((achievement) => {
            const isUnlocked = unlockedIds.includes(achievement.id);
            return (
              <div
                key={achievement.id}
                className={`p-4 rounded-2xl transition-all ${
                  isUnlocked ? 'achievement-unlocked' : 'achievement-locked'
                }`}
                style={{
                  background: isUnlocked
                    ? 'linear-gradient(135deg, var(--accent-secondary), var(--accent-primary))'
                    : 'var(--bg-surface)',
                  opacity: isUnlocked ? 1 : 0.5
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="text-3xl">
                    {isUnlocked ? achievement.icon : <Lock size={24} />}
                  </div>
                  <div className="flex-1">
                    <div
                      className="font-bold"
                      style={{ color: isUnlocked ? 'white' : 'var(--text-primary)' }}
                    >
                      {achievement.name}
                    </div>
                    <div
                      className="text-sm"
                      style={{ color: isUnlocked ? 'rgba(255,255,255,0.8)' : 'var(--text-muted)' }}
                    >
                      {achievement.description}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AchievementsModal;