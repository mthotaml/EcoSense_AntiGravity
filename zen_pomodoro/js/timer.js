/**
 * Zen Pomodoro Timer Engine & Circular SVG Progress Controller
 */

class PomodoroTimer {
    constructor() {
        this.durations = {
            focus: 25 * 60,
            shortBreak: 5 * 60,
            longBreak: 15 * 60
        };

        this.currentMode = 'focus';
        this.remainingSeconds = this.durations.focus;
        this.isRunning = false;
        this.timerId = null;
        this.completedCount = 0;

        this.autoStartBreaks = false;
        this.autoStartFocus = false;

        this.ringCircle = document.getElementById('ringProgress');
        this.timeDisplay = document.getElementById('timerTime');
        this.labelDisplay = document.getElementById('timerLabel');
        this.playIcon = document.getElementById('playIcon');

        this.circumference = 2 * Math.PI * 135; // r=135
        if (this.ringCircle) {
            this.ringCircle.style.strokeDasharray = `${this.circumference} ${this.circumference}`;
        }
    }

    setDurations(focusMin, shortMin, longMin) {
        this.durations.focus = focusMin * 60;
        this.durations.shortBreak = shortMin * 60;
        this.durations.longBreak = longMin * 60;

        if (!this.isRunning) {
            this.remainingSeconds = this.durations[this.currentMode];
            this.updateDisplay();
        }
    }

    setMode(mode) {
        if (this.currentMode === mode) return;

        this.pause();
        this.currentMode = mode;
        this.remainingSeconds = this.durations[mode];

        // Update active UI mode pills
        const btns = document.querySelectorAll('.mode-btn');
        btns.forEach(btn => {
            if (btn.dataset.mode === mode) btn.classList.add('active');
            else btn.classList.remove('active');
        });

        const modeLabels = {
            focus: 'Time to focus',
            shortBreak: 'Time for a short break',
            longBreak: 'Time for a deep break'
        };
        this.labelDisplay.textContent = modeLabels[mode];

        this.updateDisplay();
    }

    togglePlay() {
        if (this.isRunning) {
            this.pause();
        } else {
            this.start();
        }
    }

    start() {
        if (this.isRunning) return;

        // Unlock audio context if needed
        if (window.ambientEngine) {
            window.ambientEngine.initCtx();
        }

        this.isRunning = true;
        this.playIcon.className = 'fa-solid fa-pause';

        this.timerId = setInterval(() => {
            this.tick();
        }, 1000);
    }

    pause() {
        if (!this.isRunning) return;

        this.isRunning = false;
        this.playIcon.className = 'fa-solid fa-play';
        clearInterval(this.timerId);
        this.timerId = null;
    }

    reset() {
        this.pause();
        this.remainingSeconds = this.durations[this.currentMode];
        this.updateDisplay();
    }

    skip() {
        this.pause();
        this.onComplete();
    }

    tick() {
        if (this.remainingSeconds > 0) {
            this.remainingSeconds--;
            this.updateDisplay();
        } else {
            this.pause();
            this.onComplete();
        }
    }

    onComplete() {
        // Play Chime Bell
        if (window.ambientEngine) {
            window.ambientEngine.playChime();
        }

        if (this.currentMode === 'focus') {
            this.completedCount++;
            
            // Dispatch event for task & stats module
            const event = new CustomEvent('pomoCompleted', {
                detail: {
                    focusMinutes: Math.round(this.durations.focus / 60)
                }
            });
            document.dispatchEvent(event);

            // Auto switch to break
            if (this.completedCount % 4 === 0) {
                this.setMode('longBreak');
            } else {
                this.setMode('shortBreak');
            }

            if (this.autoStartBreaks) this.start();

        } else {
            // Break completed -> Switch back to Focus
            this.setMode('focus');
            if (this.autoStartFocus) this.start();
        }
    }

    updateDisplay() {
        const mins = Math.floor(this.remainingSeconds / 60);
        const secs = this.remainingSeconds % 60;
        const formatted = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        this.timeDisplay.textContent = formatted;
        document.title = `${formatted} - ${this.currentMode === 'focus' ? 'Focus' : 'Break'} | Zen Pomodoro`;

        // Update SVG Progress Ring
        const total = this.durations[this.currentMode];
        const progressFraction = (total - this.remainingSeconds) / total;
        const offset = this.circumference * (1 - progressFraction);

        if (this.ringCircle) {
            this.ringCircle.style.strokeDashoffset = offset;
        }
    }
}

window.pomodoroTimer = new PomodoroTimer();
