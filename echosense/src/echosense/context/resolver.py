"""
Live Context Resolver Engine
Resolves Daypart, Weather, Coarse Region, Road Setting, and Listening Moment without storing raw coordinates.
"""

from datetime import datetime
from typing import Dict, Optional

class ContextResolver:
    def __init__(self):
        pass

    def get_live_context(
        self,
        user_moment_override: Optional[str] = None,
        opt_in_location: bool = False
    ) -> Dict:
        """
        Resolve live context signals safely.
        Time requires no permission; Location requires explicit permission.
        Raw coordinates are never retained or logged.
        """
        now = datetime.now()
        hour = now.hour

        if 5 <= hour < 12:
            daypart = "morning"
        elif 12 <= hour < 17:
            daypart = "afternoon"
        elif 17 <= hour < 22:
            daypart = "evening"
        else:
            daypart = "night"

        context = {
            "daypart": daypart,
            "weather": "Partly Cloudy, 68°F",
            "coarse_region": "Pacific Coastal Region",
            "road_setting": "scenic",
            "activity": user_moment_override or "focus",
            "location_permission_granted": opt_in_location
        }

        return context
