# 🌿 EcoSense Music — Sustainable Ambient & Audio Visualizer App

An eco-inspired music and ambient soundscape player web application featuring a real-time **Canvas Audio Spectrum Visualizer**, curated nature and focus playlists, and an interactive **Eco Energy Saver Mode**.

---

## 🌟 Core Features

1. **Interactive Music & Soundscape Player**:
   - Play, Pause, Next, Previous track controls.
   - Interactive progress bar with click-to-seek and dynamic time display (`MM:SS`).
   - Volume slider with Mute toggle.
   - Repeat Mode (Off, All, Single Track) & Shuffle mode.

2. **Real-Time Canvas Audio Spectrum Visualizer**:
   - Web Audio API `AnalyserNode` connected to an interactive `<canvas>` element.
   - Frequency spectrum wave animation with emerald/teal gradients reacting to audio playback.

3. **Curated Ambient & Nature Categories**:
   - 🌿 **Nature Soundscapes** (*Amazonian Rainforest Symphony, Pacific Ocean Tidal Whispers*)
   - 🧠 **Deep Focus** (*Solar Drift 432Hz, Binaural Forest Breeze*)
   - 🎧 **Eco Lo-Fi Beats** (*Green Leaf Coffee, Midnight Garden*)
   - 🧘 **Meditation & Calm** (*Zen Bowl & Mountain Reverie, Emerald Flow Sanctuary*)

4. **Eco Energy Saver Mode**:
   - Toggleable low-bandwidth streaming mode displaying carbon offset metrics (`-35% Carbon Emissions & Low-Bandwidth Streaming`).

5. **Aesthetic Design System**:
   - Deep dark slate/forest background (`#07100C`), glassmorphism cards (`backdrop-filter: blur(24px)`), glowing emerald accents (`#10B981`), and modern typography (*Outfit* & *Plus Jakarta Sans*).

---

## 📁 Repository Structure

```
ecosense_music/
├── index.html        # SPA HTML layout with Canvas visualizer & sticky player bar
├── css/
│   └── style.css     # Eco dark design system & glassmorphism stylesheet
├── js/
│   ├── tracks.js     # Track metadata catalog & audio stream URLs
│   ├── audio.js      # Web Audio API engine & Canvas spectrum visualizer
│   ├── player.js     # Audio playback core engine (Play, Seek, Volume, Queue)
│   └── app.js        # UI controller & player event binding
├── tests/
│   └── test_app.js   # Automated unit test suite
└── README.md         # Setup, features, and usage documentation
```

---

## 🚀 Quickstart: How to Run

### Run via Python HTTP Server
```bash
cd ecosense_music
python3 -m http.server 8090
```
Then open **`http://127.0.0.1:8090`** in your web browser!

---

## 🧪 Running Automated Tests

Run the test suite using Node.js:
```bash
node tests/test_app.js
```

---

## 📜 License
MIT Open Source License.
