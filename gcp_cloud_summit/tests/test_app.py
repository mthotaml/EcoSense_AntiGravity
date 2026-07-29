import unittest
import sys
import os

# Add parent dir to path to import app and data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.talks_data import TALKS, EVENT_INFO

class GCPConferenceAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage_loads(self):
        """Test home page loads successfully with 200 status code."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Google Cloud Tech Summit 2026', response.data)
        self.assertIn(b'October 15, 2026', response.data)

    def test_api_get_all_talks(self):
        """Test API returns 8 total talks and lunch break information."""
        response = self.app.get('/api/talks')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['talks']), 8)
        self.assertIn('lunch_break', data)
        self.assertEqual(data['lunch_break']['duration_minutes'], 60)

    def test_api_filter_by_category(self):
        """Test API filtering by Category."""
        response = self.app.get('/api/talks?category=AI%20%26%20Machine%20Learning')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data['talks']) > 0)
        for talk in data['talks']:
            self.assertEqual(talk['category'], 'AI & Machine Learning')

    def test_api_search_by_speaker(self):
        """Test API search by speaker name."""
        response = self.app.get('/api/talks?search=Elena')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['talks']), 1)
        self.assertEqual(data['talks'][0]['speakers'][0]['first_name'], 'Elena')

    def test_api_search_by_title(self):
        """Test API search by talk title keyword."""
        response = self.app.get('/api/talks?search=FinOps')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['talks']), 1)
        self.assertIn('FinOps', data['talks'][0]['title'])

    def test_api_get_talk_by_id(self):
        """Test API single talk endpoint."""
        response = self.app.get('/api/talk/1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['talk']['id'], 1)
        self.assertIn('linkedin', data['talk']['speakers'][0])

    def test_api_get_event_info(self):
        """Test API event info endpoint."""
        response = self.app.get('/api/event-info')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['event']['name'], 'Google Cloud Tech Summit 2026')

if __name__ == '__main__':
    unittest.main()
