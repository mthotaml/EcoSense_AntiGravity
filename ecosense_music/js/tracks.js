/**
 * EcoSense Music - Track Catalog & Audio Registry
 */

const TRACKS = [
    {
        id: 1,
        title: "Amazonian Rainforest Symphony",
        artist: "EcoSense Ambient Ensemble",
        album: "Earth Harmonies Vol. I",
        category: "Nature Soundscapes",
        duration: "03:45",
        durationSec: 225,
        cover: "https://images.unsplash.com/photo-1511497584788-876761c1298b?w=400&auto=format&fit=crop&q=80",
        audioUrl: "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=rainforest-ambient-111154.mp3",
        ecoTag: "🌿 100% Acoustic Nature Recording"
    },
    {
        id: 2,
        title: "Solar Drift 432Hz Deep Focus",
        artist: "Solaris Ambient Project",
        album: "Cosmic Equilibrium",
        category: "Deep Focus",
        duration: "04:12",
        durationSec: 252,
        cover: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&auto=format&fit=crop&q=80",
        audioUrl: "https://cdn.pixabay.com/download/audio/2021/09/06/audio_4039891823.mp3?filename=ambient-piano-logo-16535.mp3",
        ecoTag: "⚡ Solar-Powered Studio Master"
    },
    {
        id: 3,
        title: "Green Leaf Coffee Lo-Fi",
        artist: "Botanical Chill",
        album: "Organic Beats",
        category: "Eco Lo-Fi Beats",
        duration: "02:30",
        durationSec: 150,
        cover: "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=400&auto=format&fit=crop&q=80",
        audioUrl: "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3?filename=lofi-study-112191.mp3",
        ecoTag: "☕ Low Energy Audio Compressed"
    },
    {
        id: 4,
        title: "Zen Bowl & Mountain Reverie",
        artist: "Kyoto Meditation Club",
        album: "Mindful Serenity",
        category: "Meditation & Calm",
        duration: "05:10",
        durationSec: 310,
        cover: "https://images.unsplash.com/photo-1518241353330-0f7941c2d9b5?w=400&auto=format&fit=crop&q=80",
        audioUrl: "https://cdn.pixabay.com/download/audio/2022/10/14/audio_9939f73809.mp3?filename=meditation-relaxing-music-123456.mp3",
        ecoTag: "🧘 Resonant Tibetan Frequency"
    },
    {
        id: 5,
        title: "Pacific Ocean Tidal Whispers",
        artist: "Coastal Echoes",
        album: "Earth Harmonies Vol. I",
        category: "Nature Soundscapes",
        duration: "03:20",
        durationSec: 200,
        cover: "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=400&auto=format&fit=crop&q=80",
        audioUrl: "https://cdn.pixabay.com/download/audio/2022/02/07/audio_c1c4f52611.mp3?filename=ocean-waves-ambient-109411.mp3",
        ecoTag: "🌊 Recorded at Big Sur, CA"
    },
    {
        id: 6,
        title: "Binaural Forest Breeze",
        artist: "NeuroCalm Labs",
        album: "Cognitive Resonance",
        category: "Deep Focus",
        duration: "04:45",
        durationSec: 285,
        cover: "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&auto=format&fit=crop&q=80",
        audioUrl: "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=soft-rain-ambient-111153.mp3",
        ecoTag: "🌲 Alpha Wave Entrainment"
    },
    {
        id: 7,
        title: "Midnight Garden Lo-Fi Study",
        artist: "Botanical Chill",
        album: "Organic Beats",
        category: "Eco Lo-Fi Beats",
        duration: "02:55",
        durationSec: 175,
        cover: "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=400&auto=format&fit=crop&q=80",
        audioUrl: "https://cdn.pixabay.com/download/audio/2022/05/16/audio_db6591201e.mp3?filename=chill-lofi-song-8444.mp3",
        ecoTag: "🌙 Night Mode Optimized"
    },
    {
        id: 8,
        title: "Emerald Flow Sanctuary Waves",
        artist: "Kyoto Meditation Club",
        album: "Mindful Serenity",
        category: "Meditation & Calm",
        duration: "06:00",
        durationSec: 360,
        cover: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&auto=format&fit=crop&q=80",
        audioUrl: "https://cdn.pixabay.com/download/audio/2022/03/10/audio_517f8b9649.mp3?filename=deep-meditation-109412.mp3",
        ecoTag: "✨ Deep Healing Resonance"
    }
];

const CATEGORIES = [
    "All Playlists",
    "Nature Soundscapes",
    "Deep Focus",
    "Eco Lo-Fi Beats",
    "Meditation & Calm"
];

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TRACKS, CATEGORIES };
}
