/**
 * EcoSense Audio Engine & Canvas Frequency Visualizer
 * Connects Web Audio API AnalyserNode to HTML5 Audio element and draws smooth visualizer waves.
 */

class AudioVisualizerEngine {
    constructor() {
        this.audioCtx = null;
        this.analyser = null;
        this.source = null;
        this.canvas = null;
        this.canvasCtx = null;
        this.animationId = null;
        this.isInitialized = false;
    }

    init(audioElement, canvasElement) {
        this.canvas = canvasElement;
        if (this.canvas) {
            this.canvasCtx = this.canvas.getContext('2d');
            this.resizeCanvas();
            window.addEventListener('resize', () => this.resizeCanvas());
        }

        this.audioElement = audioElement;
    }

    setupAudioContext() {
        if (this.isInitialized || !this.audioElement) return;

        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioCtx = new AudioContext();
            this.analyser = this.audioCtx.createAnalyser();
            this.analyser.fftSize = 128; // 64 frequency bars

            this.source = this.audioCtx.createMediaElementSource(this.audioElement);
            this.source.connect(this.analyser);
            this.analyser.connect(this.audioCtx.destination);

            this.isInitialized = true;
        } catch (e) {
            console.warn('Web Audio API CORS / Context Notice:', e);
        }
    }

    resizeCanvas() {
        if (!this.canvas) return;
        this.canvas.width = this.canvas.parentElement.clientWidth || 800;
        this.canvas.height = 120;
    }

    startVisualizer() {
        if (!this.isInitialized) {
            this.setupAudioContext();
        }

        if (this.audioCtx && this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }

        this.draw();
    }

    stopVisualizer() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.clearCanvas();
    }

    clearCanvas() {
        if (!this.canvasCtx || !this.canvas) return;
        this.canvasCtx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    draw() {
        if (!this.canvasCtx || !this.canvas) return;

        this.animationId = requestAnimationFrame(() => this.draw());

        const width = this.canvas.width;
        const height = this.canvas.height;
        this.canvasCtx.clearRect(0, 0, width, height);

        if (!this.analyser) {
            // Draw simulated gentle ambient sine wave if Web Audio source is CORS restricted
            this.drawSimulatedWave(width, height);
            return;
        }

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.analyser.getByteFrequencyData(dataArray);

        const barWidth = (width / bufferLength) * 2;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * (height * 0.85);

            // Emerald & Cyan Gradient
            const gradient = this.canvasCtx.createLinearGradient(0, height, 0, height - barHeight);
            gradient.addColorStop(0, 'rgba(16, 185, 129, 0.2)');
            gradient.addColorStop(0.5, 'rgba(16, 185, 129, 0.8)');
            gradient.addColorStop(1, 'rgba(6, 182, 212, 1)');

            this.canvasCtx.fillStyle = gradient;
            this.canvasCtx.beginPath();
            this.canvasCtx.roundRect(x, height - barHeight, barWidth - 4, barHeight, [4, 4, 0, 0]);
            this.canvasCtx.fill();

            x += barWidth;
        }
    }

    drawSimulatedWave(width, height) {
        const now = Date.now() * 0.003;
        this.canvasCtx.beginPath();
        this.canvasCtx.moveTo(0, height / 2);

        for (let x = 0; x < width; x += 10) {
            const y = Math.sin(x * 0.015 + now) * 20 + (height / 2);
            this.canvasCtx.lineTo(x, y);
        }

        this.canvasCtx.strokeStyle = 'rgba(16, 185, 129, 0.6)';
        this.canvasCtx.lineWidth = 3;
        this.canvasCtx.stroke();
    }
}

window.visualizerEngine = new AudioVisualizerEngine();
