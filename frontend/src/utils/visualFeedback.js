// Enhanced Visual Feedback System

// Error shake animation for wrong selections
export const shakeElement = (element) => {
  if (!element) return;
  
  element.style.animation = 'shake 0.5s';
  setTimeout(() => {
    element.style.animation = '';
  }, 500);
};

// Pulse animation for hints
export const pulseElement = (element, duration = 2000) => {
  if (!element) return;
  
  element.style.animation = 'pulse 0.6s ease-in-out 3';
  setTimeout(() => {
    element.style.animation = '';
  }, duration);
};

// Category-specific confetti
export const fireCategoryConfetti = (category) => {
  const categoryColors = {
    philosophy: ['#8B5CF6', '#A78BFA', '#C4B5FD'],
    values: ['#3B82F6', '#60A5FA', '#93C5FD'],
    emotions: ['#EC4899', '#F472B6', '#F9A8D4'],
    success: ['#F59E0B', '#FBBF24', '#FCD34D'],
    strength: ['#EF4444', '#F87171', '#FCA5A5'],
    relationships: ['#10B981', '#34D399', '#6EE7B7'],
    learning: ['#6366F1', '#818CF8', '#A5B4FC'],
    health: ['#22C55E', '#4ADE80', '#86EFAC'],
    nature: ['#059669', '#10B981', '#34D399'],
    spirituality: ['#8B5CF6', '#C084FC', '#E9D5FF'],
    creativity: ['#F97316', '#FB923C', '#FDBA74'],
    justice: ['#0EA5E9', '#38BDF8', '#7DD3FC']
  };
  
  const colors = categoryColors[category] || categoryColors.success;
  
  const count = 50;
  const defaults = {
    origin: { y: 0.7 },
    colors: colors
  };
  
  function fire(particleRatio, opts) {
    confetti({
      ...defaults,
      ...opts,
      particleCount: Math.floor(count * particleRatio),
      spread: 26,
      startVelocity: 55,
    });
  }
  
  fire(0.25, { spread: 26, startVelocity: 55 });
  fire(0.2, { spread: 60 });
  fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8 });
  fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2 });
  fire(0.1, { spread: 120, startVelocity: 45 });
};

// Ripple effect from a point
export const createRipple = (x, y, color = '#00D4FF') => {
  const ripple = document.createElement('div');
  ripple.style.position = 'fixed';
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;
  ripple.style.width = '10px';
  ripple.style.height = '10px';
  ripple.style.borderRadius = '50%';
  ripple.style.border = `2px solid ${color}`;
  ripple.style.transform = 'translate(-50%, -50%)';
  ripple.style.pointerEvents = 'none';
  ripple.style.zIndex = '9999';
  ripple.style.transition = 'all 0.6s ease-out';
  ripple.style.opacity = '0.8';
  
  document.body.appendChild(ripple);
  
  setTimeout(() => {
    ripple.style.width = '200px';
    ripple.style.height = '200px';
    ripple.style.opacity = '0';
  }, 10);
  
  setTimeout(() => {
    document.body.removeChild(ripple);
  }, 650);
};

// Flash screen with color
export const flashScreen = (color = '#22C55E', duration = 150) => {
  const flash = document.createElement('div');
  flash.style.position = 'fixed';
  flash.style.inset = '0';
  flash.style.backgroundColor = color;
  flash.style.opacity = '0';
  flash.style.pointerEvents = 'none';
  flash.style.zIndex = '9998';
  flash.style.transition = `opacity ${duration}ms ease-out`;
  
  document.body.appendChild(flash);
  
  setTimeout(() => {
    flash.style.opacity = '0.3';
  }, 10);
  
  setTimeout(() => {
    flash.style.opacity = '0';
  }, duration / 2);
  
  setTimeout(() => {
    document.body.removeChild(flash);
  }, duration * 2);
};

// Bounce animation for achievements
export const bounceIn = (element) => {
  if (!element) return;
  
  element.style.animation = 'bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
};

// Word reveal wave effect
export const wordRevealWave = (cells, category) => {
  const categoryColors = {
    philosophy: '#8B5CF6',
    values: '#3B82F6',
    emotions: '#EC4899',
    success: '#F59E0B',
    strength: '#EF4444',
    relationships: '#10B981',
    learning: '#6366F1',
    health: '#22C55E',
    nature: '#059669',
    spirituality: '#8B5CF6',
    creativity: '#F97316',
    justice: '#0EA5E9'
  };
  
  const color = categoryColors[category] || '#00D4FF';
  
  cells.forEach((cell, index) => {
    if (!cell) return;
    
    setTimeout(() => {
      // Pulse effect
      cell.style.transform = 'scale(1.3)';
      cell.style.boxShadow = `0 0 20px ${color}`;
      cell.style.zIndex = '100';
      
      setTimeout(() => {
        cell.style.transform = 'scale(1)';
        cell.style.boxShadow = '';
        cell.style.zIndex = '';
      }, 200);
    }, index * 50);
  });
};

// Progress bar animation
export const animateProgress = (element, from, to, duration = 600) => {
  if (!element) return;
  
  const start = Date.now();
  const diff = to - from;
  
  const animate = () => {
    const elapsed = Date.now() - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // Ease out cubic
    const current = from + (diff * eased);
    
    element.style.width = `${current}%`;
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  };
  
  requestAnimationFrame(animate);
};

// Floating text animation
export const showFloatingText = (text, x, y, color = '#00D4FF') => {
  const floater = document.createElement('div');
  floater.textContent = text;
  floater.style.position = 'fixed';
  floater.style.left = `${x}px`;
  floater.style.top = `${y}px`;
  floater.style.transform = 'translate(-50%, -50%)';
  floater.style.color = color;
  floater.style.fontSize = '1.5rem';
  floater.style.fontWeight = '900';
  floater.style.pointerEvents = 'none';
  floater.style.zIndex = '9999';
  floater.style.textShadow = `0 0 10px ${color}`;
  floater.style.transition = 'all 1s ease-out';
  floater.style.opacity = '1';
  
  document.body.appendChild(floater);
  
  setTimeout(() => {
    floater.style.transform = 'translate(-50%, -150%)';
    floater.style.opacity = '0';
  }, 10);
  
  setTimeout(() => {
    document.body.removeChild(floater);
  }, 1100);
};

// Add CSS animations to document
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
      20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    @keyframes bounceIn {
      0% { transform: scale(0); opacity: 0; }
      50% { transform: scale(1.1); }
      100% { transform: scale(1); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
}
