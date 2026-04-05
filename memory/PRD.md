# AbdoulGame Ultimate Polyglot - PRD

## Original Problem Statement
Multilingual word search game with football/soccer stadium theme featuring:
- Word search puzzle where players find hidden words
- Multilingual support (Spanish, English, French)
- Timer countdown, score tracking, multiple themes
- AI hint system, settings panel, progress tracking
- Confetti celebration on win, mobile-friendly

## Architecture
- **Frontend**: React 19 with Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Styling**: Custom CSS with Glassmorphism effects

## User Personas
1. **Casual Gamers**: Want quick, fun word puzzles
2. **Language Learners**: Practice vocabulary in ES/EN/FR
3. **Mobile Users**: Play on touch devices

## Core Requirements (Static)
- [x] Word search grid generation
- [x] Word selection via click/swipe
- [x] Timer countdown (2 minutes)
- [x] Score system (+200 per word, -100 for hints)
- [x] Multilingual UI (ES/EN/FR)
- [x] Multiple themes (Neon/Classic/Gold)
- [x] Knowledge phrases display
- [x] Win/Lose conditions
- [x] Settings persistence

## What's Been Implemented (Jan 5, 2026)
- Full game mechanics with word detection
- Backend API for game generation and scoring
- Responsive UI with stadium background
- Theme/language switching
- Hint system with visual feedback
- Settings modal with controls
- Progress bar and word bank
- Win celebration with confetti

## API Endpoints
- `GET /api/` - Health check
- `GET /api/knowledge` - Get word database
- `POST /api/game/generate` - Generate game board
- `POST /api/scores` - Save score
- `GET /api/scores/top` - Get leaderboard
- `GET /api/scores/player/{name}` - Get player scores

## Prioritized Backlog
### P0 (Critical)
- All complete ✅

### P1 (High Priority)
- [ ] Persistent user accounts
- [ ] Global leaderboard display
- [ ] More word categories

### P2 (Medium Priority)
- [ ] Daily challenges
- [ ] Achievement system
- [ ] Sound effects customization
- [ ] Offline mode (PWA)

## Next Tasks
1. Add leaderboard UI component
2. Implement user registration
3. Add more knowledge words to database
