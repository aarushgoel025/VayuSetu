# Design System - VayuSetu

## 1. Core Philosophy
VayuSetu utilizes a clean, data-dense, yet visually engaging "glassmorphism" aesthetic. The goal is to make alarming data (pollution) look clinical, professional, and actionable.

## 2. Color Palette
The application uses a semantic color scale tailored through Tailwind configuration.

- **Primary:** `blue-600` (Used for authority actions, primary buttons, and active states).
- **Secondary:** `slate-500` (Used for labels, muted text, and metadata).
- **Backgrounds:** `slate-50` (App background), `white` (Cards).
- **Error/Alert:** `red-600` (Used for severe AQI, legal violations, and critical alerts).

### AQI Severity Color Scale
Data visualization explicitly uses these Tailwind colors to denote severity:
- **Good (0-50):** `emerald-500`
- **Satisfactory (51-100):** `green-500`
- **Moderate (101-200):** `amber-500`
- **Poor (201-300):** `orange-500`
- **Severe (301+):** `red-500`

## 3. Typography
- **Primary Font:** Inter (or system-sans-serif).
- **Headers:** Bold, tight tracking (`tracking-tight`), uppercase for small labels (`uppercase tracking-wider text-[10px]`).
- **Data Values:** Extra bold, large sizes (e.g., `text-4xl font-extrabold`).

## 4. UI Components

### Cards
All surface cards use a consistent styling:
`bg-white p-5 rounded-xl border border-outline-variant shadow-soft`
If layered over a map or complex background, they use a translucent variant:
`bg-white/80 backdrop-blur-md`

### Buttons
- **Primary Action:** Solid background, rounded-lg, font-bold, white text.
- **Secondary Action:** Ghost style, text-secondary, hover to primary color.
- **Toggle (e.g., Lang switch):** Tight padding, distinct active state shadow.

## 5. Animations
- **Page Load:** Framer Motion `fadeUp` (opacity 0 -> 1, y: 20 -> 0).
- **Scroll Snap:** Used extensively on the Landing Page for a presentation-like sequence.
- **Hover States:** Subtle translateY (`-translate-y-0.5`) and shadow expansion on interactive cards.
