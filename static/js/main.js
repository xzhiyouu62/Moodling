// ==========================================================================
// Moodling — Your Musical Elf Logic
// ==========================================================================

class MusicRecommendationApp {
    constructor() {
        this.form = document.getElementById('recommendationForm');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsGrid = document.getElementById('resultsGrid');
        this.historyList = document.getElementById('historyList');
        this.clearHistoryBtn = document.getElementById('clearHistoryBtn');

        this.init();
    }

    init() {
        this.initSliders();
        this.initForm();
        this.autoDetectTimePreference();
        this.loadHistory();
        
        if (this.clearHistoryBtn) {
            this.clearHistoryBtn.addEventListener('click', () => this.clearAllHistory());
        }
    }

    initSliders() {
        const sliders = ['mood', 'stress', 'fatigue'];
        sliders.forEach(id => {
            const slider = document.getElementById(id);
            const display = document.getElementById(`${id}Value`);
            if (slider && display) {
                slider.addEventListener('input', (e) => {
                    display.textContent = e.target.value;
                    this.updateSliderTrack(slider);
                });
                this.updateSliderTrack(slider);
            }
        });
    }

    updateSliderTrack(slider) {
        const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
        slider.style.background = `linear-gradient(to right, #1a1a1a 0%, #1a1a1a ${value}%, #e5e0d8 ${value}%, #e5e0d8 100%)`;
    }

    initForm() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmission();
            });
        }
    }

    async handleFormSubmission() {
        try {
            this.showLoading();
            this.hideResults();

            const formData = this.collectFormData();
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error(`Request failed: ${response.status}`);
            const data = await response.json();

            this.saveToHistory(data);
            this.hideLoading();
            this.displayResults(data);
            this.loadHistory();

        } catch (error) {
            this.hideLoading();
            this.showError(error.message);
        }
    }

    collectFormData() {
        const formData = new FormData(this.form);
        return {
            mood: parseInt(formData.get('mood')),
            stress: parseInt(formData.get('stress')),
            fatigue: parseInt(formData.get('fatigue')),
            weather: formData.get('weather'),
            time_preference: formData.get('time_preference'),
            needs: formData.getAll('needs')
        };
    }

    showLoading() {
        this.loadingOverlay.style.display = 'flex';
        this.loadingOverlay.style.opacity = '1';
    }

    hideLoading() {
        this.loadingOverlay.style.opacity = '0';
        setTimeout(() => { this.loadingOverlay.style.display = 'none'; }, 300);
    }

    hideResults() {
        this.resultsSection.style.display = 'none';
    }

    displayResults(data) {
        this.resultsGrid.innerHTML = '';
        
        data.recommendations.forEach((song, index) => {
            const explanation = data.explanations.find(exp => exp.song_title === song.title) || { explanation: "Moodling simply loves this vibe for you!" };
            const card = this.createEnhancedSongCard(song, index + 1, explanation);
            this.resultsGrid.appendChild(card);
        });

        this.resultsSection.style.display = 'block';
        
        window.scrollTo({
            top: this.resultsSection.offsetTop - 50,
            behavior: 'smooth'
        });
    }

    createEnhancedSongCard(song, rank, explanationData) {
        const container = document.createElement('div');
        container.className = 'song-card-container';
        container.style.borderBottom = '1px solid var(--border-color)';
        container.style.padding = '2rem 0';

        const songId = `exp-${rank}-${Date.now()}`;
        
        container.innerHTML = `
            <div class="song-card" style="border-bottom: none; padding: 0;">
                <div class="song-card__rank">${rank.toString().padStart(2, '0')}</div>
                <div class="song-card__info">
                    <h3 class="song-card__title">${song.title}</h3>
                    <p class="song-card__artist">${song.artist} — ${song.album} (${song.year})</p>
                    <button class="why-button" onclick="document.getElementById('${songId}').classList.toggle('open')">
                        Why to choose this?
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    </button>
                </div>
                <button class="song-card__play" onclick="window.open('${song.youtube_url}', '_blank')">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                </button>
            </div>
            
            <div id="${songId}" class="explanation-wrapper">
                <div class="explanation-card" style="border: none; padding: 2rem 0 0 80px; margin-bottom: 0; align-items: flex-start;">
                    <div class="moodling-avatar" style="margin-top: 0;">
                        <dotlottie-wc
                            src="https://lottie.host/699f7102-dda0-43e6-86db-ff961b5f49d8/J5AXGs1lJh.lottie"
                            style="width: 80px; height: 80px"
                            autoplay
                            loop
                        ></dotlottie-wc>
                    </div>
                    <div class="explanation-content">
                        <p class="explanation-text" style="font-size: 1.1rem; line-height: 1.8; white-space: pre-wrap; word-wrap: break-word;">${explanationData.explanation}</p>
                    </div>
                </div>
            </div>
        `;
        return container;
    }

    // History Logic
    saveToHistory(data) {
        const history = JSON.parse(localStorage.getItem('moodling_history') || '[]');
        const entry = {
            id: Date.now(),
            timestamp: new Date().toLocaleString(),
            mood: data.user_state.mood,
            top_song: data.recommendations[0],
            all_data: data
        };
        history.unshift(entry);
        localStorage.setItem('moodling_history', JSON.stringify(history.slice(0, 10)));
    }

    loadHistory() {
        if (!this.historyList) return;
        const history = JSON.parse(localStorage.getItem('moodling_history') || '[]');
        
        if (history.length === 0) {
            this.historyList.innerHTML = '<p style="color: var(--text-muted); font-size: 1.1rem; font-style: italic;">No history yet. Let\'s create some memories!</p>';
            if (this.clearHistoryBtn) this.clearHistoryBtn.style.display = 'none';
            return;
        }

        if (this.clearHistoryBtn) this.clearHistoryBtn.style.display = 'block';

        this.historyList.innerHTML = '';
        history.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'song-card';
            div.style.padding = '1.5rem 0';
            div.innerHTML = `
                <div class="song-card__rank" style="font-size: 0.8rem; font-family: var(--font-sans); opacity: 0.5;">MEM</div>
                <div class="song-card__info" style="cursor: pointer;">
                    <h3 class="song-card__title" style="font-size: 1.35rem; font-family: var(--font-serif); margin: 0;">History ${history.length - index}</h3>
                    <p class="song-card__artist" style="margin-top: 0.25rem; font-size: 0.9rem;">Mood: ${item.mood} — ${item.top_song.title} (${item.timestamp.split(',')[0]})</p>
                </div>
                <div style="display: flex; align-items: center;">
                    <button class="delete-item-btn" onclick="event.stopPropagation(); window.app.deleteHistoryItem(${item.id})">Delete</button>
                </div>
            `;
            // Add click listener to the info part only
            div.querySelector('.song-card__info').onclick = () => this.displayResults(item.all_data);
            this.historyList.appendChild(div);
        });
    }

    deleteHistoryItem(id) {
        let history = JSON.parse(localStorage.getItem('moodling_history') || '[]');
        history = history.filter(item => item.id !== id);
        localStorage.setItem('moodling_history', JSON.stringify(history));
        this.loadHistory();
    }

    clearAllHistory() {
        if (confirm('Are you sure you want to clear all history?')) {
            localStorage.removeItem('moodling_history');
            this.loadHistory();
        }
    }

    autoDetectTimePreference() {
        const hour = new Date().getHours();
        const select = document.querySelector('select[name="time_preference"]');
        if (select) {
            if (hour >= 6 && hour < 12) select.value = 'morning';
            else if (hour >= 12 && hour < 18) select.value = 'afternoon';
            else if (hour >= 18 && hour < 22) select.value = 'evening';
            else select.value = 'night';
        }
    }

    showError(message) {
        alert(message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new MusicRecommendationApp();
});
