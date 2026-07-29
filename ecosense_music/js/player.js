/**
 * EcoSense Music Audio Player Core Engine
 * Featuring Clean HTML5 Audio & Real-time Canvas Spectrum Visualizer.
 */

class AudioPlayer {
    constructor(tracks) {
        this.tracks = tracks || [];
        this.queue = [...this.tracks];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.isMuted = false;
        this.volume = 0.8;
        this.repeatMode = 'off';
        this.isShuffle = false;

        this.audio = new Audio();
        this.audio.crossOrigin = "anonymous";
        this.audio.volume = this.volume;

        this.initListeners();
    }

    initListeners() {
        this.audio.addEventListener('timeupdate', () => {
            const currentTime = this.audio.currentTime;
            const duration = this.audio.duration || 1;
            const event = new CustomEvent('playerTimeUpdate', {
                detail: { currentTime, duration, percent: (currentTime / duration) * 100 }
            });
            document.dispatchEvent(event);
        });

        this.audio.addEventListener('ended', () => {
            if (this.repeatMode === 'one') {
                this.audio.currentTime = 0;
                this.play();
            } else {
                this.nextTrack();
            }
        });

        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            if (window.visualizerEngine) window.visualizerEngine.startVisualizer();
            document.dispatchEvent(new CustomEvent('playerStateChange', { detail: { isPlaying: true } }));
        });

        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            if (window.visualizerEngine) window.visualizerEngine.stopVisualizer();
            document.dispatchEvent(new CustomEvent('playerStateChange', { detail: { isPlaying: false } }));
        });
    }

    getCurrentTrack() {
        return this.queue[this.currentIndex] || this.tracks[0];
    }

    loadTrack(index) {
        if (index < 0 || index >= this.queue.length) return;
        this.currentIndex = index;
        const track = this.getCurrentTrack();

        this.audio.src = track.audioUrl;
        this.audio.load();

        document.dispatchEvent(new CustomEvent('trackLoaded', { detail: { track } }));
    }

    playTrackById(id) {
        const index = this.queue.findIndex(t => t.id === id);
        if (index !== -1) {
            this.loadTrack(index);
            this.play();
        }
    }

    play() {
        if (!this.audio.src || this.audio.src === '') {
            this.loadTrack(0);
        }

        const playPromise = this.audio.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                this.isPlaying = true;
            }).catch(err => {
                console.log("Audio play notice:", err);
            });
        }
    }

    pause() {
        this.audio.pause();
        this.isPlaying = false;
    }

    togglePlay() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    nextTrack() {
        if (this.isShuffle) {
            this.currentIndex = Math.floor(Math.random() * this.queue.length);
        } else {
            this.currentIndex = (this.currentIndex + 1) % this.queue.length;
        }
        this.loadTrack(this.currentIndex);
        this.play();
    }

    prevTrack() {
        if (this.audio.currentTime > 3) {
            this.audio.currentTime = 0;
            return;
        }
        this.currentIndex = (this.currentIndex - 1 + this.queue.length) % this.queue.length;
        this.loadTrack(this.currentIndex);
        this.play();
    }

    seekTo(percent) {
        if (this.audio.duration) {
            this.audio.currentTime = (percent / 100) * this.audio.duration;
        }
    }

    setVolume(val) {
        this.volume = parseFloat(val);
        this.audio.volume = this.volume;
        this.isMuted = this.volume === 0;
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        this.audio.muted = this.isMuted;
        return this.isMuted;
    }

    toggleShuffle() {
        this.isShuffle = !this.isShuffle;
        return this.isShuffle;
    }

    toggleRepeat() {
        const modes = ['off', 'all', 'one'];
        const nextIdx = (modes.indexOf(this.repeatMode) + 1) % modes.length;
        this.repeatMode = modes[nextIdx];
        return this.repeatMode;
    }

    filterQueueByCategory(category) {
        if (category === 'All Playlists') {
            this.queue = [...this.tracks];
        } else {
            this.queue = this.tracks.filter(t => t.category === category);
        }
        this.currentIndex = 0;
        this.loadTrack(0);
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AudioPlayer };
}
