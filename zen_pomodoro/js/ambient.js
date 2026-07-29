/**
 * Procedural Ambient Audio Engine using Web Audio API
 * Generates Rain, Ocean Waves, Forest Wind, 432Hz Focus Tones, and Chime Alerts.
 */

class AmbientSoundEngine {
    constructor() {
        this.ctx = null;
        this.activeNodes = {};
        this.volumes = {
            rain: 0.5,
            waves: 0.5,
            forest: 0.5,
            focus: 0.4
        };
    }

    initCtx() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioContext();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggleSound(type) {
        this.initCtx();
        if (this.activeNodes[type]) {
            this.stopSound(type);
            return false;
        } else {
            this.startSound(type);
            return true;
        }
    }

    startSound(type) {
        if (type === 'rain') this.createRain();
        else if (type === 'waves') this.createOceanWaves();
        else if (type === 'forest') this.createForestWind();
        else if (type === 'focus') this.createFocusTone();
    }

    stopSound(type) {
        if (this.activeNodes[type]) {
            try {
                this.activeNodes[type].gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 0.5);
                setTimeout(() => {
                    if (this.activeNodes[type]) {
                        this.activeNodes[type].sources.forEach(s => s.stop && s.stop());
                        delete this.activeNodes[type];
                    }
                }, 500);
            } catch (e) {
                delete this.activeNodes[type];
            }
        }
    }

    setVolume(type, val) {
        this.volumes[type] = parseFloat(val);
        if (this.activeNodes[type]) {
            this.activeNodes[type].gain.gain.setValueAtTime(this.volumes[type], this.ctx.currentTime);
        }
    }

    // Generator 1: Soft Rain
    createRain() {
        const bufferSize = 2 * this.ctx.sampleRate;
        const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            output[i] = Math.random() * 2 - 1;
        }

        const whiteNoise = this.ctx.createBufferSource();
        whiteNoise.buffer = noiseBuffer;
        whiteNoise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(800, this.ctx.currentTime);

        const gainNode = this.ctx.createGain();
        gainNode.gain.setValueAtTime(this.volumes.rain, this.ctx.currentTime);

        whiteNoise.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.ctx.destination);

        whiteNoise.start();
        this.activeNodes.rain = { gain: gainNode, sources: [whiteNoise] };
    }

    // Generator 2: Ocean Waves
    createOceanWaves() {
        const bufferSize = 2 * this.ctx.sampleRate;
        const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        let lastOut = 0.0;
        for (let i = 0; i < bufferSize; i++) {
            const white = Math.random() * 2 - 1;
            output[i] = (lastOut + (0.02 * white)) / 1.02;
            lastOut = output[i];
            output[i] *= 3.5;
        }

        const pinkNoise = this.ctx.createBufferSource();
        pinkNoise.buffer = noiseBuffer;
        pinkNoise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(400, this.ctx.currentTime);

        // LFO for wave modulation
        const lfo = this.ctx.createOscillator();
        lfo.frequency.setValueAtTime(0.1, this.ctx.currentTime);
        const lfoGain = this.ctx.createGain();
        lfoGain.gain.setValueAtTime(300, this.ctx.currentTime);

        lfo.connect(lfoGain);
        lfoGain.connect(filter.frequency);

        const gainNode = this.ctx.createGain();
        gainNode.gain.setValueAtTime(this.volumes.waves, this.ctx.currentTime);

        pinkNoise.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.ctx.destination);

        pinkNoise.start();
        lfo.start();
        this.activeNodes.waves = { gain: gainNode, sources: [pinkNoise, lfo] };
    }

    // Generator 3: Forest Wind
    createForestWind() {
        const bufferSize = 2 * this.ctx.sampleRate;
        const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            output[i] = Math.random() * 2 - 1;
        }

        const noise = this.ctx.createBufferSource();
        noise.buffer = noiseBuffer;
        noise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(500, this.ctx.currentTime);
        filter.Q.setValueAtTime(3.0, this.ctx.currentTime);

        const lfo = this.ctx.createOscillator();
        lfo.frequency.setValueAtTime(0.2, this.ctx.currentTime);
        const lfoGain = this.ctx.createGain();
        lfoGain.gain.setValueAtTime(250, this.ctx.currentTime);

        lfo.connect(lfoGain);
        lfoGain.connect(filter.frequency);

        const gainNode = this.ctx.createGain();
        gainNode.gain.setValueAtTime(this.volumes.forest, this.ctx.currentTime);

        noise.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.ctx.destination);

        noise.start();
        lfo.start();
        this.activeNodes.forest = { gain: gainNode, sources: [noise, lfo] };
    }

    // Generator 4: 432Hz Focus Binaural Tone
    createFocusTone() {
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();

        osc1.type = 'sine';
        osc2.type = 'sine';

        osc1.frequency.setValueAtTime(432, this.ctx.currentTime);
        osc2.frequency.setValueAtTime(436, this.ctx.currentTime); // 4Hz Theta beat

        const gainNode = this.ctx.createGain();
        gainNode.gain.setValueAtTime(this.volumes.focus * 0.3, this.ctx.currentTime);

        osc1.connect(gainNode);
        osc2.connect(gainNode);
        gainNode.connect(this.ctx.destination);

        osc1.start();
        osc2.start();

        this.activeNodes.focus = { gain: gainNode, sources: [osc1, osc2] };
    }

    // Play Bell Chime Alert
    playChime() {
        this.initCtx();
        const now = this.ctx.currentTime;

        const harmonics = [220, 440, 880, 1320];
        harmonics.forEach((freq, index) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now);

            const vol = 0.3 / (index + 1);
            gain.gain.setValueAtTime(vol, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 3.0);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 3.0);
        });
    }
}

window.ambientEngine = new AmbientSoundEngine();
