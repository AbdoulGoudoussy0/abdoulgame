# AbdoulGame Ultimate Polyglot - PRD

## Original Problem Statement
Multilingual word search game with football/soccer stadium theme. V2 Updates requested:
- Sonidos suaves al encontrar palabras
- Diseño responsive para móvil/tablet/desktop con manejo de orientación
- Animaciones y transiciones modernas
- Selector de nivel manual con progreso automático
- Integración de IA avanzada (GPT-4o)
- Botón de compartir logros en redes sociales
- Interfaz inmersiva y acogedora

## Architecture
- **Frontend**: React 19 with Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI**: OpenAI GPT-4o via Emergent LLM Key
- **Styling**: Custom CSS with Glassmorphism effects

## User Personas
1. **Casual Gamers**: Quick, fun word puzzles
2. **Language Learners**: Practice vocabulary in ES/EN/FR
3. **Mobile Users**: Play on touch devices (portrait/landscape)
4. **Social Players**: Share achievements with friends

## Core Requirements (Static)
- [x] Word search grid generation
- [x] Word selection via click/swipe
- [x] Timer countdown with visual warnings
- [x] Score system with animations
- [x] Multilingual UI (ES/EN/FR)
- [x] Multiple themes (Neon/Classic/Gold)
- [x] Knowledge phrases display
- [x] Win/Lose conditions
- [x] Settings persistence

## V2 Features Implemented (Jan 5, 2026)
- [x] Soft, pleasant sounds (base64 encoded)
- [x] Responsive design for mobile/tablet/desktop
- [x] Portrait/Landscape orientation support
- [x] Modern animations (cell-pulse, found-glow, trophy-bounce)
- [x] Manual level selector (1-10) with auto progression
- [x] AI-powered hints via GPT-4o
- [x] AI-generated wisdom phrases
- [x] AI encouragement messages
- [x] Social sharing button (native share + clipboard)
- [x] Immersive glassmorphism UI
- [x] Progress bar with shimmer effect

## API Endpoints
- `GET /api/` - Health check
- `GET /api/knowledge` - Get word database
- `POST /api/game/generate` - Generate game board (with time_limit by level)
- `POST /api/ai/hint` - Get AI-powered hint (GPT-4o)
- `POST /api/ai/wisdom` - Get AI wisdom phrase
- `POST /api/ai/encouragement` - Get AI encouragement
- `POST /api/share/generate` - Generate share text
- `POST /api/scores` - Save score
- `GET /api/scores/top` - Get leaderboard

## Level Configuration
| Level | Grid Size | Words | Time Limit |
|-------|-----------|-------|------------|
| 1     | 8x8       | 3     | 150s       |
| 2     | 8x8       | 4     | 140s       |
| 3     | 9x9       | 4     | 130s       |
| 4     | 9x9       | 5     | 125s       |
| 5     | 10x10     | 5     | 120s       |
| 6     | 10x10     | 6     | 115s       |
| 7     | 11x11     | 6     | 110s       |
| 8     | 11x11     | 7     | 105s       |
| 9     | 12x12     | 7     | 100s       |
| 10    | 12x12     | 8     | 95s        |

## Prioritized Backlog
### P0 (Critical) - Completed ✅

### P1 (High Priority)
- [ ] User accounts with persistent progress
- [ ] Global leaderboard display in UI
- [ ] More word categories/themes

### P2 (Medium Priority)
- [ ] Daily challenges mode
- [ ] Achievement badges system
- [ ] Multiplayer mode
- [ ] Offline PWA support

## Known Issues
- Minor: French AI hints occasionally reveal word directly (LOW priority)

## Next Tasks
1. Add leaderboard UI component
2. Implement user registration/login
3. Tune AI prompts for better hint quality in French
