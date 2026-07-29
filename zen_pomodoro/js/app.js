/**
 * Zen Pomodoro App Controller
 * Theme switching, modals, ambient drawer, keyboard shortcuts, & settings binding.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Theme Manager
    const themeBtn = document.getElementById('themeBtn');
    const themeDropdown = document.getElementById('themeDropdown');
    const themeOptions = document.querySelectorAll('.theme-option');

    // Drawer & Modals
    const soundToggleBtn = document.getElementById('soundToggleBtn');
    const ambientDrawer = document.getElementById('ambientDrawer');
    const closeAmbientBtn = document.getElementById('closeAmbientBtn');
    const soundActiveBadge = document.getElementById('soundActiveBadge');

    const statsBtn = document.getElementById('statsBtn');
    const statsModal = document.getElementById('statsModal');
    const closeStatsBtn = document.getElementById('closeStatsBtn');

    const settingsBtn = document.getElementById('settingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const settingsForm = document.getElementById('settingsForm');

    // Controls
    const playBtn = document.getElementById('playBtn');
    const resetBtn = document.getElementById('resetBtn');
    const skipBtn = document.getElementById('skipBtn');
    const modeBtns = document.querySelectorAll('.mode-btn');

    // Load Saved Theme
    const savedTheme = localStorage.getItem('zen_theme') || 'forest';
    setTheme(savedTheme);

    // Theme Switcher Events
    if (themeBtn) {
        themeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            themeDropdown.classList.toggle('hidden');
        });
    }

    document.addEventListener('click', () => {
        if (themeDropdown && !themeDropdown.classList.contains('hidden')) {
            themeDropdown.classList.add('hidden');
        }
    });

    themeOptions.forEach(opt => {
        opt.addEventListener('click', () => {
            const theme = opt.dataset.theme;
            setTheme(theme);
        });
    });

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('zen_theme', theme);
        themeOptions.forEach(o => {
            if (o.dataset.theme === theme) o.classList.add('active');
            else o.classList.remove('active');
        });
    }

    // Ambient Soundscapes Drawer Events
    if (soundToggleBtn) {
        soundToggleBtn.addEventListener('click', () => {
            ambientDrawer.classList.toggle('hidden');
        });
    }

    if (closeAmbientBtn) {
        closeAmbientBtn.addEventListener('click', () => {
            ambientDrawer.classList.add('hidden');
        });
    }

    // Ambient Sound Card Events
    const soundCards = document.querySelectorAll('.sound-card');
    soundCards.forEach(card => {
        const soundType = card.dataset.sound;
        const toggleBtn = card.querySelector('.sound-toggle-btn');
        const slider = card.querySelector('.volume-slider');

        toggleBtn.addEventListener('click', () => {
            const isPlaying = window.ambientEngine.toggleSound(soundType);
            if (isPlaying) {
                card.classList.add('playing');
                toggleBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
            } else {
                card.classList.remove('playing');
                toggleBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
            }
            updateActiveSoundBadge();
        });

        slider.addEventListener('input', (e) => {
            window.ambientEngine.setVolume(soundType, e.target.value);
        });
    });

    function updateActiveSoundBadge() {
        const playingCount = Object.keys(window.ambientEngine.activeNodes).length;
        if (playingCount > 0) {
            soundActiveBadge.classList.remove('hidden');
        } else {
            soundActiveBadge.classList.add('hidden');
        }
    }

    // Mode Selector Pills
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            window.pomodoroTimer.setMode(btn.dataset.mode);
        });
    });

    // Play / Pause / Reset / Skip Buttons
    if (playBtn) {
        playBtn.addEventListener('click', () => {
            window.pomodoroTimer.togglePlay();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            window.pomodoroTimer.reset();
        });
    }

    if (skipBtn) {
        skipBtn.addEventListener('click', () => {
            window.pomodoroTimer.skip();
        });
    }

    // Keyboard Shortcuts (Space, S, R)
    document.addEventListener('keydown', (e) => {
        // Prevent shortcuts if typing in input field
        if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

        if (e.code === 'Space') {
            e.preventDefault();
            window.pomodoroTimer.togglePlay();
        } else if (e.code === 'KeyS') {
            window.pomodoroTimer.skip();
        } else if (e.code === 'KeyR') {
            window.pomodoroTimer.reset();
        }
    });

    // Stats Modal
    if (statsBtn) {
        statsBtn.addEventListener('click', () => {
            window.statsTracker.updateUI();
            statsModal.classList.remove('hidden');
        });
    }

    if (closeStatsBtn) {
        closeStatsBtn.addEventListener('click', () => {
            statsModal.classList.add('hidden');
        });
    }

    // Settings Modal
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            settingsModal.classList.remove('hidden');
        });
    }

    if (closeSettingsBtn) {
        closeSettingsBtn.addEventListener('click', () => {
            settingsModal.classList.add('hidden');
        });
    }

    if (settingsForm) {
        settingsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const focus = parseInt(document.getElementById('setFocusTime').value, 10) || 25;
            const shortB = parseInt(document.getElementById('setShortBreak').value, 10) || 5;
            const longB = parseInt(document.getElementById('setLongBreak').value, 10) || 15;

            window.pomodoroTimer.setDurations(focus, shortB, longB);
            window.pomodoroTimer.autoStartBreaks = document.getElementById('setAutoBreaks').checked;
            window.pomodoroTimer.autoStartFocus = document.getElementById('setAutoFocus').checked;

            settingsModal.classList.add('hidden');
        });
    }
});
