# KisanSathi — Design System Tokens Spec

## 1. Color Palette (Tailwind + CSS Variables)
Tailored for agriculture, warmth, high outdoor readability (sunlight contrast), and trust.

### Primitive & Semantic Tokens
```css
:root {
  /* Brand Primary: Deep Agriculture Emerald */
  --primary-50: #f0fdf4;
  --primary-100: #dcfce7;
  --primary-500: #22c55e;
  --primary-600: #16a34a;
  --primary-700: #15803d; /* Primary Brand Hero */
  --primary-800: #166534;
  --primary-900: #14532d;

  /* Accent: Warm Harvest Amber / Golden Crop */
  --accent-50: #fffbeb;
  --accent-100: #fef3c7;
  --accent-400: #fbbf24;
  --accent-500: #f59e0b; /* Primary Accent */
  --accent-600: #d97706;

  /* Neutrals: Earthy Slate / Soil */
  --slate-50: #f8fafc;
  --slate-100: #f1f5f9;
  --slate-200: #e2e8f0;
  --slate-400: #94a3b8;
  --slate-600: #475569;
  --slate-800: #1e293b;
  --slate-900: #0f172a;

  /* Semantic Feedback */
  --color-success: #16a34a;
  --color-warning: #f59e0b;
  --color-danger: #dc2626;
  --color-info: #0284c7;

  /* Elevation & Surface (Light Theme) */
  --bg-app: #f8fafc;
  --bg-card: #ffffff;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --border-subtle: #e2e8f0;
  --radius-card: 12px;
  --radius-button: 8px;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

.dark {
  --bg-app: #0f172a;
  --bg-card: #1e293b;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --border-subtle: #334155;
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.3);
}
```

## 2. Typography Scale
- UI Font: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- Indic Fallback: `"Noto Sans Devanagari", "Noto Sans Gujarati", sans-serif`
- Scale:
  - `text-xs`: 12px / line-height 1.5 (Footnotes, source tags)
  - `text-sm`: 14px / line-height 1.5 (Secondary text, dates, chips)
  - `text-base`: 16px / line-height 1.5 (Body copy, chat messages, input values)
  - `text-lg`: 18px / line-height 1.4 (Card headings, section headers)
  - `text-xl`: 20px / line-height 1.3 (Dialog titles)
  - `text-2xl`: 24px / line-height 1.2 (Dashboard screen titles)
  - `text-3xl`: 30px / line-height 1.1 (Hero metrics, Mandi prices)

## 3. Touch Targets & Accessibility (WCAG AA)
- Minimum interactive touch target: **48px x 48px** for all mobile buttons, tabs, and toggles.
- Contrast ratio: Minimum **4.5:1** for regular text against background; **3:1** for large text/icons.
- Visible focus ring: `ring-2 ring-emerald-500 ring-offset-2`.
- `prefers-reduced-motion`: Disables non-essential CSS transitions/animations.
