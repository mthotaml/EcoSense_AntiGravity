# 🧘 Zen Pomodoro — Mindful Focus & Ambient Productivity App

A serene, highly aesthetic Pomodoro productivity web application designed to promote calm concentration, reduce stress, and boost deep work efficiency.

---

## 🌟 Key Features

1. **Serene Visual Aesthetics & Theme Switcher**:
   - Customizable color themes:
     - 🌿 **Calm Forest** (Sage green & mist white)
     - 🌅 **Sunset Zen** (Warm terracotta & soft gold)
     - 🌌 **Midnight Minimal** (Deep indigo & soft lavender)
     - ☕ **Soft Latte** (Warm beige & mocha)
   - Soft glassmorphic containers (`backdrop-filter: blur(24px)`), smooth drop shadows, and ambient background glow orbs.

2. **Circular SVG Progress Ring & Timer Engine**:
   - 3 Modes: **Focus (25m)**, **Short Break (5m)**, and **Long Break (15m)**.
   - Smooth animated circular SVG ring displaying elapsed vs remaining time.
   - Hotkey controls: `Spacebar` (Start/Pause), `S` (Skip), `R` (Reset).
   - Dynamic tab title updating (e.g. `24:59 - Focus | Zen Pomodoro`).

3. **Procedural Ambient Soundscapes (Web Audio API)**:
   - High-quality, zero-dependency procedural audio generator:
     - 🌧️ **Soft Rain**
     - 🌊 **Ocean Waves**
     - 🌲 **Forest Wind**
     - 🧠 **432Hz Binaural Focus Tone**
     - 🔔 **Tibetan Singing Bowl Chime** alert on session completion.

4. **Integrated Task Management**:
   - Add tasks with estimated Pomodoro counts.
   - Assign active task to current timer session.
   - Auto-increment completed Pomodoro counters per task upon timer completion.

5. **Focus Analytics & Daily Streak Tracker**:
   - Aggregates daily total focus hours & minutes.
   - Tracks completed Pomodoro sessions & consecutive daily streaks.
   - LocalStorage persistence for user preferences, tasks, and history.

---

## 📁 Architecture & File Structure

```
zen_pomodoro/
├── index.html        # App UI layout (Timer, Tasks, Soundscapes, Modals)
├── css/
│   └── style.css     # Design system, themes, SVG ring styling, glassmorphism
├── js/
│   ├── timer.js      # Pomodoro countdown engine & SVG ring animation
│   ├── ambient.js    # Procedural Web Audio API sound generator & chime
│   ├── tasks.js      # Task list controller & LocalStorage persistence
│   ├── stats.js      # Focus analytics & daily streak tracker
│   └── app.js        # Main controller, shortcuts, theme picker & modals
├── tests/
│   └── test_suite.js # Automated test runner for timer math & state logic
└── README.md         # Project documentation
```

---

## 🚀 Quickstart: How to Run Locally

### Option 1: Using Python HTTP Server
Open your terminal in the `zen_pomodoro` directory:
```bash
cd zen_pomodoro
python3 -m http.server 8080
```
Then open **`http://127.0.0.1:8080`** in your browser!

### Option 2: Direct File Opening
You can also directly open `index.html` in any web browser!

---

## 🧪 Running Automated Tests

Run the test suite using Node.js:
```bash
node tests/test_suite.js
```

---

## 📜 License
MIT Open Source License.
