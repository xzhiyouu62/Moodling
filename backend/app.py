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

# Vercel sets env vars directly, but this helps local dev
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
        # Prefer GOOGLE_API_KEY from environment
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini Client initialized.")
            except Exception as e:
                logger.error(f"Failed to init Gemini: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("No GOOGLE_API_KEY found.")

    def generate(self, state, songs):
        explanations = []
        for i, song in enumerate(songs, 1):
            # 提供更多細節讓 AI 發揮，避免公式化
            tags = ", ".join(song.get('tags', []))
            prompt = f"""
            你是一位很有靈性的音樂小精靈 Moodling。現在用戶的心情是 {state.get('mood')}/10，壓力是 {state.get('stress')}/10。
            我想推薦他聽 {song['artist']} 的《{song['title']}》（標籤：{tags}）。
            
            請像個懂音樂的知心好友，隨性且溫暖地聊聊這首歌。
            要求：
            1. 絕對不要使用「這首歌非常適合你現在的狀態」或「希望帶給你力量」這種老套的公式。
            2. 請根據歌曲的氛圍（如：{tags}）描述一種具體的畫面感或情感連結。
            3. 字數大約 60-100 字，語氣要自然，不要像機器人。
            4. 每次的開頭都要有變化。
            """
            
            text = ""
            if self.client:
                try:
                    resp = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[{'parts': [{'text': prompt}]}],
                        config={
                            'temperature': 0.9, # 增加創意與變化
                            'top_p': 0.95,
                            'max_output_tokens': 400
                        }
                    )
                    text = resp.text.strip()
                except Exception as e:
                    logger.error(f"AI generation failed: {e}")
                    fallbacks = [
                        f"這首《{song['title']}》的旋律剛好能接住你現在的情緒，聽聽看吧。",
                        f"Moodling 覺得 {song['artist']} 的聲音在這種時候聽起來特別溫柔，分享給你。",
                        f"閉上眼聽這首《{song['title']}》，或許能讓你的心情稍微透透氣。"
                    ]
                    text = random.choice(fallbacks)
            else:
                text = f"這首 {song['artist']} 的作品正帶著一種獨特的氛圍，希望能與你產生共鳴。"

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
    # Default to 5001 for local, but Vercel uses its own
    app.run(debug=True, host='0.0.0.0', port=5001)
