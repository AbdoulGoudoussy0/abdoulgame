// Enhanced particle effects for word discoveries

export const createCategoryParticles = (category, x, y) => {
  const particles = {
    philosophy: { emoji: '🧠', count: 15, colors: ['#8B5CF6', '#A78BFA'] },
    values: { emoji: '💎', count: 12, colors: ['#3B82F6', '#60A5FA'] },
    emotions: { emoji: '❤️', count: 20, colors: ['#EC4899', '#F472B6'] },
    success: { emoji: '⭐', count: 18, colors: ['#F59E0B', '#FBBF24'] },
    strength: { emoji: '💪', count: 15, colors: ['#EF4444', '#F87171'] },
    relationships: { emoji: '🤝', count: 12, colors: ['#10B981', '#34D399'] },
    learning: { emoji: '📚', count: 14, colors: ['#6366F1', '#818CF8'] },
    health: { emoji: '💚', count: 16, colors: ['#22C55E', '#4ADE80'] },
    nature: { emoji: '🌿', count: 18, colors: ['#059669', '#10B981'] },
    spirituality: { emoji: '✨', count: 20, colors: ['#8B5CF6', '#C084FC'] },
    creativity: { emoji: '🎨', count: 16, colors: ['#F97316', '#FB923C'] },
    justice: { emoji: '⚖️', count: 14, colors: ['#0EA5E9', '#38BDF8'] }
  };

  const particleConfig = particles[category] || particles.success;
  
  // Create particle elements
  for (let i = 0; i < particleConfig.count; i++) {
    const particle = document.createElement('div');
    particle.textContent = particleConfig.emoji;
    particle.style.position = 'fixed';
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;
    particle.style.fontSize = `${Math.random() * 20 + 15}px`;
    particle.style.pointerEvents = 'none';
    particle.style.zIndex = '9999';
    particle.style.transition = 'all 1.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    
    document.body.appendChild(particle);
    
    // Animate
    setTimeout(() => {
      const angle = (Math.PI * 2 * i) / particleConfig.count;
      const distance = Math.random() * 150 + 100;
      const tx = Math.cos(angle) * distance;
      const ty = Math.sin(angle) * distance - 100; // Move up
      
      particle.style.transform = `translate(${tx}px, ${ty}px) scale(0)`;
      particle.style.opacity = '0';
    }, 10);
    
    // Remove after animation
    setTimeout(() => {
      document.body.removeChild(particle);
    }, 1600);
  }
};

export const createWordRevealEffect = (cells) => {
  // Wave effect on word cells
  cells.forEach((cell, index) => {
    setTimeout(() => {
      if (cell) {
        cell.style.transform = 'scale(1.3) rotateZ(5deg)';
        setTimeout(() => {
          cell.style.transform = 'scale(1)';
        }, 200);
      }
    }, index * 50);
  });
};

export const createComboEffect = (comboCount, x, y) => {
  const comboText = document.createElement('div');
  comboText.innerHTML = `<div style="font-size: 2rem; font-weight: 900; color: #F59E0B; text-shadow: 0 0 20px #F59E0B;">
    🔥 ${comboCount}x COMBO! 🔥
  </div>`;
  comboText.style.position = 'fixed';
  comboText.style.left = `${x}px`;
  comboText.style.top = `${y}px`;
  comboText.style.transform = 'translate(-50%, -50%)';
  comboText.style.pointerEvents = 'none';
  comboText.style.zIndex = '9999';
  comboText.style.transition = 'all 1s ease-out';
  comboText.style.opacity = '1';
  
  document.body.appendChild(comboText);
  
  setTimeout(() => {
    comboText.style.transform = 'translate(-50%, -150%) scale(1.5)';
    comboText.style.opacity = '0';
  }, 100);
  
  setTimeout(() => {
    document.body.removeChild(comboText);
  }, 1100);
};

export const createLevelUpEffect = (newLevel) => {
  const levelUpDiv = document.createElement('div');
  levelUpDiv.innerHTML = `
    <div style="
      font-size: 3rem;
      font-weight: 900;
      background: linear-gradient(135deg, #8B5CF6, #EC4899);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      text-shadow: 0 0 40px rgba(139, 92, 246, 0.5);
    ">
      ⬆️ LEVEL ${newLevel} ⬆️
    </div>
  `;
  levelUpDiv.style.position = 'fixed';
  levelUpDiv.style.top = '50%';
  levelUpDiv.style.left = '50%';
  levelUpDiv.style.transform = 'translate(-50%, -50%) scale(0)';
  levelUpDiv.style.zIndex = '10000';
  levelUpDiv.style.transition = 'all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
  levelUpDiv.style.opacity = '0';
  
  document.body.appendChild(levelUpDiv);
  
  setTimeout(() => {
    levelUpDiv.style.transform = 'translate(-50%, -50%) scale(1)';
    levelUpDiv.style.opacity = '1';
  }, 100);
  
  setTimeout(() => {
    levelUpDiv.style.transform = 'translate(-50%, -50%) scale(0)';
    levelUpDiv.style.opacity = '0';
  }, 2000);
  
  setTimeout(() => {
    document.body.removeChild(levelUpDiv);
  }, 2600);
};

export const createAchievementToast = (achievement) => {
  const toast = document.createElement('div');
  toast.innerHTML = `
    <div style="
      background: linear-gradient(135deg, rgba(139, 92, 246, 0.95), rgba(236, 72, 153, 0.95));
      backdrop-filter: blur(20px);
      padding: 1rem 1.5rem;
      border-radius: 1rem;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
      display: flex;
      align-items: center;
      gap: 1rem;
      min-width: 300px;
    ">
      <div style="font-size: 2rem;">${achievement.icon}</div>
      <div>
        <div style="font-weight: 800; color: white; font-size: 1rem;">🏆 Logro Desbloqueado</div>
        <div style="font-weight: 600; color: white; font-size: 0.875rem;">${achievement.name}</div>
        <div style="color: rgba(255,255,255,0.8); font-size: 0.75rem;">${achievement.description}</div>
      </div>
    </div>
  `;
  toast.style.position = 'fixed';
  toast.style.top = '20px';
  toast.style.right = '-400px';
  toast.style.zIndex = '10001';
  toast.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.right = '20px';
  }, 100);
  
  setTimeout(() => {
    toast.style.right = '-400px';
  }, 4000);
  
  setTimeout(() => {
    document.body.removeChild(toast);
  }, 4600);
};
