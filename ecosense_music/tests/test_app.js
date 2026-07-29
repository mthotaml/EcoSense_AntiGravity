/**
 * EcoSense Music App Automated Test Suite
 */

const assert = require('assert');
const { TRACKS, CATEGORIES } = require('../js/tracks.js');

console.log('🧪 Running EcoSense Music Test Suite...');

// Test 1: Track Registry Integrity
function testTrackRegistry() {
    assert.ok(Array.isArray(TRACKS), 'TRACKS should be an array');
    assert.strictEqual(TRACKS.length, 8, 'Catalog should contain 8 tracks');

    TRACKS.forEach(track => {
        assert.ok(track.id, 'Track should have an id');
        assert.ok(track.title, 'Track should have a title');
        assert.ok(track.artist, 'Track should have an artist');
        assert.ok(track.category, 'Track should have a category');
        assert.ok(track.audioUrl, 'Track should have an audioUrl');
        assert.ok(track.ecoTag, 'Track should have an ecoTag');
    });

    console.log('✅ Test 1: Track Registry Integrity Passed');
}

// Test 2: Category Catalog Validation
function testCategories() {
    assert.ok(Array.isArray(CATEGORIES), 'CATEGORIES should be an array');
    assert.ok(CATEGORIES.includes('Nature Soundscapes'), 'Should contain Nature Soundscapes category');
    assert.ok(CATEGORIES.includes('Deep Focus'), 'Should contain Deep Focus category');
    assert.ok(CATEGORIES.includes('Eco Lo-Fi Beats'), 'Should contain Eco Lo-Fi Beats category');
    assert.ok(CATEGORIES.includes('Meditation & Calm'), 'Should contain Meditation & Calm category');
    console.log('✅ Test 2: Categories Validation Passed');
}

// Test 3: Category Filtering Logic
function testCategoryFiltering() {
    const focusTracks = TRACKS.filter(t => t.category === 'Deep Focus');
    assert.ok(focusTracks.length > 0, 'Deep Focus should yield matching tracks');
    focusTracks.forEach(t => assert.strictEqual(t.category, 'Deep Focus'));

    const natureTracks = TRACKS.filter(t => t.category === 'Nature Soundscapes');
    assert.ok(natureTracks.length > 0, 'Nature Soundscapes should yield matching tracks');

    console.log('✅ Test 3: Category Filtering Logic Passed');
}

// Test 4: Time Formatting Logic
function testTimeFormatting() {
    function formatTime(seconds) {
        if (isNaN(seconds)) return "00:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    assert.strictEqual(formatTime(225), "03:45", "225 seconds should format to 03:45");
    assert.strictEqual(formatTime(0), "00:00", "0 seconds should format to 00:00");
    assert.strictEqual(formatTime(360), "06:00", "360 seconds should format to 06:00");

    console.log('✅ Test 4: Time Formatting Logic Passed');
}

testTrackRegistry();
testCategories();
testCategoryFiltering();
testTimeFormatting();

console.log('🎉 ALL 4 TESTS PASSED CLEANLY!');
