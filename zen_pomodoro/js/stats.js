/**
 * Zen Focus Analytics & Daily Streak Tracker
 */

class StatsTracker {
    constructor() {
        this.stats = JSON.parse(localStorage.getItem('zen_stats')) || {
            totalFocusMinutes: 75,
            completedPomos: 3,
            streak: 1,
            lastActiveDate: new Date().toISOString().split('T')[0]
        };

        this.init();
    }

    init() {
        this.checkStreak();

        // Listen for pomo completion
        document.addEventListener('pomoCompleted', (e) => {
            const focusMins = e.detail.focusMinutes || 25;
            this.recordSession(focusMins);
        });
    }

    checkStreak() {
        const today = new Date().toISOString().split('T')[0];
        const lastDate = this.stats.lastActiveDate;

        if (lastDate !== today) {
            const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
            if (lastDate === yesterday) {
                // Continued streak
            } else if (lastDate < yesterday) {
                // Reset streak if missed a day
                this.stats.streak = 1;
            }
            this.stats.lastActiveDate = today;
            this.save();
        }
    }

    recordSession(minutes) {
        this.stats.totalFocusMinutes += minutes;
        this.stats.completedPomos += 1;
        this.save();
        this.updateUI();
    }

    save() {
        localStorage.setItem('zen_stats', JSON.stringify(this.stats));
    }

    updateUI() {
        const focusTimeEl = document.getElementById('statFocusTime');
        const completedPomosEl = document.getElementById('statCompletedPomos');
        const streakEl = document.getElementById('statStreak');

        if (focusTimeEl) {
            const hours = Math.floor(this.stats.totalFocusMinutes / 60);
            const mins = this.stats.totalFocusMinutes % 60;
            focusTimeEl.textContent = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
        }

        if (completedPomosEl) {
            completedPomosEl.textContent = this.stats.completedPomos;
        }

        if (streakEl) {
            streakEl.textContent = `${this.stats.streak} ${this.stats.streak === 1 ? 'Day' : 'Days'}`;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.statsTracker = new StatsTracker();
});
