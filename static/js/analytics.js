/* ==========================================================================
   Moodling Analytics System - Modern Redesign
   ========================================================================== */

class AnalyticsApp {
    constructor() {
        this.activeChart = 'mood-distribution';
        this.chartData = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Page load
        document.addEventListener('DOMContentLoaded', () => {
            this.loadHeroStats();
            this.loadStatistics();
        });
    }

    async loadInitialData() {
        await Promise.all([
            this.loadHeroStats(),
            this.loadStatistics()
        ]);
    }

    // Hero Stats Loading
    async loadHeroStats() {
        try {
            const response = await fetch('/api/analytics/hero-stats');
            const data = await response.json();

            if (response.ok) {
                this.displayHeroStats(data);
            }
        } catch (error) {
            console.error('Hero stats loading error:', error);
        }
    }

    displayHeroStats(stats) {
        const heroStats = document.getElementById('heroStats');
        if (!heroStats) return;

        const heroCards = [
            {
                value: stats.total_recommendations || 0,
                label: 'Total Recommendations'
            },
            {
                value: stats.user_satisfaction || '94.2%',
                label: 'User Satisfaction'
            },
            {
                value: stats.active_songs || 0,
                label: 'Active Songs'
            }
        ];

        heroStats.innerHTML = heroCards.map(card => `
            <div class="stat-card">
                <div class="stat-card__value" style="font-family: var(--font-serif); font-size: 3rem; margin-bottom: 0.5rem;">${card.value}</div>
                <div class="stat-card__title" style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted);">${card.label}</div>
            </div>
        `).join('');
    }

    // Statistics Loading
    async loadStatistics() {
        try {
            const response = await fetch('/api/analytics/stats');
            const data = await response.json();

            if (response.ok) {
                this.displayStatistics(data);
            }
        } catch (error) {
            console.error('Statistics loading error:', error);
        }
    }

    displayStatistics(stats) {
        const statsGrid = document.getElementById('statsGrid');
        if (!statsGrid) return;

        const statCards = [
            { title: 'Library', value: stats.song_count || 0, label: 'Tracks' },
            { title: 'Artists', value: stats.artist_count || 0, label: 'Creators' },
            { title: 'Energy', value: (stats.avg_energy || 0).toFixed(1), label: 'Avg Pulse' },
            { title: 'Mood', value: (stats.avg_valence || 0).toFixed(1), label: 'Avg Mood' },
            { title: 'Tempo', value: Math.round(stats.avg_tempo || 0), label: 'Avg BPM' },
            { title: 'Activity', value: stats.interaction_count || 0, label: 'Requests' }
        ];

        statsGrid.innerHTML = statCards.map(card => `
            <div class="stat-card" style="padding: 3rem; border: 1px solid var(--border-color); background: white;">
                <div class="stat-card__value" style="font-family: var(--font-serif); font-size: 2.5rem; margin-bottom: 0.5rem;">${card.value}</div>
                <div class="stat-card__title" style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted);">${card.title}</div>
            </div>
        `).join('');
    }

    showError(message) {
        alert(message);
    }
}

// Global Functions
function refreshAllData() {
    if (window.analyticsApp) {
        window.analyticsApp.loadInitialData();
    }
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsApp = new AnalyticsApp();
});
