/**
 * EcoSense Music App UI Controller & State Manager
 */

document.addEventListener('DOMContentLoaded', () => {
    if (typeof TRACKS === 'undefined') return;

    // Initialize Player & Visualizer
    const player = new AudioPlayer(TRACKS);
    const canvas = document.getElementById('audioCanvas');
    if (canvas && window.visualizerEngine) {
        window.visualizerEngine.init(player.audio, canvas);
    }

    // DOM Elements
    const trackGrid = document.getElementById('trackGrid');
    const categoryPills = document.getElementById('categoryPills');
    const searchInput = document.getElementById('searchInput');

    // Sticky Player Controls
    const nowPlayingCover = document.getElementById('nowPlayingCover');
    const nowPlayingTitle = document.getElementById('nowPlayingTitle');
    const nowPlayingArtist = document.getElementById('nowPlayingArtist');
    const nowPlayingEcoTag = document.getElementById('nowPlayingEcoTag');

    const playPauseBtn = document.getElementById('playPauseBtn');
    const playPauseIcon = document.getElementById('playPauseIcon');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const shuffleBtn = document.getElementById('shuffleBtn');
    const repeatBtn = document.getElementById('repeatBtn');

    const progressBar = document.getElementById('progressBar');
    const progressFill = document.getElementById('progressFill');
    const currentTimeEl = document.getElementById('currentTime');
    const totalTimeEl = document.getElementById('totalTime');

    const volumeSlider = document.getElementById('volumeSlider');
    const muteBtn = document.getElementById('muteBtn');
    const ecoSaverToggle = document.getElementById('ecoSaverToggle');
    const ecoEnergyCounter = document.getElementById('ecoEnergyCounter');

    let currentCategory = 'All Playlists';
    let searchQuery = '';
    let isEcoSaverActive = false;

    // Load initial track metadata into player bar
    player.loadTrack(0);

    // ==========================================
    // Render Functions
    // ==========================================

    function renderTrackGrid() {
        if (!trackGrid) return;
        trackGrid.innerHTML = '';

        const filtered = player.queue.filter(t => {
            if (!searchQuery) return true;
            return t.title.toLowerCase().includes(searchQuery) ||
                   t.artist.toLowerCase().includes(searchQuery) ||
                   t.category.toLowerCase().includes(searchQuery);
        });

        if (filtered.length === 0) {
            trackGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-compact-disc"></i>
                    <h3>No tracks found</h3>
                    <p>Try searching for a different ambient genre or artist.</p>
                </div>
            `;
            return;
        }

        filtered.forEach(track => {
            const isCurrent = player.getCurrentTrack().id === track.id;
            const isPlayingThis = isCurrent && player.isPlaying;

            const card = document.createElement('div');
            card.className = `track-card ${isCurrent ? 'active' : ''}`;
            card.dataset.id = track.id;

            card.innerHTML = `
                <div class="track-cover-wrapper">
                    <img src="${track.cover}" alt="${track.title}" class="track-cover-img">
                    <button class="play-overlay-btn" title="Play Track">
                        <i class="fa-solid ${isPlayingThis ? 'fa-pause' : 'fa-play'}"></i>
                    </button>
                    <span class="category-badge">${track.category}</span>
                </div>
                <div class="track-info-body">
                    <h4 class="track-card-title">${track.title}</h4>
                    <p class="track-card-artist">${track.artist}</p>
                    <div class="track-card-footer">
                        <span class="eco-tag-lbl">${track.ecoTag}</span>
                        <span class="duration-lbl">${track.duration}</span>
                    </div>
                </div>
            `;

            card.addEventListener('click', () => {
                if (isCurrent) {
                    player.togglePlay();
                } else {
                    player.playTrackById(track.id);
                }
            });

            trackGrid.appendChild(card);
        });
    }

    function renderCategoryPills() {
        if (!categoryPills || typeof CATEGORIES === 'undefined') return;
        categoryPills.innerHTML = '';

        CATEGORIES.forEach(cat => {
            const btn = document.createElement('button');
            btn.className = `pill-btn ${cat === currentCategory ? 'active' : ''}`;
            btn.textContent = cat;

            btn.addEventListener('click', () => {
                currentCategory = cat;
                player.filterQueueByCategory(cat);
                renderCategoryPills();
                renderTrackGrid();
            });

            categoryPills.appendChild(btn);
        });
    }

    // ==========================================
    // Event Listeners for Player Engine
    // ==========================================

    document.addEventListener('trackLoaded', (e) => {
        const track = e.detail.track;
        if (nowPlayingCover) nowPlayingCover.src = track.cover;
        if (nowPlayingTitle) nowPlayingTitle.textContent = track.title;
        if (nowPlayingArtist) nowPlayingArtist.textContent = track.artist;
        if (nowPlayingEcoTag) nowPlayingEcoTag.textContent = track.ecoTag;
        if (totalTimeEl) totalTimeEl.textContent = track.duration;
        renderTrackGrid();
    });

    document.addEventListener('playerStateChange', (e) => {
        const isPlaying = e.detail.isPlaying;
        if (playPauseIcon) {
            playPauseIcon.className = `fa-solid ${isPlaying ? 'fa-pause' : 'fa-play'}`;
        }
        renderTrackGrid();
    });

    document.addEventListener('playerTimeUpdate', (e) => {
        const { currentTime, duration, percent } = e.detail;
        if (progressFill) progressFill.style.width = `${percent}%`;
        if (currentTimeEl) currentTimeEl.textContent = formatTime(currentTime);
        if (totalTimeEl && !isNaN(duration)) totalTimeEl.textContent = formatTime(duration);
    });

    // Control Button Clicks
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', () => player.togglePlay());
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => player.prevTrack());
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => player.nextTrack());
    }

    if (shuffleBtn) {
        shuffleBtn.addEventListener('click', () => {
            const active = player.toggleShuffle();
            shuffleBtn.classList.toggle('active', active);
        });
    }

    if (repeatBtn) {
        repeatBtn.addEventListener('click', () => {
            const mode = player.toggleRepeat();
            repeatBtn.classList.toggle('active', mode !== 'off');
            repeatBtn.title = `Repeat: ${mode.toUpperCase()}`;
        });
    }

    // Seekbar Interaction
    if (progressBar) {
        progressBar.addEventListener('click', (e) => {
            const rect = progressBar.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const percent = (clickX / rect.width) * 100;
            player.seekTo(percent);
        });
    }

    // Volume & Mute
    if (volumeSlider) {
        volumeSlider.addEventListener('input', (e) => {
            player.setVolume(e.target.value);
        });
    }

    if (muteBtn) {
        muteBtn.addEventListener('click', () => {
            const isMuted = player.toggleMute();
            muteBtn.innerHTML = `<i class="fa-solid ${isMuted ? 'fa-volume-xmark' : 'fa-volume-high'}"></i>`;
        });
    }

    // Search Input
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.trim().toLowerCase();
            renderTrackGrid();
        });
    }

    // Eco Saver Mode Toggle
    if (ecoSaverToggle) {
        ecoSaverToggle.addEventListener('change', (e) => {
            isEcoSaverActive = e.target.checked;
            document.body.classList.toggle('eco-mode-active', isEcoSaverActive);
            if (ecoEnergyCounter) {
                ecoEnergyCounter.textContent = isEcoSaverActive ? "🌱 Eco Mode: -35% Carbon Emissions & Low-Bandwidth Streaming" : "⚡ Standard High Fidelity Mode";
            }
        });
    }

    function formatTime(seconds) {
        if (isNaN(seconds)) return "00:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Initial Renders
    renderCategoryPills();
    renderTrackGrid();
});
