# ☁️ Google Cloud Tech Summit 2026 - 1-Day Technical Conference Web Application

A full-stack web application for a **1-Day Google Cloud Technical Conference**. Built with **Python and Flask** on the server side, and modern **HTML5, CSS3, and JavaScript** on the front end.

---

## ✨ Key Features & Functional Requirements

1. **Event Information Header**: Displays current event date (*October 15, 2026*), venue location (*Moscone Center West, San Francisco & Virtual Stream*), and schedule metrics.
2. **8 Technical Talks**: Covers 8 deep-dive sessions centered around Google Cloud technologies (Vertex AI, GKE, BigQuery, Cloud Run, AlloyDB, FinOps, etc.).
3. **1 to 2 Speakers Per Talk**: Each speaker profile contains First Name, Last Name, Role, Company, and a direct **LinkedIn profile link**.
4. **Structured Talk Schema**: Each talk possesses `ID`, `Title`, `Speakers`, `Category`, `Description`, `Time of talk`, and `Room`.
5. **60-Minute Lunch Break**: Prominently scheduled between Talk #4 and Talk #5 (12:15 PM - 1:15 PM) for networking and keynotes.
6. **Instant Live Search & Filtering**: 
   - **Search Box**: Real-time filtering by talk title, speaker first/last name, company, or keyword.
   - **Category Pills**: Instant single-click filtering across 4 Google Cloud tech categories (*AI & Machine Learning*, *Cloud Infrastructure & Security*, *Data Analytics & Databases*, *Serverless & DevOps*).
7. **Interactive Talk Detail Modal**: Click any talk to open a detailed modal with abstract, full speaker bios, and clickable LinkedIn links.
8. **Modern Aesthetic**: Built with a custom glassmorphism dark theme inspired by Google Cloud branding.

---

## 📁 Repository & Project Architecture

```
gcp_cloud_summit/
├── app.py                 # Core Flask Web Application & REST API endpoints
├── data/
│   └── talks_data.py      # Conference dataset (Event metadata, 8 talks, speakers, lunch break)
├── static/
│   ├── css/
│   │   └── style.css      # Design system, glassmorphic dark theme, responsive grid
│   └── js/
│       └── main.js        # Dynamic DOM filter engine, search listener & modal logic
├── templates/
│   └── index.html         # Main Jinja2 HTML layout & template structure
├── tests/
│   └── test_app.py        # Automated test suite for Flask endpoints & search logic
├── requirements.txt       # Python dependencies (Flask)
└── README.md              # Project documentation, setup, and developer guide
```

---

## 🚀 Quickstart Guide: How to Setup and Run

### Prerequisites
- Python 3.9+ installed on your machine.
- `pip` (Python package manager).

### Step 1: Create a Virtual Environment (Recommended)
Open your terminal inside the project directory:
```bash
cd gcp_cloud_summit
python3 -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Launch the Web Application
```bash
python app.py
```
By default, the server will start on **`http://127.0.0.1:5000`** (or `http://localhost:5000`).

Open your browser and navigate to `http://127.0.0.1:5000` to review the live site!

---

## 🧪 Running Automated Tests

Run the test suite using `unittest` or `pytest`:

```bash
# Using Python unittest
python -m unittest tests/test_app.py

# Or using Pytest
pytest tests/test_app.py
```

The test suite validates:
- Homepage rendering (200 OK)
- Endpoint `/api/talks` returning all 8 talks and the 60-minute lunch break
- Filtering by category (e.g. `AI & Machine Learning`)
- Searching by speaker name (e.g. `Elena`)
- Searching by title keyword (e.g. `FinOps`)
- Individual talk details (`/api/talk/1`)

---

## 🛠️ How to Make Further Changes

### 1. Adding or Modifying Talks / Speakers
To update talk schedules or add new speakers, edit `data/talks_data.py`.

Example talk object format:
```python
{
    "id": 9,
    "title": "Your Custom Talk Title",
    "category": "AI & Machine Learning",
    "time": "04:35 PM - 05:20 PM",
    "description": "Abstract description of the session...",
    "room": "Track A - Main Auditorium",
    "speakers": [
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "role": "Cloud Architect",
            "company": "Google",
            "avatar": "https://images.unsplash.com/...",
            "linkedin": "https://www.linkedin.com/in/janedoe"
        }
    ]
}
```

### 2. Customizing Styling or Theme Colors
Edit `static/css/style.css`. Key CSS variables can be modified at the top of the file:
```css
:root {
    --bg-dark: #090D16;
    --gcp-blue: #4285F4;
    --gcp-red: #EA4335;
    --gcp-yellow: #FBBC04;
    --gcp-green: #34A853;
}
```

### 3. Adding New API Routes
Edit `app.py` to add new Flask server routes or microservices.

---

## 🌐 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Render the HTML Conference Home Page |
| `/api/talks` | `GET` | Return JSON list of talks. Supports `?search=query` and `?category=name` |
| `/api/talk/<id>` | `GET` | Return JSON detail for a specific talk ID |
| `/api/event-info` | `GET` | Return JSON event metadata and category lists |

---

## 📜 License
This project is open-source and available under the MIT License.
