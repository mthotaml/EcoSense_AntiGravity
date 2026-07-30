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
    const autopilotToggle = document.getElementById('autopilotToggle');
    const autopilotStatusTag = document.getElementById('autopilotStatusTag');

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
            const duration = audio.duration || 240;
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

    // Unified UI & Audio Sync Helper
    function syncNowPlayingUI(data) {
        if (!data || !data.now_playing) return;
        const track = data.now_playing;

        // 1. Update Recommendation Card DOM
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

        // 2. Update Player Bar DOM
        const titleEl = document.getElementById('playerTitle');
        const artistEl = document.getElementById('playerArtist');
        const coverEl = document.getElementById('playerCover');
        if (titleEl) titleEl.textContent = track.title;
        if (artistEl) artistEl.textContent = track.artist_name;
        if (coverEl) coverEl.src = track.cover_url;

        // 3. Play audio preview
        if (track.preview_url) {
            playTrackAudio(track.preview_url);
        }

        // 4. Update Autopilot queue table & pagination bar
        if (data.autopilot_queue && data.autopilot_queue.length > 0) {
            const offset = data.page ? (data.page - 1) * 5 : 0;
            renderAutopilotQueueTable(data.autopilot_queue, offset);
            updatePaginationControls(data);
        }
    }

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
                syncNowPlayingUI(data);
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

    // Play Now Handler for Table Rows
    const handlePlayNow = async (decisionId) => {
        try {
            const res = await fetch('/api/play', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ decision_id: decisionId })
            });
            const data = await res.json();
            syncNowPlayingUI(data);
        } catch (e) {
            console.error('Play Now error:', e);
        }
    };

    function attachPlayNowListeners() {
        document.querySelectorAll('.btn-play-now').forEach(btn => {
            btn.addEventListener('click', () => {
                handlePlayNow(btn.dataset.id);
            });
        });
    }
    attachPlayNowListeners();

    let currentAutopilotPage = 1;
    let autopilotTotalPages = 1;
    let autopilotTotalItems = 0;

    const btnPrevPage = document.getElementById('btnPrevPage');
    const btnNextPage = document.getElementById('btnNextPage');
    const btnLoadMoreTracks = document.getElementById('btnLoadMoreTracks');
    const currentPageNumEl = document.getElementById('currentPageNum');
    const totalPagesNumEl = document.getElementById('totalPagesNum');
    const totalQueueItemsEl = document.getElementById('totalQueueItems');
    const pageQuickJumpContainer = document.getElementById('pageQuickJumpContainer');

    function updatePaginationControls(data) {
        if (!data) return;
        currentAutopilotPage = data.page || 1;
        autopilotTotalPages = data.total_pages || 1;
        autopilotTotalItems = data.total_items || 0;

        if (currentPageNumEl) currentPageNumEl.textContent = currentAutopilotPage;
        if (totalPagesNumEl) totalPagesNumEl.textContent = autopilotTotalPages;
        if (totalQueueItemsEl) totalQueueItemsEl.textContent = autopilotTotalItems;

        if (btnPrevPage) btnPrevPage.disabled = (currentAutopilotPage <= 1);
        if (btnNextPage) btnNextPage.disabled = (currentAutopilotPage >= autopilotTotalPages);

        if (pageQuickJumpContainer) {
            let btnsHtml = '';
            for (let p = 1; p <= autopilotTotalPages; p++) {
                const isActive = (p === currentAutopilotPage);
                btnsHtml += `
                    <button class="btn-page-num ${isActive ? 'active' : ''}" data-page="${p}" style="padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; background: ${isActive ? '#1ed760' : 'rgba(255,255,255,0.08)'}; color: ${isActive ? '#000' : '#fff'}; border: none; cursor: pointer; font-weight: 600;">
                        ${p}
                    </button>
                `;
            }
            pageQuickJumpContainer.innerHTML = btnsHtml;
            attachQuickJumpListeners();
        }
    }

    async function fetchAutopilotPage(page) {
        try {
            const res = await fetch(`/api/autopilot?page=${page}&page_size=5`);
            const data = await res.json();
            if (data.autopilot_queue) {
                renderAutopilotQueueTable(data.autopilot_queue, (page - 1) * 5);
                updatePaginationControls(data);
            }
        } catch (e) {
            console.error('Fetch page error:', e);
        }
    }

    function attachQuickJumpListeners() {
        document.querySelectorAll('.btn-page-num').forEach(btn => {
            btn.addEventListener('click', () => {
                const p = parseInt(btn.dataset.page, 10);
                if (p && p !== currentAutopilotPage) {
                    fetchAutopilotPage(p);
                }
            });
        });
    }
    attachQuickJumpListeners();

    if (btnPrevPage) {
        btnPrevPage.addEventListener('click', () => {
            if (currentAutopilotPage > 1) {
                fetchAutopilotPage(currentAutopilotPage - 1);
            }
        });
    }

    if (btnNextPage) {
        btnNextPage.addEventListener('click', () => {
            if (currentAutopilotPage < autopilotTotalPages) {
                fetchAutopilotPage(currentAutopilotPage + 1);
            }
        });
    }

    if (btnLoadMoreTracks) {
        btnLoadMoreTracks.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/autopilot/load_more', { method: 'POST' });
                const data = await res.json();
                if (data.autopilot_queue) {
                    fetchAutopilotPage(data.total_pages);
                }
            } catch (e) {
                console.error('Load more error:', e);
            }
        });
    }

    function renderAutopilotQueueTable(queue, indexOffset = 0) {
        const tbody = document.getElementById('autopilotTableBody');
        if (!tbody) return;

        tbody.innerHTML = queue.map((dec, idx) => {
            const dnaVal = dec.factors ? Math.round(dec.factors.dna_affinity * 100) : 100;
            const ctxVal = dec.factors ? Math.round(dec.factors.live_context_fit * 100) : 100;
            const prefVal = dec.factors ? Math.round(dec.factors.learned_preference * 100) : 0;
            const divVal = dec.factors ? Math.round(dec.factors.diversity_guard * 100) : 100;

            return `
                <tr>
                    <td>${indexOffset + idx + 1}</td>
                    <td>
                        <div class="table-track-cell">
                            <img src="${dec.track.cover_url}" alt="" class="table-thumb">
                            <div>
                                <strong class="table-track-title">${dec.track.title}</strong>
                                <span class="table-artist">${dec.track.artist_name}</span>
                            </div>
                        </div>
                    </td>
                    <td><span class="score-bar-bg"><span class="score-bar-fill" style="width: ${dnaVal}%;"></span></span> ${dnaVal}%</td>
                    <td><span class="score-bar-bg"><span class="score-bar-fill context" style="width: ${ctxVal}%;"></span></span> ${ctxVal}%</td>
                    <td><span class="score-pill">+${prefVal}%</span></td>
                    <td><span class="badge-diversity"><i class="fa-solid fa-shield"></i> ${divVal}%</span></td>
                    <td>
                        <div style="font-size: 0.82rem; color: #d0d0d0; max-width: 280px; line-height: 1.35;">
                            <i class="fa-solid fa-sparkles" style="color: #1ed760; margin-right: 4px;"></i>
                            ${dec.why_now}
                        </div>
                    </td>
                    <td><button class="btn-play-now" data-id="${dec.decision_id}">Play now</button></td>
                </tr>
            `;
        }).join('');
        
        attachPlayNowListeners();
    }

    // Autopilot Queue ON / OFF Toggle
    if (autopilotToggle) {
        autopilotToggle.addEventListener('change', async () => {
            const enabled = autopilotToggle.checked;
            try {
                const res = await fetch('/api/autopilot/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: enabled })
                });
                const data = await res.json();
                
                if (autopilotStatusTag) {
                    autopilotStatusTag.innerHTML = enabled
                        ? `<span class="pulse-dot"></span> Autopilot Active`
                        : `<span style="background: rgba(255, 193, 7, 0.2); color: #ffc107; padding: 6px 12px; border-radius: 20px; font-size: 0.82rem; border: 1px solid rgba(255, 193, 7, 0.4);"><i class="fa-brands fa-spotify"></i> Direct Spotify Mode (OFF)</span>`;
                }

                if (data.autopilot_queue) {
                    const offset = data.page ? (data.page - 1) * 5 : 0;
                    renderAutopilotQueueTable(data.autopilot_queue, offset);
                    updatePaginationControls(data);
                }
            } catch (e) {
                console.error('Autopilot toggle error:', e);
            }
        });
    }

    // Live Context Resolution ON / OFF Toggle
    const liveContextToggle = document.getElementById('liveContextToggle');
    const liveContextStatusBadge = document.getElementById('liveContextStatusBadge');

    if (liveContextToggle) {
        liveContextToggle.addEventListener('change', async () => {
            const enabled = liveContextToggle.checked;
            try {
                const res = await fetch('/api/context/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: enabled })
                });
                const data = await res.json();

                if (liveContextStatusBadge) {
                    liveContextStatusBadge.innerHTML = enabled
                        ? `<span class="pulse-dot"></span> <span style="color: #1ed760; font-weight: 600; font-size: 0.85rem;">Live Context ON</span>`
                        : `<span style="background: rgba(220, 53, 69, 0.2); color: #ff6b6b; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; border: 1px solid rgba(220, 53, 69, 0.4);"><i class="fa-solid fa-ban"></i> Live Context OFF</span>`;
                }

                if (data.autopilot_queue) {
                    const offset = data.page ? (data.page - 1) * 5 : 0;
                    renderAutopilotQueueTable(data.autopilot_queue, offset);
                    updatePaginationControls(data);
                }
            } catch (e) {
                console.error('Live Context toggle error:', e);
            }
        });
    }

    // Skip Current Song Functionality
    const handleSkip = async () => {
        try {
            const res = await fetch('/api/skip', { method: 'POST' });
            const data = await res.json();
            
            if (data.status === 'success' && data.now_playing) {
                if (startRecBtn && data.decision_id) {
                    startRecBtn.dataset.id = data.decision_id;
                }
                syncNowPlayingUI(data);
            }
        } catch (e) {
            console.error('Skip error:', e);
        }
    };

    if (skipCurrentBtn) skipCurrentBtn.addEventListener('click', handleSkip);
    if (playerSkipBtn) playerSkipBtn.addEventListener('click', handleSkip);

    // Spotify OAuth Connect
    if (connectSpotifyBtn) {
        connectSpotifyBtn.addEventListener('click', () => {
            window.location.href = '/auth/spotify';
        });
    }

    // Spotify Credentials Form Handler
    const spotifyCredsForm = document.getElementById('spotifyCredsForm');
    const spotifyClientIdInput = document.getElementById('spotifyClientIdInput');
    const spotifyClientSecretInput = document.getElementById('spotifyClientSecretInput');

    if (spotifyCredsForm) {
        spotifyCredsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const clientId = spotifyClientIdInput.value.trim();
            const clientSecret = spotifyClientSecretInput.value.trim();

            if (!clientId || !clientSecret) {
                alert('Please enter both Spotify Client ID and Client Secret.');
                return;
            }

            try {
                const res = await fetch('/api/settings/spotify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ client_id: clientId, client_secret: clientSecret })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    window.location.href = '/auth/spotify';
                }
            } catch (err) {
                console.error('Error updating Spotify credentials:', err);
            }
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

    // Info Icon Modal Handlers
    const infoModal = document.getElementById('infoModal');
    const closeInfoModal = document.getElementById('closeInfoModal');
    const infoModalTitle = document.getElementById('infoModalTitle');
    const infoModalBody = document.getElementById('infoModalBody');

    const infoModalContentMap = {
        'dna': {
            title: '<i class="fa-solid fa-dna" style="color: #1ed760; margin-right: 8px;"></i> Music DNA Affinity',
            body: `<p><strong>Music DNA Affinity</strong> measures how closely a track matches your long-term musical taste vector built from your Spotify library.</p>
                <div style="background: rgba(255,255,255,0.04); padding: 14px; border-radius: 10px; margin: 16px 0; border: 1px solid rgba(255,255,255,0.08);">
                    <strong style="color: #1ed760;">Calculation Formula:</strong><br>
                    <code style="color: #64b5f6; font-size: 0.9rem;">DNA Affinity = (0.60 × Artist Affinity) + (0.40 × Category Fit)</code>
                </div>
                <ul style="padding-left: 20px; margin: 0 0 16px 0;">
                    <li><strong>Artist Affinity (60% weight)</strong>: Base score of 0.85 for your top artists on Spotify, boosted by +0.10 for recent plays (up to 1.0).</li>
                    <li><strong>Category/Genre Fit (40% weight)</strong>: Match score against your primary listened categories (e.g. Deep Focus, Nature Soundscapes, Eco Lo-Fi Beats).</li>
                </ul>`
        },
        'context': {
            title: '<i class="fa-solid fa-cloud-sun" style="color: #1ed760; margin-right: 8px;"></i> Live Context Fit',
            body: `<p><strong>Live Context Fit</strong> evaluates real-time environmental context signals (daypart, weather, road setting, and current activity).</p>
                <div style="background: rgba(255,255,255,0.04); padding: 14px; border-radius: 10px; margin: 16px 0; border: 1px solid rgba(255,255,255,0.08);">
                    <strong style="color: #1ed760;">Context Policy Cap:</strong><br>
                    <code style="color: #64b5f6; font-size: 0.9rem;">Live Context Fit is capped at max 35% (0.35) of total candidate score</code>
                </div>`
        },
        'preference': {
            title: '<i class="fa-solid fa-brain" style="color: #1ed760; margin-right: 8px;"></i> Learned Preference',
            body: `<p><strong>Learned Preference</strong> applies bounded score adjustments (-0.20 to +0.20) learned dynamically from your completed plays and skips in similar contexts.</p>`
        },
        'diversity': {
            title: '<i class="fa-solid fa-shield-halved" style="color: #1ed760; margin-right: 8px;"></i> Diversity Guard',
            body: `<p><strong>Diversity Guard</strong> protects against artist fatigue. Max 2 tracks per artist are permitted in the queue preview, with non-adjacent artist bonuses (+0.05).</p>`
        }
    };

    document.querySelectorAll('.info-icon').forEach(icon => {
        icon.addEventListener('click', (e) => {
            e.stopPropagation();
            const text = icon.getAttribute('title') || icon.getAttribute('aria-label') || '';
            let key = 'dna';
            if (text.includes('context')) key = 'context';
            else if (text.includes('preference')) key = 'preference';
            else if (text.includes('guard')) key = 'diversity';

            const modalData = infoModalContentMap[key] || infoModalContentMap['dna'];
            if (infoModalTitle) infoModalTitle.innerHTML = modalData.title;
            if (infoModalBody) infoModalBody.innerHTML = modalData.body;
            if (infoModal) infoModal.style.display = 'flex';
        });
    });

    if (closeInfoModal) {
        closeInfoModal.addEventListener('click', () => {
            if (infoModal) infoModal.style.display = 'none';
        });
    }

    if (infoModal) {
        infoModal.addEventListener('click', (e) => {
            if (e.target === infoModal) {
                infoModal.style.display = 'none';
            }
        });
    }
});
