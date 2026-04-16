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
            你是一位專業的音樂策展小精靈 Moodling，擅長從音樂心理學角度解釋選曲邏輯。
            
            用戶狀態：心情 {mood}/10, 壓力 {stress}/10, 疲勞 {fatigue}/10。
            推薦歌曲：{song['artist']} - 《{song['title']}》
            歌曲特徵：能量指數 {energy}/100, 情感愉悅度 {valence}/100, 風格標籤 [{tags}]。
            
            任務：請撰寫一段 80-120 字的「推薦深度解析」。
            
            要求：
            1. 邏輯對接：具體說明為什麼這首歌的 [能量/愉悅度/風格標籤] 能對應 [用戶的心情/壓力/疲勞]。
            2. 音樂性描述：描述歌曲的聽感（例如：是跳動的貝斯、清冷的鋼琴、還是層層遞進的人聲）如何影響用戶目前的心理。
            3. 禁止敷衍：絕對不要說「這首歌很適合你」或「希望帶給你力量」。
            4. 語氣：專業、富有洞察力、且帶有靈性，像是一位資深的電台主持人。
            5. 直接開始解析，不要任何客套的開場白（如：哎呀、你好）。
            """
            
            text = ""
            if self.client:
                try:
                    resp = self.client.models.generate_content(
                        model='gemini-2.5-flash',
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
                    text = f"選曲解析：考慮到您的壓力指數({stress}/10)，《{song['title']}》的 {tags} 節奏能與您的心跳共振，透過其 {energy} 水平的能量緩解心理負荷。"
            else:
                text = f"選曲分析：基於您的數據，這首歌的 {tags} 氛圍正對接您當下的心理需求。"

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
