# VayuSetu Design System

This document outlines the official design tokens, typography, spacing, colors, and layout guidelines for the **VayuSetu Urban Intelligence Platform**, extracted from the Stitch project.

---

## 🌟 Brand & Style
The design system is engineered for high-stakes urban intelligence, blending the analytical rigor of geographic information systems (ArcGIS) with the refined utility of high-end developer tools (Linear/Stripe). 

The brand personality is **authoritative yet approachable**, positioning itself as a silent, intelligent partner for urban planners and environmental agencies.

The visual style follows a **Modern Corporate** aesthetic with a strong emphasis on **Precision Minimalism**. It utilizes expansive white space, a disciplined color application, and a functional hierarchy to ensure that dense environmental data remains legible and actionable. The interface feels expansive, clean, and technologically advanced, evoking a sense of calm control over complex data.

---

## 🎨 Color Palette
This design system utilizes a structured palette designed for rapid data interpretation.

### Core Brand Colors
| Color Role | Color Hex | Description |
| :--- | :--- | :--- |
| **Primary** | `● #004ac6` | Primary brand blue. Used for primary actions, active navigation states, and highlights. |
| **Primary Container** | `● #2563eb` | High-contrast container background. |
| **Secondary** | `● #505f76` | Supporting UI elements, inactive icons, and metadata. |
| **Neutral Surface** | `● #ffffff` | Surface container background to create a subtle lift from the background. |
| **Background** | `● #f7f9fb` | Crisp neutral canvas to allow data and highlights to pop. |
| **Error** | `● #ba1a1a` | Warning / Alert actions and critical status indications. |

### Complete Palette Specification
Below is the full set of named colors mapped to the Material Design token system:

#### Primary & Secondary
* **Primary:** `● #004ac6` | **On Primary:** `● #ffffff`
* **Primary Container:** `● #2563eb` | **On Primary Container:** `● #eeefff`
* **Primary Fixed:** `● #dbe1ff` | **Primary Fixed Dim:** `● #b4c5ff`
* **On Primary Fixed:** `● #00174b` | **On Primary Fixed Variant:** `● #003ea8`
* **Secondary:** `● #505f76` | **On Secondary:** `● #ffffff`
* **Secondary Container:** `● #d0e1fb` | **On Secondary Container:** `● #54647a`
* **Secondary Fixed:** `● #d3e4fe` | **Secondary Fixed Dim:** `● #b7c8e1`
* **On Secondary Fixed:** `● #0b1c30` | **On Secondary Fixed Variant:** `● #38485d`

#### Tertiary & Surface
* **Tertiary:** `● #943700` | **On Tertiary:** `● #ffffff`
* **Tertiary Container:** `● #bc4800` | **On Tertiary Container:** `● #ffede6`
* **Tertiary Fixed:** `● #ffdbcd` | **Tertiary Fixed Dim:** `● #ffb596`
* **On Tertiary Fixed:** `● #360f00` | **On Tertiary Fixed Variant:** `● #7d2d00`
* **Surface:** `● #f7f9fb` | **Surface Bright:** `● #f7f9fb` | **Surface Dim:** `● #d8dadc`
* **Surface Container Lowest:** `● #ffffff`
* **Surface Container Low:** `● #f2f4f6`
* **Surface Container:** `● #eceef0`
* **Surface Container High:** `● #e6e8ea`
* **Surface Container Highest:** `● #e0e3e5`
* **On Surface:** `● #191c1e` | **On Surface Variant:** `● #434655`
* **Inverse Surface:** `● #2d3133` | **Inverse On Surface:** `● #eff1f3`
* **Outline:** `● #737686` | **Outline Variant:** `● #c3c6d7`
* **Surface Tint:** `● #0053db` | **Surface Variant:** `● #e0e3e5`

#### Error
* **Error:** `● #ba1a1a` | **On Error:** `● #ffffff`
* **Error Container:** `● #ffdad6` | **On Error Container:** `● #93000a`

---

## 🔠 Typography
The typography relies exclusively on **Inter** for its systematic, utilitarian, and highly legible qualities. A secondary monospaced font (**JetBrains Mono**) is permitted strictly for coordinates, technical sensor IDs, and raw data output.

### Type Styles
| Token | Font Family | Size | Weight | Line Height | Letter Spacing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **display-lg** | Inter | `48px` | `700` (Bold) | `56px` | `-0.02em` |
| **headline-lg** | Inter | `32px` | `600` (Semi-Bold) | `40px` | `-0.02em` |
| **headline-md** | Inter | `24px` | `600` (Semi-Bold) | `32px` | `-0.01em` |
| **headline-sm** | Inter | `20px` | `600` (Semi-Bold) | `28px` | Normal |
| **body-lg** | Inter | `16px` | `400` (Regular) | `24px` | Normal |
| **body-md** | Inter | `14px` | `400` (Regular) | `20px` | Normal |
| **label-md** | Inter | `12px` | `500` (Medium) | `16px` | `0.01em` |
| **mono-md** | JetBrains Mono | `13px` | `400` (Regular) | `18px` | Normal |

---

## 📏 Spacing & Layout
A systematic spacing scale is used to define layout grids, component margins, and paddings. Spacing scales are based on an **8px linear scaling rhythm** for internal alignment.

### Spacing Scale
* **xs:** `4px`
* **base:** `4px`
* **sm:** `8px`
* **md:** `16px`
* **lg:** `24px`
* **xl:** `32px`
* **2xl:** `48px`

### Layout Dimensions
* **Container Max Width:** `1440px`
* **Sidebar Width:** `240px`
* **Layout Grid:** Fluid grid for map layouts, fixed sidebar for navigation.
* **Component Padding:**
  * Interactive elements and tables should use compact/dense padding (`8px` / `12px`) for high information density.
  * Information cards should maintain generous `24px` padding.
* **Margins:** Dashboard panels must maintain a `24px` margin from the screen edge on Desktop, and reduce to `16px` on Mobile.
* **Breakpoints:**
  * **Mobile (<768px):** Sidebar collapses into a bottom navigation bar or hamburger menu. Margins reduce to `16px`.
  * **Desktop (>1024px):** Dual-pane view (Navigation + Content + Inspector panel).

---

## 📐 Shape & Roundness
The shape language balances modern approachability and clean technical structure:

* **sm (Small Elements):** `0.25rem` (e.g., input checkboxes, small tags)
* **DEFAULT (Standard):** `0.5rem` / `8px` (e.g., buttons, input fields, standard widgets)
* **md (Medium Components):** `0.75rem` / `12px` (e.g., cards, dashboard widgets)
* **lg (Large Containers):** `1.0rem` / `16px` (e.g., larger map overlay panels, modal sheets)
* **xl:** `1.5rem`
* **full:** `9999px` (e.g., pill badges, fully rounded avatars)

---

## 🌑 Elevation & Depth
Depth is established through **Tonal Layering** and **Ambient Shadows** to simulate hierarchy:

* **Level 0 (Base):** Background `#F8FAFC`.
* **Level 1 (Cards & Sidebars):** `#FFFFFF` surfaces with a `1px` border of `#E2E8F0` and a soft, diffused ambient shadow:
  ```css
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  ```
* **Level 2 (Modals & Popovers):** High elevation shadow to indicate overlay context:
  ```css
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  ```
* **Hover Interaction:** Buttons and interactive cards should lift on hover by slightly increasing the shadow spread and reducing the Y-offset.

---

## 🧩 Key Component Specs

### 1. Sidebar Navigation
* **Style:** Transparent background with a `1px` right border.
* **Icons:** Size `18px`, color `Secondary/400`.
* **States:** Active states use a subtle `Primary/50` background tint and a `Primary/600` icon.

### 2. Data Visualization Cards
* **Style:** White background, `1px` border in `#E2E8F0`.
* **Padding:** `24px` (lg).
* **Header:** Includes a `Label-MD` title and an optional "More" icon button.

### 3. AQI Status Badges
* **Style:** Small, high-contrast labels with a `6px` corner radius.
* **Contrast:** Text color should be a darkened version of the semantic color for accessibility.
  * *Example:* Safe status uses a light green background `#DCFCE7` and dark green text `#166534`.

### 4. Action Buttons (e.g., "Generate Notice")
* **Primary:** Background `#2563EB`, white text, `8px` corner radius. A subtle top-to-bottom gradient with 5% opacity is applied for a premium feel.
* **Ghost:** White background with a subtle border and no shadow until hovered.

### 5. Map Elements
* **Pins:** A "Droplet" shape colored using the AQI semantic severity scale.
* **Interactive State:** When selected, pins expand to reveal a mini-sparkline showing the 24-hour AQI trend.

### 6. Health Advisory Card
* **Style:** Soft tint background of the current AQI severity color (at 5% opacity).
* **Graphics:** Minimalist, illustrative icons.
