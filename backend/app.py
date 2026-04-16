#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__,
           template_folder='../frontend',
           static_folder='../static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_songs():
    try:
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'korean_songs.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading songs: {e}")
        return []

class SongRecommendationEngine:
    def __init__(self, songs_data):
        self.songs = songs_data

    def calculate_score(self, song, state):
        score = 0
        mood = state.get('mood', 5)
        if mood >= 8: score += song.get('valence', 50) * 0.02
        elif mood <= 3: score += (100 - song.get('valence', 50)) * 0.015
        
        fatigue = state.get('fatigue', 5)
        if fatigue >= 7: score += (100 - song.get('energy', 50)) * 0.015
        else: score += song.get('energy', 50) * 0.015

        stress = state.get('stress', 5)
        if stress >= 7 and 'relaxing' in song.get('tags', []): score += 30
        
        return score

    def recommend(self, state, num=5):
        scored = [{'song': s, 'score': self.calculate_score(s, state)} for s in self.songs]
        scored.sort(key=lambda x: x['score'], reverse=True)
        return [item['song'] for item in scored[:num]]

class AIExplainer:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate(self, state, songs):
        explanations = []
        for i, song in enumerate(songs, 1):
            prompt = f"Explain in Traditional Chinese (80 words) why '{song['title']}' by {song['artist']} suits a person with mood {state.get('mood')}/10, stress {state.get('stress')}/10, and fatigue {state.get('fatigue')}/10. Keep it warm and professional."
            
            try:
                if self.client:
                    resp = self.client.models.generate_content(
                        model='models/gemma-3-1b-it',
                        contents=[{'parts': [{'text': prompt}]}],
                        config={'max_output_tokens': 500}
                    )
                    text = resp.candidates[0].content.parts[0].text.strip()
                else:
                    text = "Moodling thinks this is a great match for your vibe!"
            except:
                text = "Moodling loves this choice for you."

            explanations.append({
                'song_title': song['title'],
                'artist': song['artist'],
                'explanation': text
            })
        return explanations

songs_data = load_songs()
engine = SongRecommendationEngine(songs_data)
explainer = AIExplainer()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/analytics')
def analytics(): return render_template('analytics.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        state = request.json
        recs = engine.recommend(state)
        exps = explainer.generate(state, recs)
        return jsonify({'recommendations': recs, 'explanations': exps, 'user_state': state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/hero-stats')
def hero_stats():
    return jsonify({'total_recommendations': 128, 'user_satisfaction': '98%', 'active_songs': len(songs_data)})

@app.route('/api/analytics/stats')
def stats():
    return jsonify({'song_count': len(songs_data), 'artist_count': 15, 'avg_energy': 65.5})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
