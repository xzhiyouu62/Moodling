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
            # 整合更深度的數據供 AI 分析
            tags = ", ".join(song.get('tags', []))
            energy = song.get('energy', 50)
            valence = song.get('valence', 50)
            mood = state.get('mood', 5)
            stress = state.get('stress', 5)
            fatigue = state.get('fatigue', 5)

            prompt = f"""
            你是 Moodling，一個對音樂和情緒很有洞察力的音樂小精靈。

            目前狀況：有人現在的心情是 {mood}/10 開心，{stress}/10 壓力，{fatigue}/10 有活力。

            我為他們選擇了 {song['artist']} 的《{song['title']}》。這首歌有 {tags} 的特質，能量程度是 {energy}，情感色調是 {valence}。

            請寫一個詳細、個人化的解釋（80-120字），分析為什麼這首特定的歌曲符合他們此刻的心情狀態。

            重點分析：
            1. 這首歌的獨特之處（節奏、旋律、演唱風格、樂器編排）
            2. 這些音樂元素如何針對他們當前的情感需求
            3. 這首歌現在會對他們產生什麼心理/情感效果
            4. 要針對這首歌的具體特色，不要用通用描述

            寫作風格：
            - 像一個真正懂音樂的朋友那樣溫暖對話
            - 要有深度見解但保持親切
            - 詳細解釋選擇的「為什麼」
            - 必須使用繁體中文
            - 專注於具體的音樂分析，避免空泛讚美
            """
            
            text = ""
            if self.client:
                try:
                    resp = self.client.models.generate_content(
                        model='models/gemma-3-1b-it',
                        contents=[{'parts': [{'text': prompt}]}],
                        config={
                            'temperature': 0.7, 
                            'top_p': 0.9,
                            'max_output_tokens': 600
                        }
                    )
                    text = resp.text.strip()
                except Exception as e:
                    logger.error(f"AI generation failed: {e}")
                    text = f"這首《{song['title']}》有種 {tags} 的感覺，剛好跟你現在的狀態很搭！聽起來會讓心情更順暢一些。"
            else:
                text = f"《{song['title']}》這首歌的 {tags} 氛圍，感覺很適合你現在的心情呢～"

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
