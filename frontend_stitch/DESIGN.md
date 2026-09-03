---
name: Bharat Academix
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#43474e'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#74777f'
  outline-variant: '#c4c6cf'
  surface-tint: '#455f88'
  primary: '#002045'
  on-primary: '#ffffff'
  primary-container: '#1a365d'
  on-primary-container: '#86a0cd'
  inverse-primary: '#adc7f7'
  secondary: '#8f4e00'
  on-secondary: '#ffffff'
  secondary-container: '#fe9832'
  on-secondary-container: '#683700'
  tertiary: '#002617'
  on-tertiary: '#ffffff'
  tertiary-container: '#003e29'
  on-tertiary-container: '#6eab8c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#adc7f7'
  on-primary-fixed: '#001b3c'
  on-primary-fixed-variant: '#2d476f'
  secondary-fixed: '#ffdcc2'
  secondary-fixed-dim: '#ffb77a'
  on-secondary-fixed: '#2e1500'
  on-secondary-fixed-variant: '#6d3a00'
  tertiary-fixed: '#b1f0ce'
  tertiary-fixed-dim: '#95d4b3'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#0e5138'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
  citation-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 16px
  sidebar-width: 320px
---

## Brand & Style
The design system is engineered for a premium AI-driven educational environment. It centers on the "India-modern" aesthetic: a synthesis of traditional academic authority and forward-leaning technological innovation. The UI utilizes a **Minimalist-Glassmorphic** hybrid approach. Surfaces are clean and structured to minimize cognitive load, while translucent layers and subtle blurs signify the fluid, "living" nature of AI-generated content.

The emotional response should be one of focused confidence. It avoids the frantic energy of social platforms in favor of a calm, institutional reliability. Every element—from the high-contrast typography to the deliberate use of whitespace—is designed to facilitate deep work and long-form learning.

## Colors
The palette is anchored by **Academy Blue**, a deep, high-contrast shade that provides a sense of institutional stability. 

- **Primary (Academy Blue):** Used for headers, primary navigation, and foundational text to establish authority.
- **Secondary (Saffron Spark):** Applied sparingly for high-priority calls to action, active states, and "moment of discovery" highlights.
- **Tertiary (Growth Green):** Dedicated exclusively to progress indicators, success states, and verified RAG citations.
- **Backgrounds:** A soft "Off-White" (#F8FAFC) is used to reduce eye strain, while pure white (#FFFFFF) is reserved for elevated cards and active workspaces.

## Typography
This design system employs a multi-family typographic scale to distinguish between instructional content and technical meta-data.

- **Headlines:** Plus Jakarta Sans provides a friendly yet modern professional tone. Its open counters ensure legibility even in dense academic headers.
- **Body:** Inter is used for all instructional text and chat interfaces. Its high x-height and neutral character make it ideal for sustained reading.
- **Technical/System:** JetBrains Mono is used for citations, timestamps, and AI-confidence scores to provide a distinct "data" feel that separates AI metadata from the core curriculum.

## Layout & Spacing
The layout follows a **structured fluid grid** model. The primary learning area (video or document) occupies a central 8-column span, while interactive sidebars (AI Chat/Transcripts) occupy a 4-column span.

- **Desktop:** A 12-column grid with 24px gutters. Content is centered with a max-width of 1440px to prevent excessive line lengths.
- **Mobile:** A single-column flow with 16px margins. Sidebars transition to bottom-sheet overlays or secondary tabs.
- **Rhythm:** All spacing (padding, margins, gap) must be multiples of the 8px base unit to maintain a strict vertical rhythm.

## Elevation & Depth
Depth is created through **Glassmorphism and Tonal Layering** rather than heavy shadows.

- **Level 0 (Base):** Off-white background.
- **Level 1 (Cards):** Pure white with a 1px border (#E2E8F0) and a very soft, 4% opacity neutral shadow.
- **Level 2 (AI Overlays/Modals):** Semi-transparent white (90% opacity) with a 20px backdrop blur and a 1px white inner-stroke to create a "glass" edge.
- **Interactions:** Hover states should not use shadows; instead, use a subtle scale-up (1.02x) and a shift in border color to the primary Academy Blue.

## Shapes
The shape language is "Sophisticated-Soft." A consistent **12px (0.75rem) radius** is applied to standard components like input fields, small cards, and buttons. 

For larger containers, such as video players and primary workspace panels, a **16px (1rem) radius** is used. Progress bars and citation badges utilize a **fully rounded (pill)** shape to differentiate them from interactive structural elements.

## Components
- **Primary Buttons:** Solid Academy Blue with white text. High-contrast, 12px rounded corners, 16px horizontal padding.
- **AI Citation Badges:** Pill-shaped, light Growth Green background (#D1FAE5) with dark green text and a small "source" icon. Used to ground AI claims in factual data.
- **Video Containers:** 16:9 aspect ratio with 16px corner radius. Controls should be hosted on a glassmorphic bar that overlays the bottom of the video on hover.
- **Chat/Transcript Sidebars:** Subtle gray background (#F1F5F9) to distinguish from the main workspace. Messages from the AI feature a light glassmorphic tint, while student messages are plain white cards.
- **Input Fields:** 1px border (#CBD5E1) that transitions to Academy Blue on focus. Labels use the JetBrains Mono "Label-md" style for a precise, technical feel.
- **Progress Indicators:** Linear bars using Growth Green for completion and Saffron Spark for current "in-focus" modules.