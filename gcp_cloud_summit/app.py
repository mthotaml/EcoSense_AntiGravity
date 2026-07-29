from flask import Flask, render_template, jsonify, request
import sys
import os

# Add data folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data'))
from talks_data import EVENT_INFO, TALKS, CATEGORIES

app = Flask(__name__)

@app.route('/')
def index():
    """Render the conference home page."""
    return render_template(
        'index.html',
        event=EVENT_INFO,
        talks=TALKS,
        categories=CATEGORIES
    )

@app.route('/api/talks', methods=['GET'])
def get_talks():
    """API endpoint to fetch talks with optional filtering by query, category, or speaker."""
    query = request.args.get('search', '').strip().lower()
    category_filter = request.args.get('category', '').strip()
    speaker_filter = request.args.get('speaker', '').strip().lower()

    filtered_talks = []

    for talk in TALKS:
        # Category check
        if category_filter and category_filter.lower() != 'all' and talk['category'].lower() != category_filter.lower():
            continue

        # Speaker check
        if speaker_filter:
            speaker_match = any(
                speaker_filter in f"{s['first_name']} {s['last_name']}".lower()
                for s in talk['speakers']
            )
            if not speaker_match:
                continue

        # General Search Query check (Title, Category, Speakers, Description)
        if query:
            title_match = query in talk['title'].lower()
            category_match = query in talk['category'].lower()
            description_match = query in talk['description'].lower()
            speaker_match = any(
                query in s['first_name'].lower() or
                query in s['last_name'].lower() or
                query in f"{s['first_name']} {s['last_name']}".lower() or
                query in s['company'].lower()
                for s in talk['speakers']
            )

            if not (title_match or category_match or description_match or speaker_match):
                continue

        filtered_talks.append(talk)

    return jsonify({
        "status": "success",
        "total": len(filtered_talks),
        "talks": filtered_talks,
        "lunch_break": EVENT_INFO["lunch_break"]
    })

@app.route('/api/talk/<int:talk_id>', methods=['GET'])
def get_talk_detail(talk_id):
    """API endpoint to get single talk detail."""
    talk = next((t for t in TALKS if t['id'] == talk_id), None)
    if talk:
        return jsonify({"status": "success", "talk": talk})
    return jsonify({"status": "error", "message": "Talk not found"}), 404

@app.route('/api/event-info', methods=['GET'])
def get_event_info():
    """API endpoint to fetch event metadata."""
    return jsonify({
        "status": "success",
        "event": EVENT_INFO,
        "categories": CATEGORIES
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Google Cloud Tech Summit 2026 server on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
