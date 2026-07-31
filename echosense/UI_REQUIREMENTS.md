# EchoSense UI Requirements & Design System Specification

## 1. Executive Summary & Design Philosophy
EchoSense is an explainable, cognitive context-aware music recommendation platform. The user interface (UI) is designed around transparency, auditability, user agency, and modern dark-mode aesthetic excellence.

Key UI principles:
- **Instant Visual Clarity**: Dark glassmorphic container aesthetics paired with vibrant accent indicators (`#1ed760` Spotify green, `#64b5f6` cognitive blue).
- **Explainability First**: Every recommendation presents human-readable "Why in Queue" badges and detailed 4-factor scoring breakdowns.
- **Unified Single-Player Model**: Audio playback is anchored to a single persistent player bar to prevent multi-audio streaming conflicts.
- **Privacy & Governance Transparency**: Direct user controls for data consent, context resolution toggles, and one-click consent-derived data deletion.

---

## 2. Color Palette & Typography Tokens

### 2.1 Color Tokens
| Name | Hex / Value | Usage |
| :--- | :--- | :--- |
| **Background Base** | `#0a0a0c` | Body background, root application container |
| **Card Surface** | `rgba(24, 24, 28, 0.75)` | Floating glassmorphic section cards |
| **Glass Border** | `rgba(255, 255, 255, 0.08)` | Card borders, table row dividers |
| **Accent Primary (Spotify Green)** | `#1ed760` | Primary action buttons, play triggers, active state indicators |
| **Accent Secondary (Cognitive Blue)** | `#64b5f6` | Cognitive memory headers, semantic badge highlights |
| **Accent Warning (Amber)** | `#ffb74d` | Working memory indicators, pending learning state |
| **Accent Danger (Red)** | `#ff5252` | Data deletion triggers, consent revoking badges |
| **Text Primary** | `#ffffff` | Headings, main track titles, hero text |
| **Text Secondary** | `#a0a0a0` | Subtitles, artist names, metadata labels |
| **Text Muted** | `#666666` | Footers, privacy disclaimers, mathematical formulas |

### 2.2 Typography System
- **Font Family**: System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`).
- **Heading 1 (`<h1>`)**: `1.75rem` (28px), Weight `700`, Line Height `1.2`.
- **Heading 2 (`<h2>`)**: `1.35rem` (21.6px), Weight `600`, Line Height `1.3`.
- **Section Heading (`<h3>`)**: `1.1rem` (17.6px), Weight `600`.
- **Body Text**: `0.95rem` (15.2px), Weight `400`, Line Height `1.5`.
- **Badge / Caption**: `0.75rem` - `0.85rem` (12-13.6px), Weight `600`.

---

## 3. UI Layout & Component Specifications

### 3.1 Global Header & Navigation Bar
- **Brand Logo**: EchoSense icon with gradient audio wave logo.
- **Connection Status**:
  - `Connected` badge (green pulse dot + user display name).
  - `Disconnected` state featuring a "Connect Spotify" CTA button.
- **Quick Controls**: Context resolver toggle button, Settings drawer trigger.

### 3.2 Hero Recommendation Card ("Today's Contextual Pick")
- **Layout**: 2-column card featuring high-resolution album art (`160x160px` with rounded corners `12px`) on the left, details and controls on the right.
- **Track Metadata**: Large track title, artist name, category/genre tag badge.
- **Why-in-Queue Section**:
  - Human-readable reason pill (e.g. `✨ Matched for Morning Commute during Rainy weather`).
- **4-Factor Score Breakdown Progress Bars**:
  1. **Music DNA Affinity** (60% weight floor): Green progress bar.
  2. **Live Context Fit** (Capped at max 35%): Blue progress bar.
  3. **Learned Preference** ([-0.20, +0.20] adjustment): Amber progress bar.
  4. **Diversity Guard** (Max 2 tracks per artist cap): Purple progress bar.
- **Interactive Action Bar**:
  - `▶ Play Recommendation` button (`#1ed760` background, dark text).
  - `♥ Save` button (saves to user library).
  - `⏭ Skip Track` button (records counterfactual skip feedback).

### 3.3 Persistent Spotify Player Bar
- **Position**: Sticky bottom or anchored iframe player.
- **Behavior**: Uses official Spotify Embed Web Player (`https://open.spotify.com/embed/track/{track_id}`).
- **Sync Rule**: Automatically updates iframe `src` to the active track's 22-character Spotify ID when `▶ Play` is clicked anywhere on the page.

### 3.4 Continuous Autopilot Queue Table
- **Header**: Section title (`<i class="fa-solid fa-list-ol"></i> Autopilot Queue`), page count indicator (`Page X of Y`), and page quick-jump buttons (`1, 2, 3...`).
- **Table Columns**:
  1. `#` (Rank position).
  2. `Track & Artist` (Album thumbnail `44x44px`, title, artist).
  3. `Category / Genre` (Badge pill).
  4. `Affinity & Factors` (Score breakdown + interactive `i` info icon).
  5. `Actions` (Play button, Like button, Dislike button, Skip button).
- **Load More DNA Tracks**: `[ + Load More DNA Tracks ]` CTA button at the bottom of the table to dynamically expand the queue.

### 3.5 Cognitive Memory Store Inspector Card
- **Grid Layout**: 3-column responsive card grid.
- **Card 1 — Episodic Memory**:
  - Timestamped experience logs (e.g. `• Morning commute stream (Confidence: 0.92)`).
- **Card 2 — Semantic Propositions**:
  - Active subject-predicate-object propositions (e.g. `• Listener → Prefers Category: Eco Lo-Fi Beats [active]`).
- **Card 3 — Working Memory (Expiring)**:
  - Short-lived expiring reasoning context (e.g. `• Current Focus: Deep Work & Scenic Driving`).

### 3.6 Live Context Resolution Panel
- **Status Toggle**: `[x] Factor Live Context in DNA Queue` toggle switch.
- **Interactive Context Chips**:
  - `Daypart`: Morning, Afternoon, Evening, Night.
  - `Weather`: Rainy, Clear, Cloudy, Stormy.
  - `Road Setting`: Scenic, Highway, Urban.
  - `Activity`: Focus, Relaxation, Workout, Commute.

### 3.7 Data Privacy & Governance Control Center
- **Consent Toggles**:
  - `Contextual Recommendations` (Enable/Disable).
  - `Data Retention` (Enable/Disable).
- **Right to be Forgotten Button**:
  - `[ Delete All My Data ]` button with confirmation modal.
  - On execution, displays a cryptographically verifiable deletion receipt modal containing `receipt_id`, timestamp, and count of deleted records.

### 3.8 Factor Explanation Info Modal (`i` Modal)
- Triggered by clicking any `i` info icon in the table or factor bars.
- Modal displays:
  - Header with factor icon and name.
  - Mathematical formula box (e.g. `DNA Affinity = (0.60 × Artist Affinity) + (0.40 × Category Fit)`).
  - Detailed explanation bullet points.

---

## 4. Responsive Layout & Breakpoints

```css
/* Responsive Grid System */
@media (max-width: 1024px) {
  .hero-card-content {
    grid-template-columns: 1fr;
  }
  .cognitive-memory-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .chips-container {
    flex-direction: column;
  }
  .autopilot-table {
    display: block;
    overflow-x: auto;
  }
}
```

---

## 5. API Mappings for UI Components

| Component | Trigger Action | API Endpoint | HTTP Method |
| :--- | :--- | :--- | :--- |
| **Hero / Queue Play** | Click `▶ Play` | `/api/play` | `POST` |
| **Queue Skip** | Click `⏭ Skip` | `/api/skip` | `POST` |
| **Feedback (Like/Dislike)** | Click `👍` or `👎` | `/api/feedback` | `POST` |
| **Cognitive Memory** | Page Load | `/api/memory` | `GET` |
| **Context Switch** | Select Context Chip | `/api/context` | `POST` |
| **Data Deletion** | Click `Delete All Data` | `/api/consent/delete` | `POST` |
| **Spotify Auth** | Click `Connect Spotify` | `/auth/spotify` | `GET` |
