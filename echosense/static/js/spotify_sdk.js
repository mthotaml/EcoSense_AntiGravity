/**
 * Spotify Web Playback SDK Wrapper
 */

class EchoSenseSpotifySDK {
    constructor() {
        this.player = null;
        this.deviceId = null;
        this.isReady = false;
    }

    init() {
        window.onSpotifyWebPlaybackSDKReady = () => {
            this.player = new Spotify.Player({
                name: 'EchoSense Web Player',
                getOAuthToken: cb => { cb('mock_access_token'); },
                volume: 0.8
            });

            this.player.addListener('ready', ({ device_id }) => {
                this.deviceId = device_id;
                this.isReady = true;
                console.log('✅ Spotify Web Playback SDK Ready with Device ID:', device_id);
            });

            this.player.addListener('player_state_changed', state => {
                if (state) {
                    document.dispatchEvent(new CustomEvent('spotifyStateChanged', { detail: state }));
                }
            });

            this.player.connect();
        };
    }
}

window.spotifySDK = new EchoSenseSpotifySDK();
window.spotifySDK.init();
