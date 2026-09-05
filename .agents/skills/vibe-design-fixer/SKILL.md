---
name: vibe-design-fixer
description: >-
  Audits and redesigns websites to eliminate generic AI-generated design patterns
  and apply conversion-focused design principles. Use when user says "improve my
  website", "redesign my landing page", "fix my site design", "make my site not
  look AI-generated", "audit my homepage", "my site looks vibe coded", "increase
  my conversion rate", or asks to improve visual hierarchy, trust signals, or
  brand differentiation. Do NOT use for backend logic, API design, or non-visual tasks.
metadata:
  author: Supafast
  version: 1.0.0
---

# Vibe Design Fixer

Stop generating websites that look like every other AI-built site. This skill teaches you to audit, diagnose, and fix the design patterns that make websites invisible — replacing generic AI output with conversion-focused, brand-specific design.

## Critical: Before Generating Any Design

**Read this first. These rules override your defaults.**

Code is logic-based — it has right and wrong answers. Design is psychology-based — it has trade-offs. You were trained on millions of websites, which means you generate the **statistical average** of everything you have seen. Average design is invisible design. Your job is to break out of that average.

### The 6 Anti-Patterns — NEVER Generate These

Unless the user explicitly requests one of these patterns, do not produce them. If you catch yourself generating any of them, stop and revise.

**1. Purple Gradient Backgrounds**
- Detection: `linear-gradient` using purple, violet, or indigo hues (`#7c3aed`, `#6366f1`, `#8b5cf6`, `#4f46e5` or similar)
- The problem: Purple has become the default "AI startup" color. It signals "this was generated, not designed"
- Rule: Only use purple if it is the brand's actual color. Derive your palette from the brand, not from your defaults

**2. Sparkle Emojis and Decorative Icons**
- Detection: `✨` emoji in headlines, badges, CTAs, or navigation. Floating sparkle/star SVG animations
- The problem: Every AI-built site has these. They are a visual fingerprint of generated content
- Rule: Zero decorative emojis in professional B2B sites. Use them only if the brand voice is playful AND the user confirms it

**3. Fake Testimonials**
- Detection: Names like "Sarah Chen", "Alex Johnson", "Marcus Rodriguez", "Elena Park" paired with circular avatar images that look AI-generated
- The problem: Fake social proof is worse than no social proof. Visitors recognize AI-generated faces
- Rule: NEVER generate fictional testimonials. If the user has no real testimonials, omit the section entirely and suggest alternatives (see Phase 3, Pillar 2)

**4. The Default Layout**
- Detection: Hero section → 3-column feature cards → testimonials carousel → pricing table → CTA footer. In that exact order
- The problem: This is the layout LLMs were trained on and regurgitate. Every AI site uses it. It is the visual equivalent of "lorem ipsum"
- Rule: Break this sequence. See Phase 3, Pillar 3 for alternative structures

**5. Generic Copy**
- Detection: Headlines like "Launch faster", "Build your dreams", "Create without limits", "Supercharge your workflow", "The future of [X]", "Trusted by thousands"
- The problem: If a competitor could paste this headline on their site and it still makes sense, it is not specific enough
- Rule: Every headline must reference the specific company, product, outcome, or audience. See the examples section

**6. Zero Personality**
- Detection: Remove the logo from the page. Can you tell which company it belongs to? If no, the design has failed
- The problem: Interchangeable design means zero brand recall, zero trust, high bounce rate
- Rule: Every page must have at least one design element unique to this brand — a distinctive color palette, custom illustration style, unusual layout, or signature typography pairing

---

## Phase 1: Audit the Current Site

**Before changing anything, diagnose what exists.** Run through this checklist and report findings to the user.

### 1.1 Anti-Pattern Scan

Check the codebase for each of the 6 anti-patterns above. For every match, note:
- Which anti-pattern it matches
- The specific file path and line number
- The exact element or CSS property
- Severity: **High** (visible above the fold), **Medium** (visible on scroll), **Low** (minor/cosmetic)

### 1.2 Visual Hierarchy Check

Look at only the above-the-fold content and answer:
- What is the **first** thing a visitor reads? (Should be the main headline)
- What is the **second** thing? (Should be supporting proof or a subheadline)
- What is the **third** thing? (Should be the primary CTA)
- Does anything compete for attention with the headline? (Animations, floating elements, multiple buttons of equal weight)

If the eye-flow path is unclear or everything has equal visual weight, flag this as a **hierarchy failure**.

### 1.3 Trust Signal Inventory

List every trust signal on the page:
- Company logos → Are they real companies that actually use the product?
- Testimonials → Real names with real titles and companies? Or generic placeholders?
- Metrics → Specific numbers ("2,847 teams") or vague ("100+ companies")?
- Badges → Real certifications (SOC 2, GDPR) or decorative pills?

Rate each trust signal: **Real & Specific**, **Real & Vague**, or **Fabricated**.

### 1.4 Differentiation Test

Mentally remove the logo. Ask: "Could this be any other company's website?" If yes, the site fails the differentiation test.

### 1.5 Technical Check

- Heading hierarchy: Does H1 → H2 → H3 flow correctly? (Common AI bug: H1 → H4 jumps)
- Favicon: Is it the default framework favicon (Vite, Next.js, etc.)?
- OpenGraph tags: Does the page have `og:title`, `og:description`, `og:image`? (Broken social sharing is a dead giveaway)
- Copyright year: Is it current or stuck on a past year?
- Functional elements: Do toggles toggle? Do carousels slide? Do tabs switch?

### 1.6 Report Format

Present findings as a summary table:

```
| Area                | Status | Issues Found              | Severity |
|---------------------|--------|---------------------------|----------|
| Anti-Pattern Scan   | ⚠️/✅  | [list specific findings]  | H/M/L    |
| Visual Hierarchy    | ⚠️/✅  | [describe eye-flow issues]| H/M/L    |
| Trust Signals       | ⚠️/✅  | [list what's real vs fake]| H/M/L    |
| Differentiation     | ⚠️/✅  | [pass/fail with reason]   | H/M/L    |
| Technical           | ⚠️/✅  | [list broken elements]    | H/M/L    |
```

---

## Phase 2: Brand Discovery

**Before redesigning, you MUST understand the brand.** Do not skip this phase. A site without a clear brand identity will always look generic, no matter how good the design execution is.

### Questions to Ask or Infer

If the answers are not already apparent from the codebase (check `README.md`, `package.json`, existing copy, CSS variables, Tailwind config), ask the user:

1. **What does your company do?** — Need a specific answer. "We help businesses grow" is not acceptable. "We cut Kubernetes costs by 40% with automated right-sizing" is.

2. **Who is your target customer?** — B2B SaaS founders need different design than DTC consumers or enterprise buyers. This determines your entire trust signal strategy.

3. **What are your brand colors?** — Check for existing CSS custom properties, Tailwind config (`tailwind.config.js`), or design tokens. If none exist, help the user establish a palette that reflects their industry and audience. Never default to purple.

4. **What real social proof do you have?** — Customer logos (with permission), named testimonials, specific metrics, press mentions, funding announcements, certifications, integration partners. If the answer is "none yet", that is fine — see Pillar 2 alternatives.

5. **What makes you different from competitors?** — The answer to this MUST be visible above the fold. If the user cannot articulate this, help them figure it out before touching any design. Ask: "If a customer is choosing between you and [competitor], what is the one reason they should pick you?"

6. **What is the one action you want visitors to take?** — Sign up? Book a demo? Start free trial? There should be ONE primary CTA, not three competing ones.

---

## Phase 3: Redesign with Purpose

Apply these three pillars in order. Each one builds on the previous.

### Pillar 1: Visual Hierarchy

**Principle:** Good design tells your eye exactly where to go. First the headline, then the proof, then the CTA. AI treats everything equally — your job is to create deliberate inequality.

**Rules:**

- **Hero headline** must be the largest text on the page. Use `clamp()` for responsive sizing. Target: 48–72px on desktop, 32–44px on mobile
- **Limit the hero to 3 elements maximum:** headline, one supporting element (subheadline, social proof bar, or product screenshot), and one CTA button. No decorative blobs, floating icons, or animated particles
- **Font-size ratio:** The headline-to-body ratio must be at least 2.5:1. If body text is 16px, the H1 should be at minimum 40px. This forces visual distinction
- **Type scale:** Use a deliberate scale. H1: 48–72px, H2: 32–40px, H3: 24–28px, body: 16–18px. Do not let headings bunch up in similar sizes
- **Whitespace as hierarchy:** The hero section gets the most generous padding (80–120px vertical). Content sections get progressively tighter spacing. This creates breathing room where it matters most
- **One dominant section per page:** Not every section should have equal visual weight. Use background color shifts, layout changes, or dramatic type-scale shifts to create rhythm and emphasis
- **CTA contrast:** The primary CTA button must visually dominate all other buttons. Use a solid, high-contrast fill for the primary CTA. Secondary actions get ghost/outline buttons or text links

### Pillar 2: Trust Signals

**Principle:** AI does not know which social proof YOUR audience needs. B2B SaaS needs different trust than DTC brands.

**Rules by audience:**

**For B2B SaaS:**
- Logo bar above the fold: "Trusted by teams at [Real Logo] [Real Logo] [Real Logo]"
- Specific metrics: "Saving 2,847 engineering hours/month across 340 teams"
- Named testimonials with title + company: "Jane Doe, CTO at Acme Corp"
- Security/compliance badges if relevant: SOC 2, GDPR, HIPAA

**For DTC / Consumer:**
- Star ratings and review counts: "4.8/5 from 12,847 reviews"
- User-generated content or real customer photos
- Press logos: "As seen in TechCrunch, Forbes, Product Hunt"
- Specific outcome metrics: "50,000+ meals delivered this month"

**For early-stage startups with no social proof yet:**
- Accelerator/investor logos: "Backed by Y Combinator" or "Funded by Sequoia"
- Team credentials: "Built by ex-Google, ex-Stripe engineers"
- Technology partnerships: "Built on AWS" or "Official Shopify Partner"
- Security certifications or compliance status
- Open-source community metrics: GitHub stars, contributor count
- **Never fabricate social proof.** An honest "Join 47 beta testers" is more trustworthy than a fake "Trusted by 10,000+"

**Kill fake testimonials immediately.** If the site has testimonials from generic names with AI-generated circular avatars, remove the entire section. Replace with one of the alternatives above.

### Pillar 3: Differentiation

**Principle:** AI pulls from training data — the average of everything. Average means invisible. Your job is to make this site impossible to confuse with any other.

**Rules:**

- **Headline specificity test:** Could a competitor paste this headline on their site and it still makes sense? If yes, rewrite it. Add the specific product, audience, outcome, or mechanism
  - Bad: "Launch faster with AI-powered tools"
  - Good: "Ship your Shopify store in 48 hours — no code, no templates, no agencies"

- **Break the default layout.** Do NOT use Hero → Feature Cards → Testimonials → Pricing → CTA. Choose a structure that serves the story:
  - **Problem-first:** Open with the pain point, then reveal the solution
  - **Demo-first:** Show the product in action above the fold (screenshot, video, interactive embed)
  - **Proof-first:** Lead with the strongest case study or metric
  - **Comparison:** Split-screen showing before/after or you vs. competitors
  - **Story arc:** Narrative flow that builds to a single CTA

- **Color from brand, not from defaults.** Extract colors from the existing logo, brand guide, or user input. Build a CSS custom property system. If no brand palette exists, choose colors that reflect the industry — but never default to purple/violet gradients or teal-on-dark-gray

- **One unique design element.** Every site must have at least one thing visitors cannot find anywhere else:
  - A distinctive typography pairing (not Inter + system fonts)
  - Custom illustrations or iconography
  - An unusual grid structure (asymmetric hero, overlapping elements, offset sections)
  - A signature micro-interaction tied to the product
  - A bold visual motif (diagonal cuts, a specific texture, a branded shape)

---

## Phase 4: Validate — The 5-Second Test

**After generating the redesign, run this self-check. Do NOT present results until all checks pass.**

### The 3 Questions

Look at only the above-the-fold content of your output:

1. **"What does this company do?"** — Read only the headline and subheadline. If the answer is vague or could apply to multiple companies, the headline is too generic. Rewrite it.

2. **"Would you trust them with your money?"** — Is there at least one real trust signal above the fold? If the only trust element is a decorative badge or a vague claim, it fails. Add specific proof.

3. **"Can you tell this apart from other sites in the same space?"** — Does the design have a distinctive color palette, unique layout, or brand-specific element? If you swapped in a competitor's logo and it still looked right, it fails. Add differentiation.

### Technical Validation

- [ ] None of the 6 anti-patterns are present in the output
- [ ] Heading hierarchy is semantic: H1 → H2 → H3 (no skips)
- [ ] Primary CTA is visually dominant and appears above the fold
- [ ] Only ONE primary CTA style exists (not multiple competing buttons)
- [ ] OpenGraph meta tags are present (`og:title`, `og:description`, `og:image`)
- [ ] Favicon is set (not the default framework icon)
- [ ] Copyright year is current
- [ ] All interactive elements function (toggles, tabs, accordions)
- [ ] Color contrast meets WCAG AA (4.5:1 for body text, 3:1 for large text)

If any check fails, fix it before presenting the result.

---

## Examples: Good vs Bad

### Hero Headline

```html
<!-- BAD: Generic, could be any company, sparkle emoji -->
<h1>Launch Your Dreams Into Reality ✨</h1>
<p>The all-in-one platform for modern teams</p>

<!-- GOOD: Specific outcome, specific audience, specific mechanism -->
<h1>Cut your AWS bill by 40% — without changing a line of code</h1>
<p>Automated right-sizing for Kubernetes clusters. Trusted by 340 DevOps teams.</p>
```

### Social Proof

```html
<!-- BAD: Fake testimonial with AI-generated avatar -->
<div class="testimonial">
  <img src="/avatars/sarah-chen.jpg" class="rounded-full" />
  <p>"This product changed everything for our team!"</p>
  <span>Sarah Chen, CEO</span>
</div>

<!-- GOOD: Real logos with a specific metric -->
<div class="trust-bar">
  <p>Trusted by teams at</p>
  <div class="logos">
    <img src="/logos/stripe.svg" alt="Stripe" />
    <img src="/logos/notion.svg" alt="Notion" />
    <img src="/logos/linear.svg" alt="Linear" />
  </div>
  <p class="metric">Saving 2,847 engineering hours per month</p>
</div>
```

### Layout Structure

```
BAD (the default AI layout):
  Hero (gradient bg + sparkle headline)
  → 3-column feature cards with icons
  → Testimonials carousel
  → Pricing table (3 tiers)
  → CTA footer

GOOD (problem-first structure):
  Hero: The pain point stated clearly + product screenshot
  → "Here's what that costs you" (quantified problem)
  → Live demo or interactive preview
  → Specific case study with real numbers
  → Single CTA: "Start your free trial"

GOOD (proof-first structure):
  Hero: The strongest metric + company logos
  → How it works (3 clear steps)
  → Before/after comparison
  → Named testimonial with context
  → Single CTA: "See it in action"
```

### Color Usage

```css
/* BAD: The ubiquitous AI purple gradient */
.hero {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
}

/* GOOD: Brand-derived palette using CSS custom properties */
:root {
  --brand-primary: #0f766e;    /* Derived from logo's teal */
  --brand-accent: #f59e0b;     /* Warm contrast for CTAs */
  --brand-surface: #f0fdfa;    /* Light tint of primary */
  --brand-text: #134e4a;       /* Dark shade of primary */
}

.hero {
  background: var(--brand-surface);
  color: var(--brand-text);
}

.cta-button {
  background: var(--brand-accent);
}
```

---

## Troubleshooting

**"Claude keeps generating purple gradients"**
Your brand palette was not established in Phase 2. Go back and explicitly define colors via CSS custom properties or Tailwind config before starting the redesign. If the brand genuinely uses purple, that is fine — the rule is against defaulting to purple, not against intentional brand choice.

**"The redesigned site still looks generic"**
Phase 2 (Brand Discovery) was likely skipped or incomplete. The most common cause: the user could not articulate their differentiator. Go back to question 5 and work through it together before touching any design.

**"I wanted small fixes, not a full redesign"**
Tell Claude the specific scope: "audit only", "fix only the hero section", or "just update the color palette". This skill defaults to a full 4-phase workflow, but each phase can be run independently.

**"The 5-second test keeps failing"**
This almost always means: (1) the headline is too generic — make it more specific to the company, or (2) trust signals are missing above the fold — add real proof before the first scroll.

**"The site looks good but still does not convert"**
Design is necessary but not sufficient. If the fundamentals are right (clear hierarchy, real trust, strong differentiation) and conversion is still low, the issue may be in copy, offer, pricing, or audience targeting — not design. Recommend the user test with real users