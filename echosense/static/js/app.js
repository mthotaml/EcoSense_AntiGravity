/**
 * EchoSense UI Coordinator, Clean Audio Stream Engine, & Spotify API Client
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Controls
    const startRecBtn = document.getElementById('startRecBtn');
    const skipCurrentBtn = document.getElementById('skipCurrentBtn');
    const playerSkipBtn = document.getElementById('playerSkipBtn');
    const mainPlayBtn = document.getElementById('mainPlayBtn');
    const mainPlayIcon = document.getElementById('mainPlayIcon');
    const disconnectBtn = document.getElementById('disconnectBtn');
    const connectSpotifyBtn = document.getElementById('connectSpotifyBtn');

    const correctionForm = document.getElementById('correctionForm');
    const correctedInput = document.getElementById('correctedInput');
    const resetTemporalBtn = document.getElementById('resetTemporalBtn');
    const deleteConsentBtn = document.getElementById('deleteConsentBtn');

    // Pure HTML5 Audio Player Engine
    const audio = new Audio();
    audio.crossOrigin = "anonymous";
    audio.volume = 0.8;
    let isPlaying = false;
    let progressTimer = null;

    function playTrackAudio(previewUrl) {
        if (!previewUrl) return;

        const absoluteUrl = new URL(previewUrl, window.location.origin).href;
        if (audio.src !== absoluteUrl) {
            audio.src = absoluteUrl;
        }

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                isPlaying = true;
                updatePlayIcons(true);
                startProgressTimer();
            }).catch(err => {
                console.log("Audio play notice:", err);
                isPlaying = false;
                updatePlayIcons(false);
            });
        }
    }

    function pauseTrackAudio() {
        audio.pause();
        isPlaying = false;
        updatePlayIcons(false);
        stopProgressTimer();
    }

    function toggleAudioPlayback(previewUrl) {
        if (isPlaying) {
            pauseTrackAudio();
        } else {
            if (previewUrl || audio.src) {
                playTrackAudio(previewUrl || audio.src);
            }
        }
    }

    function updatePlayIcons(playing) {
        if (mainPlayIcon) {
            mainPlayIcon.className = playing ? 'fa-solid fa-pause' : 'fa-solid fa-play';
        }
        if (startRecBtn) {
            const icon = startRecBtn.querySelector('i');
            if (icon) {
                icon.className = playing ? 'fa-solid fa-pause' : 'fa-solid fa-play';
            }
        }
    }

    function startProgressTimer() {
        stopProgressTimer();
        progressTimer = setInterval(() => {
            const currentTime = audio.currentTime || 0;
            const duration = audio.duration || 8;
            const progressFill = document.querySelector('.player-progress-fill');
            if (progressFill) {
                const percent = Math.min((currentTime / duration) * 100, 100);
                progressFill.style.width = `${percent}%`;
            }
        }, 300);
    }

    function stopProgressTimer() {
        if (progressTimer) {
            clearInterval(progressTimer);
            progressTimer = null;
        }
    }

    // Audio Event Listeners
    audio.addEventListener('ended', () => {
        handleSkip();
    });

    // Play Recommendation Button
    if (startRecBtn) {
        startRecBtn.addEventListener('click', async () => {
            const decisionId = startRecBtn.dataset.id;
            try {
                const res = await fetch('/api/play', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ decision_id: decisionId })
                });
                const data = await res.json();
                const previewUrl = (data.now_playing && data.now_playing.preview_url) ? data.now_playing.preview_url : null;
                toggleAudioPlayback(previewUrl);
            } catch (e) {
                console.error('Play error:', e);
            }
        });
    }

    // Main Player Play/Pause Button
    if (mainPlayBtn) {
        mainPlayBtn.addEventListener('click', () => {
            toggleAudioPlayback(audio.src || null);
        });
    }

    // Skip Current Song Functionality
    const handleSkip = async () => {
        try {
            const res = await fetch('/api/skip', { method: 'POST' });
            const data = await res.json();
            
            if (data.status === 'success' && data.now_playing) {
                const track = data.now_playing;
                
                // 1. Update Card DOM Elements
                const cardTitle = document.querySelector('.rec-track-title');
                const cardArtist = document.querySelector('.rec-artist-name');
                const cardCover = document.querySelector('.rec-cover-img');
                const cardCategory = document.querySelector('.rec-category-tag');
                const cardReason = document.querySelector('.reason-text');

                if (cardTitle) cardTitle.textContent = track.title;
                if (cardArtist) cardArtist.innerHTML = `${track.artist_name} &bull; <em>${track.album_name}</em>`;
                if (cardCover) cardCover.src = track.cover_url;
                if (cardCategory) cardCategory.textContent = track.category;
                if (cardReason) cardReason.textContent = `Switched via Autopilot: ${track.title} by ${track.artist_name}`;

                // 2. Update Bottom Player Bar DOM Elements
                const titleEl = document.getElementById('playerTitle');
                const artistEl = document.getElementById('playerArtist');
                const coverEl = document.getElementById('playerCover');
                if (titleEl) titleEl.textContent = track.title;
                if (artistEl) artistEl.textContent = track.artist_name;
                if (coverEl) coverEl.src = track.cover_url;

                // 3. Update Decision ID
                if (startRecBtn && data.decision_id) {
                    startRecBtn.dataset.id = data.decision_id;
                }
                
                // 4. Play New Track Audio Stream
                if (track.preview_url) {
                    playTrackAudio(track.preview_url);
                }

                // 5. Dynamic Continuous Autopilot Queue Table Re-render
                if (data.autopilot_queue && data.autopilot_queue.length > 0) {
                    const tbody = document.getElementById('autopilotTableBody');
                    if (tbody) {
                        tbody.innerHTML = data.autopilot_queue.map((dec, idx) => `
                            <tr>
                                <td>${idx + 1}</td>
                                <td>
                                    <div class="table-track-cell">
                                        <img src="${dec.track.cover_url}" alt="" class="table-thumb">
                                        <div>
                                            <strong class="table-track-title">${dec.track.title}</strong>
                                            <span class="table-artist">${dec.track.artist_name}</span>
                                        </div>
                                    </div>
                                </td>
                                <td><span class="score-bar-bg"><span class="score-bar-fill" style="width: ${Math.round(dec.factors.dna_affinity * 100)}%;"></span></span> ${Math.round(dec.factors.dna_affinity * 100)}%</td>
                                <td><span class="score-bar-bg"><span class="score-bar-fill context" style="width: ${Math.round(dec.factors.live_context_fit * 100)}%;"></span></span> ${Math.round(dec.factors.live_context_fit * 100)}%</td>
                                <td><span class="score-pill">+${Math.round(dec.factors.learned_preference * 100)}%</span></td>
                                <td><span class="badge-diversity"><i class="fa-solid fa-shield"></i> ${Math.round(dec.factors.diversity_guard * 100)}%</span></td>
                                <td>
                                    <div style="font-size: 0.82rem; color: #d0d0d0; max-width: 280px; line-height: 1.35;">
                                        <i class="fa-solid fa-sparkles" style="color: #1ed760; margin-right: 4px;"></i>
                                        ${dec.why_now}
                                    </div>
                                </td>
                                <td><button class="btn-play-now" data-id="${dec.decision_id}">Play now</button></td>
                            </tr>
                        `).join('');
                        
                        tbody.querySelectorAll('.btn-play-now').forEach(btn => {
                            btn.addEventListener('click', async () => {
                                const decisionId = btn.dataset.id;
                                const res = await fetch('/api/play', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ decision_id: decisionId })
                                });
                                const playData = await res.json();
                                if (playData.now_playing && playData.now_playing.preview_url) {
                                    playTrackAudio(playData.now_playing.preview_url);
                                }
                            });
                        });
                    }
                }
            }
        } catch (e) {
            console.error('Skip error:', e);
        }
    };

    if (skipCurrentBtn) skipCurrentBtn.addEventListener('click', handleSkip);
    if (playerSkipBtn) playerSkipBtn.addEventListener('click', handleSkip);

    // Play Now Override in Autopilot Table
    document.querySelectorAll('.btn-play-now').forEach(btn => {
        btn.addEventListener('click', async () => {
            const decisionId = btn.dataset.id;
            const res = await fetch('/api/play', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ decision_id: decisionId })
            });
            const data = await res.json();
            if (data.now_playing && data.now_playing.preview_url) {
                playTrackAudio(data.now_playing.preview_url);
            }
        });
    });

    // Spotify OAuth Connect
    if (connectSpotifyBtn) {
        connectSpotifyBtn.addEventListener('click', () => {
            window.location.href = '/auth/spotify';
        });
    }

    // Correction Form
    if (correctionForm) {
        correctionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const patternVal = correctedInput.value.trim();
            if (!patternVal) return;

            await fetch('/api/context/correct', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ daypart: 'morning', corrected_pattern: patternVal })
            });
            window.location.reload();
        });
    }

    // Reset Temporal Memory
    if (resetTemporalBtn) {
        resetTemporalBtn.addEventListener('click', async () => {
            if (confirm('Reset temporal memory? Music DNA will remain intact.')) {
                await fetch('/api/context/reset', { method: 'POST' });
                window.location.reload();
            }
        });
    }

    // Delete Consent Data
    if (deleteConsentBtn) {
        deleteConsentBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete all consent-derived data and reset memory?')) {
                const res = await fetch('/api/consent/delete', { method: 'POST' });
                const data = await res.json();
                alert(`Data deletion completed cleanly. Receipt ID: ${data.receipt.receipt_id}`);
                window.location.reload();
            }
        });
    }

    // Disconnect Spotify
    if (disconnectBtn) {
        disconnectBtn.addEventListener('click', async () => {
            await fetch('/api/disconnect', { method: 'POST' });
            window.location.reload();
        });
    }
});
