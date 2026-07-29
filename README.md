# 🌿 EcoSense AntiGravity Suite

> **Source-of-Truth Repository for EcoSense Contextual Music Intelligence, Sustainable Audio Visualizer, Zen Pomodoro, and Google Cloud Summit Web Platform.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com/)

---

## 🚀 Projects Included

### 1. 🎧 EchoSense Contextual Music Intelligence Platform (`echosense/`)
- **Architecture**: Provider-neutral Music DNA, Contextual Candidate Ranker with 35% max context cap, 5-track Music DNA Autopilot queue, 28-day rolling window Temporal Pattern Learner.
- **Tech Stack**: FastAPI, Python 3.10+, SQLAlchemy, Cryptography (Fernet token encryption), HTML5, CSS3, JavaScript.
- **Verification**: Guardian Release Gate v2 automated test suite (`python scripts/release_gate.py`).

```bash
cd echosense
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python scripts/release_gate.py
./venv/bin/python -m uvicorn echosense.product_app:app --app-dir src --host 127.0.0.1 --port 8008
```

---

### 2. 🌿 EcoSense Music & Audio Visualizer (`ecosense_music/`)
- **Architecture**: Real-time HTML5 Canvas audio spectrum visualizer, 8 nature/ambient soundscape tracks, eco-mode.
- **Tech Stack**: HTML5, CSS3, Vanilla JavaScript, Web Audio API.

```bash
cd ecosense_music
python3 -m http.server 8090
```

---

### 3. 🧘 Zen Pomodoro Productivity App (`zen_pomodoro/`)
- **Architecture**: Mindful productivity timer with SVG countdown ring, procedural Web Audio ambient soundscapes (Soft Rain, Ocean Waves, Binaural 432Hz focus tones), task manager, and focus stats.

```bash
cd zen_pomodoro
python3 -m http.server 8080
```

---

### 4. ☁️ Google Cloud Tech Summit 2026 Website (`gcp_cloud_summit/`)
- **Architecture**: 1-Day Technical Conference web app featuring 8 talks, 60m lunch break, speaker LinkedIn profiles, instant category and search filters.

```bash
cd gcp_cloud_summit
./venv/bin/python app.py
```

---

## 📜 License
This repository is licensed under the [MIT License](LICENSE).
