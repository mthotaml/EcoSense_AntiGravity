"""
Generate clean, local WAV audio track files for EchoSense demo.
Guarantees 100% offline, zero-CORS audio playback for all tracks.
"""

import os
import math
import struct
import wave

def generate_wav(filename, freq1, freq2, duration=8.0, sample_rate=44100):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    num_samples = int(duration * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2)      # Stereo
        wav_file.setsampwidth(2)      # 16-bit PCM
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            # Smooth fade in and fade out envelope
            envelope = math.sin(math.pi * (i / num_samples))
            
            # Harmonic sine wave tone
            val1 = math.sin(2 * math.pi * freq1 * t)
            val2 = math.sin(2 * math.pi * freq2 * t)
            
            sample_l = int((val1 * 0.4 + val2 * 0.3) * envelope * 32767)
            sample_r = int((val1 * 0.3 + val2 * 0.4) * envelope * 32767)
            
            # Clamp 16-bit integer values
            sample_l = max(-32768, min(32767, sample_l))
            sample_r = max(-32768, min(32767, sample_r))
            
            frames.extend(struct.pack('<hh', sample_l, sample_r))
            
        wav_file.writeframes(frames)
    print(f"✅ Generated local audio: {filename}")

if __name__ == "__main__":
    audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'audio'))
    
    # 8 Clean Harmonic Track WAV Files
    generate_wav(os.path.join(audio_dir, 'track101.wav'), 432.0, 528.0) # Deep Focus
    generate_wav(os.path.join(audio_dir, 'track102.wav'), 261.6, 392.0) # Nature Soundscape
    generate_wav(os.path.join(audio_dir, 'track103.wav'), 329.6, 493.8) # Eco Lo-Fi
    generate_wav(os.path.join(audio_dir, 'track104.wav'), 220.0, 440.0) # Meditation Zen
    generate_wav(os.path.join(audio_dir, 'track105.wav'), 432.0, 648.0) # Solar Drift
    generate_wav(os.path.join(audio_dir, 'track106.wav'), 174.0, 285.0) # Rainforest
    generate_wav(os.path.join(audio_dir, 'track107.wav'), 349.2, 523.2) # Green Leaf
    generate_wav(os.path.join(audio_dir, 'track108.wav'), 528.0, 792.0) # Tibetan Bowl
