---
name: Kinetic Pulse
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1b1c1c'
  on-surface-variant: '#444650'
  inverse-surface: '#303030'
  inverse-on-surface: '#f3f0ef'
  outline: '#757682'
  outline-variant: '#c5c6d2'
  surface-tint: '#435b9f'
  primary: '#00113a'
  on-primary: '#ffffff'
  primary-container: '#002366'
  on-primary-container: '#758dd5'
  inverse-primary: '#b3c5ff'
  secondary: '#216a52'
  on-secondary: '#ffffff'
  secondary-container: '#a7efcf'
  on-secondary-container: '#276e56'
  tertiary: '#1d1200'
  on-tertiary: '#ffffff'
  tertiary-container: '#362500'
  on-tertiary-container: '#ad8a46'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b3c5ff'
  on-primary-fixed: '#00174a'
  on-primary-fixed-variant: '#2a4386'
  secondary-fixed: '#aaf1d2'
  secondary-fixed-dim: '#8ed5b7'
  on-secondary-fixed: '#002116'
  on-secondary-fixed-variant: '#00513b'
  tertiary-fixed: '#ffdea5'
  tertiary-fixed-dim: '#e9c176'
  on-tertiary-fixed: '#261900'
  on-tertiary-fixed-variant: '#5d4201'
  background: '#fcf9f8'
  on-background: '#1b1c1c'
  surface-variant: '#e5e2e1'
typography:
  display-lg:
    fontFamily: Montserrat
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Montserrat
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
  headline-md:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Montserrat
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Montserrat
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Montserrat
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  caption:
    fontFamily: Montserrat
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 80px
---

## Brand & Style

This design system embodies a "High-Performance Heritage" aesthetic. It merges the urgency of athletic energy with the restraint of luxury editorial design. The target audience values precision, longevity, and status, requiring a UI that feels both technologically advanced and classically rooted.

The visual style is a hybrid of **Corporate Modern** and **Minimalism**, utilizing expansive whitespace (via the Cream background) to allow the heavy-hitting primary colors to anchor the experience. It avoids fleeting trends like glassmorphism in favor of solid forms, intentional depth, and a high-contrast palette that evokes the feeling of a premium sporting club or a high-end fintech platform.

## Colors

The palette is anchored by **Royal Blue**, providing a foundation of authority and kinetic energy. **Imperial Green** serves as the primary accent, used to denote growth, success, and secondary actions. 

- **Primary (Royal Blue):** Used for main CTAs, headers, and active states.
- **Secondary (Imperial Green):** Used for success states, supplemental buttons, and highlight accents.
- **Background (Cream):** Replaces pure white to reduce eye strain and inject a sense of warmth and premium quality.
- **Surface (Off-White):** Used for cards and nested containers to create subtle separation from the main background.
- **Tertiary (Metallic Gold/Bronze):** To be used sparingly for high-tier badges or premium features.

## Typography

Montserrat is the sole typeface, utilized across all levels to maintain a cohesive, geometric, and energetic feel. To ensure the "sophisticated" aspect of the brief, tracking is slightly tightened on large headlines and widened on small labels.

- **Headlines:** Use Bold (700) or SemiBold (600) weights. High-contrast color (Royal Blue) should be applied to primary headings.
- **Body:** Regular (400) weight is preferred for readability against the Cream background.
- **Labels:** Use Medium (500) or SemiBold (600) with uppercase transformation for a "button-like" or "meta-data" appearance.

## Layout & Spacing

The design system utilizes a **12-column fluid grid** for desktop and a **4-column grid** for mobile. The spacing rhythm is based on a strict **8px root**, ensuring mathematical harmony across all components.

- **Containers:** Max-width of 1280px for desktop layouts to maintain readability.
- **Padding:** Use "Generous Breathing Room" (24px+) for card internals to reinforce the premium feel.
- **Mobile Reflow:** Elements should stack vertically, with horizontal margins shrinking to 16px to maximize screen real estate while maintaining the 8px baseline grid alignment.

## Elevation & Depth

To maintain a refined look, depth is communicated through **Tonal Layering** and **Soft Ambient Shadows**. We avoid harsh black shadows.

- **Level 0 (Background):** Cream (#FFFDD0).
- **Level 1 (Cards/Surfaces):** Off-White (#F9F8F0) with a 1px stroke of Royal Blue at 5% opacity.
- **Level 2 (Elevated):** Subtle shadow (0px 4px 20px) using a Royal Blue tint at 8% opacity.
- **Interactions:** Hover states should not only shift shadow depth but also slightly deepen the background color of the component.

## Shapes

The shape language is defined by **Round Eight (0.5rem)** logic. This provides a soft, modern feel that avoids the "childish" nature of full pills while steering clear of the "aggressive" nature of sharp corners.

- **Standard Elements:** 8px (0.5rem) corner radius.
- **Large Containers/Cards:** 16px (1rem) corner radius.
- **Small Elements (Tags/Badges):** 4px (0.25rem) corner radius.

## Components

### Buttons
- **Primary:** Royal Blue background, White text. 8px radius. Heavy padding (12px 24px).
- **Secondary:** Imperial Green background, White text. Used for "Add," "Success," or "Secondary Action."
- **Outline:** Royal Blue 2px border, Cream background, Royal Blue text.

### Input Fields
- Background should be a slightly darker off-white to distinguish from the card surface.
- Border-bottom (2px) in Royal Blue is preferred over full borders for a cleaner, editorial look.
- Focus state: Increase border-bottom thickness or add a subtle Royal Blue glow.

### Cards
- Surfaces use the Off-White variable.
- Use 16px (rounded-lg) corners to differentiate from smaller UI components.
- Padding should be consistent at 24px (md).

### Chips & Badges
- Small, uppercase labels.
- Backgrounds should be low-opacity versions of the Primary or Secondary colors (e.g., Imperial Green at 10% opacity with 100% opacity text).

### Lists
- Use thin dividers (1px) in a light grey or a 10% tint of Royal Blue.
- Active list items should use a left-edge "accent bar" in Imperial Green.