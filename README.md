# 🌿 EcoSense AntiGravity Suite

> **Source-of-Truth Repository for EcoSense Contextual Music Intelligence Platform, EcoSense UI, Sustainable Audio Visualizer, Zen Pomodoro, and Google Cloud Summit Web Application.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com/)

---

## 🎨 User Interfaces & Web Applications

### 1. 🎧 EchoSense Platform UI (`echosense/`)
- **Location**: [`echosense/templates/index.html`](file:///Users/mohan/agetest/echosense/templates/index.html), [`echosense/static/css/style.css`](file:///Users/mohan/agetest/echosense/static/css/style.css), [`echosense/static/js/app.js`](file:///Users/mohan/agetest/echosense/static/js/app.js)
- **Features**:
  - **Global Header**: Spotify connection status pill and disconnect control.
  - **Greeting & Value Banner**: Personalized daypart greeting.
  - **Spotify Integration Card**: OAuth PKCE authorization trigger and healthy connection indicator.
  - **Current Contextual Recommendation**: Hero album cover, track details, match confidence badge, and reason box explaining why the track was selected.
  - **Autopilot 5-Track Queue Table**: Interactive factor score breakdown (*Music DNA Affinity*, *Live Context Fit*, *Learned Preference*, *Diversity Guard*) with accessible tooltips.
  - **Live Context Summary**: Active daypart, weather, region, road setting, and activity moment.
  - **Temporal Listening Pattern Learner**: Detected stable listening patterns, manual correction form, and memory reset button.
  - **Persistent Player Bar**: Active playback track details, progress seekbar, and media controls.

```bash
cd echosense
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python scripts/release_gate.py
./venv/bin/python -m uvicorn echosense.product_app:app --app-dir src --host 127.0.0.1 --port 8012
```

---

### 2. 🌿 EcoSense Music & Audio Visualizer UI (`ecosense_music/`)
- **Location**: [`ecosense_music/index.html`](file:///Users/mohan/agetest/ecosense_music/index.html), [`ecosense_music/css/style.css`](file:///Users/mohan/agetest/ecosense_music/css/style.css), [`ecosense_music/js/player.js`](file:///Users/mohan/agetest/ecosense_music/js/player.js)
- **Features**: Real-time Canvas audio frequency spectrum visualizer, 8 nature/ambient soundscapes, eco lo-fi beats, meditation tracks, sticky player bar.

```bash
cd ecosense_music
python3 -m http.server 8090
```

---

### 3. 🧘 Zen Pomodoro Productivity UI (`zen_pomodoro/`)
- **Location**: [`zen_pomodoro/index.html`](file:///Users/mohan/agetest/zen_pomodoro/index.html)
- **Features**: Animated SVG countdown timer, Web Audio procedural ambient soundscapes (Soft Rain, Ocean Waves, Binaural 432Hz focus tone), task manager, theme picker.

```bash
cd zen_pomodoro
python3 -m http.server 8080
```

---

### 4. ☁️ Google Cloud Tech Summit 2026 UI (`gcp_cloud_summit/`)
- **Location**: [`gcp_cloud_summit/templates/index.html`](file:///Users/mohan/agetest/gcp_cloud_summit/templates/index.html)
- **Features**: 1-Day Technical Conference schedule, 8 Google Cloud talks, 60m lunch break, speaker LinkedIn links, instant category and search filters.

```bash
cd gcp_cloud_summit
./venv/bin/python app.py
```

---

## 📜 License
This repository is licensed under the [MIT License](LICENSE).
