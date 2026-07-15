# VayuSetu - Cursor / AI Agent Rules

When assisting with or modifying the VayuSetu codebase, strictly adhere to the following rules:

## 1. UI / UX Standards (Vibe Coding)
- Always prioritize a premium, modern aesthetic. 
- Use standard Tailwind CSS utilities. Avoid custom CSS files unless implementing complex keyframe animations or WebGL canvases.
- Maintain the glassmorphism aesthetic (`bg-white/70`, `backdrop-blur`, `shadow-soft`).
- Always ensure responsive design (use `md:`, `lg:` prefixes properly).

## 2. API & Data Flow
- Frontend must exclusively fetch data via `src/api/client.js`. Never write inline `fetch` calls inside React components.
- Honor the `VITE_USE_MOCK_DATA` flag. If adding a new endpoint, provide a mock data fallback in `client.js`.
- The frontend should gracefully handle loading states (using skeleton loaders) and `null` data gracefully.

## 3. Component Architecture
- Keep components modular. If a file exceeds 300 lines, consider extracting sub-components into the `src/components/ui/` folder.
- Always use `useMemo` and `useCallback` when passing props to heavy visualization components (like Maps or Charts) to prevent unnecessary re-renders.

## 4. Backend Standards
- Keep routes clean. Business logic and AI prompting must reside in isolated services (e.g., `station_panel.py`, `dispersion.py`), not inside `routes.py`.
- Always wrap Gemini AI calls in `try/except` blocks and provide hardcoded fallback text to ensure the API never crashes the UI if the AI service is down.
