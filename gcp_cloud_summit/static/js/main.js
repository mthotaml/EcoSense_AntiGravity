/**
 * Google Cloud Tech Summit 2026 - Main JavaScript Engine
 * Handles live search, category pill filtering, speaker lookups, and modal dialogs.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const categorySelect = document.getElementById('categorySelect');
    const categoryPillsContainer = document.getElementById('categoryPills');
    const scheduleTimeline = document.getElementById('scheduleTimeline');
    const talkCards = document.querySelectorAll('.talk-card');
    const resultsCount = document.getElementById('resultsCount');
    const noResults = document.getElementById('noResults');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');

    const talkModal = document.getElementById('talkModal');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const modalContent = document.getElementById('modalContent');

    // Data Store
    const allTalks = window.INITIAL_TALKS || [];
    const eventInfo = window.EVENT_INFO || {};

    let currentCategory = 'all';
    let currentSearch = '';

    // ==========================================
    // Event Listeners
    // ==========================================

    // Instant Search Input
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.trim().toLowerCase();
            toggleClearSearchButton();
            applyFilters();
        });
    }

    // Clear Search Button
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            currentSearch = '';
            toggleClearSearchButton();
            applyFilters();
            searchInput.focus();
        });
    }

    // Category Select Dropdown
    if (categorySelect) {
        categorySelect.addEventListener('change', (e) => {
            currentCategory = e.target.value;
            updateCategoryPillsState();
            applyFilters();
        });
    }

    // Category Pills Click
    if (categoryPillsContainer) {
        categoryPillsContainer.addEventListener('click', (e) => {
            const pill = e.target.closest('.pill-btn');
            if (!pill) return;

            currentCategory = pill.dataset.category;
            categorySelect.value = currentCategory;
            updateCategoryPillsState();
            applyFilters();
        });
    }

    // Reset Filters Button
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', () => {
            currentCategory = 'all';
            currentSearch = '';
            searchInput.value = '';
            categorySelect.value = 'all';
            toggleClearSearchButton();
            updateCategoryPillsState();
            applyFilters();
        });
    }

    // Modal Close Events
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeModal);
    }

    if (talkModal) {
        talkModal.addEventListener('click', (e) => {
            if (e.target === talkModal) {
                closeModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !talkModal.classList.contains('hidden')) {
                closeModal();
            }
        });
    }

    // ==========================================
    // Core Filter Logic
    // ==========================================

    function applyFilters() {
        let visibleCount = 0;

        talkCards.forEach(card => {
            const talkId = parseInt(card.dataset.id, 10);
            const talk = allTalks.find(t => t.id === talkId);
            if (!talk) return;

            // Check Category
            const categoryMatch = (currentCategory === 'all' || talk.category.toLowerCase() === currentCategory.toLowerCase());

            // Check Search Term
            let searchMatch = true;
            if (currentSearch) {
                const titleMatch = talk.title.toLowerCase().includes(currentSearch);
                const catMatch = talk.category.toLowerCase().includes(currentSearch);
                const descMatch = talk.description.toLowerCase().includes(currentSearch);
                const speakerMatch = talk.speakers.some(s => 
                    `${s.first_name} ${s.last_name}`.toLowerCase().includes(currentSearch) ||
                    s.company.toLowerCase().includes(currentSearch) ||
                    s.role.toLowerCase().includes(currentSearch)
                );

                searchMatch = (titleMatch || catMatch || descMatch || speakerMatch);
            }

            if (categoryMatch && searchMatch) {
                card.classList.remove('hidden');
                visibleCount++;
            } else {
                card.classList.add('hidden');
            }
        });

        // Update Counter
        if (resultsCount) {
            resultsCount.textContent = `Showing ${visibleCount} of ${allTalks.length} talks`;
        }

        // Handle Empty State
        if (visibleCount === 0) {
            noResults.classList.remove('hidden');
        } else {
            noResults.classList.add('hidden');
        }
    }

    function toggleClearSearchButton() {
        if (currentSearch.length > 0) {
            clearSearchBtn.style.display = 'block';
        } else {
            clearSearchBtn.style.display = 'none';
        }
    }

    function updateCategoryPillsState() {
        const pills = categoryPillsContainer.querySelectorAll('.pill-btn');
        pills.forEach(pill => {
            if (pill.dataset.category.toLowerCase() === currentCategory.toLowerCase()) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });
    }

    // ==========================================
    // Modal Functions
    // ==========================================

    window.openTalkModal = function(talkId) {
        const talk = allTalks.find(t => t.id === talkId);
        if (!talk) return;

        const categoryClass = talk.category.toLowerCase().replace(/ & /g, '-').replace(/ /g, '-');

        const speakersHtml = talk.speakers.map(s => `
            <div class="modal-speaker-card">
                <img src="${s.avatar}" alt="${s.first_name} ${s.last_name}" class="modal-speaker-img">
                <div class="modal-speaker-details">
                    <div class="modal-speaker-name">${s.first_name} ${s.last_name}</div>
                    <div class="modal-speaker-bio">${s.role} at <strong>${s.company}</strong></div>
                </div>
                <a href="${s.linkedin}" target="_blank" rel="noopener noreferrer" class="linkedin-btn" title="View LinkedIn Profile">
                    <i class="fa-brands fa-linkedin fa-lg"></i>
                </a>
            </div>
        `).join('');

        modalContent.innerHTML = `
            <div class="modal-talk-header">
                <div class="talk-meta-row">
                    <span class="category-tag tag-${categoryClass}">${talk.category}</span>
                    <span class="room-tag"><i class="fa-solid fa-door-open"></i> ${talk.room}</span>
                </div>
                <h2 class="modal-talk-title">${talk.title}</h2>
                <div class="badge lunch-time-badge">
                    <i class="fa-regular fa-clock"></i> ${talk.time} &bull; TALK #${talk.id}
                </div>
            </div>

            <div class="modal-talk-section" style="margin-bottom: 24px;">
                <h4 style="color: var(--text-muted); text-transform: uppercase; font-size: 0.85rem; margin-bottom: 8px;">Abstract & Overview</h4>
                <p style="font-size: 1rem; color: var(--text-secondary); line-height: 1.6;">${talk.description}</p>
            </div>

            <div class="modal-speakers-section">
                <h4>Speakers (${talk.speakers.length})</h4>
                ${speakersHtml}
            </div>
        `;

        talkModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    };

    function closeModal() {
        talkModal.classList.add('hidden');
        document.body.style.overflow = '';
    }
});
