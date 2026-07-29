# 🎧 EchoSense — Contextual Music Intelligence & Continuous Playback Platform

> **EchoSense is the driver; the listener is the passenger.**

Source-of-truth implementation for **EchoSense** — a Spotify-connected contextual music intelligence platform with provider-neutral Music DNA, 35% capped contextual ranker, 5-track Music DNA Autopilot, factor explainability, and Guardian Release Gate v2.

---

## 🌟 Key Architectural Features

1. **Provider-Neutral Music DNA**:
   - Ingests top artists, top tracks, recent tracks, and library saves.
   - Computes long-term taste affinities independent of provider catalogs.

2. **Contextual Candidate Ranker**:
   - Enforces **35% Max Context Influence Cap** (durable taste always dominates).
   - Enforces **Music DNA Floor** ($< 0.20$ affinity excluded).
   - Enforces **Explicit Negative Overrides** (dislikes/skips outrank inferred context).
   - **Diversity Guard**: ISRC/slug deduplication, max 2 tracks per artist in preview, adjacent artist penalty.

3. **Continuous Music DNA Autopilot**:
   - Maintains **5 distinct tracks ahead** in the queue preview.
   - Auto-replenishes queue after track completion, verified skip, or context changes.
   - Keeps active playback track identity separate from future candidate recommendations.

4. **Temporal Listening Pattern Learner**:
   - Identifies stable patterns requiring $\ge 3$ positive events across $\ge 2$ distinct days in a rolling 28-day window.
   - Isolates morning and evening patterns.
   - 7-day decay half-life for recent listening shifts.
   - Manual pattern correction & memory reset capabilities.

5. **Governance & Privacy**:
   - Decision provenance logging (candidate slate, factor scores, context, chosen item).
   - Outcome idempotency (using `outcome_id` primary key).
   - Full consent data deletion & receipt generation (`POST /api/consent/delete`).

---

## 📁 Repository Structure

```
echosense/
├── src/
│   └── echosense/
│       ├── config.py             # Settings, Fernet keys, Spotify OAuth config
│       ├── security.py           # Token encryption (Fernet), OAuth PKCE, privacy sanitization
│       ├── db.py                 # SQLite ORM schemas (Users, DNA, Decisions, Outcomes, Consents)
│       ├── provider/
│       │   ├── spotify.py        # Spotify API adapter (OAuth PKCE, retries, 429/5xx handling)
│       │   └── models.py         # Provider-neutral models (Artist, Track, PlaybackState)
│       ├── dna/
│       │   ├── profile.py        # Music DNA normalization & affinity scoring
│       │   └── ranker.py         # Candidate ranker (35% context cap, DNA floor, diversity)
│       ├── context/
│       │   ├── resolver.py       # Live context resolution (Daypart, Weather, Activity)
│       │   └── temporal.py       # Temporal pattern learner (28-day window, 3 events / 2 days)
│       ├── autopilot.py          # Continuous Autopilot (5 distinct tracks ahead)
│       ├── governance.py         # Decision provenance & consent data deletion
│       └── product_app.py        # FastAPI server & REST API routes
├── templates/
│   └── index.html                # Responsive accessible interface
├── static/
│   ├── css/style.css             # WCAG AA accessible design system
│   └── js/app.js                 # Client controller & factor explanation tooltips
├── scripts/
│   └── release_gate.py           # Guardian Release Gate v2 runner
├── tests/
│   ├── test_dna_ranker.py        # Ranker unit tests
│   ├── test_spotify_adapter.py    # Adapter & PKCE unit tests
│   ├── test_temporal_patterns.py # Temporal learning unit tests
│   └── test_api_routes.py        # API route integration tests
└── README.md
```

---

## 🚀 Execution & Guardian Release Gate

### 1. Run Guardian Release Gate v2
```bash
cd echosense
python scripts/release_gate.py
```

Expected Output:
```json
{
  "schema_version": 2,
  "browser_gate_executed": true,
  "release_ready": true
}
```

### 2. Launch FastAPI Web Application
```bash
python -m uvicorn echosense.product_app:app --app-dir src --host 127.0.0.1 --port 8001
```
Open **[http://127.0.0.1:8001](http://127.0.0.1:8001)** in your browser!

---

## 📜 License
MIT License.
