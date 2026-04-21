#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
import google.genai as genai
import requests
import urllib.parse
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

class HybridMusicEngine:
    def __init__(self):
        self.lastfm_key = os.getenv('LASTFM_API_KEY')
        self.lastfm_base_url = 'https://ws.audioscrobbler.com/2.0/'
        self.itunes_base_url = 'https://itunes.apple.com/search'

    def mood_to_tags(self, state):
        """將用戶情緒轉換為音樂標籤"""
        mood = state.get('mood', 5)
        stress = state.get('stress', 5)
        energy = state.get('fatigue', 5)

        tags = ['korean', 'k-pop']

        # 情緒標籤映射
        if mood >= 8:
            tags.extend(['happy', 'upbeat', 'cheerful', 'joyful'])
        elif mood >= 6:
            tags.extend(['uplifting', 'positive', 'feel-good'])
        elif mood <= 3:
            tags.extend(['sad', 'melancholy', 'emotional', 'ballad'])
        else:
            tags.extend(['peaceful', 'calm', 'mellow'])

        # 能量程度標籤
        if energy >= 8:
            tags.extend(['energetic', 'dance', 'uplifting', 'powerful'])
        elif energy >= 6:
            tags.extend(['upbeat', 'lively'])
        elif energy <= 3:
            tags.extend(['chill', 'relaxing', 'ambient', 'soft'])
        else:
            tags.extend(['moderate', 'easy-listening'])

        # 壓力程度標籤
        if stress <= 3:
            tags.extend(['chill', 'peaceful', 'relaxing'])
        elif stress >= 7:
            tags.extend(['intense', 'powerful', 'energetic'])

        return list(set(tags))[:6]  # 去重並限制標籤數量

    def search_lastfm_by_tags(self, tags, limit=20):
        """使用 Last.fm API 根據標籤搜索音樂"""
        try:
            tracks = []
            seen_tracks = set()  # 避免重複

            # 方法1: 直接搜索 K-pop 和韓國相關標籤
            kpop_tags = ['k-pop', 'korean', 'kpop']
            for tag in kpop_tags:
                if len(tracks) >= limit:
                    break

                params = {
                    'method': 'tag.gettoptracks',
                    'tag': tag,
                    'api_key': self.lastfm_key,
                    'format': 'json',
                    'limit': 50  # 增加獲取數量
                }

                response = requests.get(self.lastfm_base_url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'tracks' in data and 'track' in data['tracks']:
                        for track in data['tracks']['track']:
                            if len(tracks) >= limit:
                                break

                            artist_name = track.get('artist', {}).get('name', '') if isinstance(track.get('artist'), dict) else str(track.get('artist', ''))
                            track_name = track.get('name', '')
                            track_key = f"{artist_name}-{track_name}".lower()

                            # 避免重複並檢查是否為韓國音樂
                            if track_key not in seen_tracks and self.is_korean_music(artist_name, track_name):
                                seen_tracks.add(track_key)
                                tracks.append({
                                    'name': track_name,
                                    'artist': artist_name,
                                    'lastfm_url': track.get('url', ''),
                                    'playcount': track.get('playcount', 0)
                                })

            # 方法2: 如果還是不夠，搜索具體韓國藝人
            if len(tracks) < limit:
                korean_artists = ['BTS', 'BLACKPINK', 'TWICE', 'Red Velvet', 'IU', 'Stray Kids', 'ITZY', 'aespa']

                for artist in korean_artists:
                    if len(tracks) >= limit:
                        break

                    params = {
                        'method': 'artist.gettoptracks',
                        'artist': artist,
                        'api_key': self.lastfm_key,
                        'format': 'json',
                        'limit': 10
                    }

                    response = requests.get(self.lastfm_base_url, params=params, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if 'toptracks' in data and 'track' in data['toptracks']:
                            for track in data['toptracks']['track']:
                                if len(tracks) >= limit:
                                    break

                                track_key = f"{artist}-{track.get('name', '')}".lower()
                                if track_key not in seen_tracks:
                                    seen_tracks.add(track_key)
                                    tracks.append({
                                        'name': track.get('name', ''),
                                        'artist': artist,
                                        'lastfm_url': track.get('url', ''),
                                        'playcount': track.get('playcount', 0)
                                    })

            return tracks[:limit]

        except Exception as e:
            logger.error(f"Last.fm API error: {e}")
            return []

    def is_korean_music(self, artist, track):
        """簡單判斷是否為韓國音樂"""
        korean_indicators = [
            'bts', 'blackpink', 'twice', 'red velvet', 'girls generation', 'snsd',
            'exo', 'bigbang', 'iu', 'stray kids', 'itzy', 'aespa', 'newjeans',
            'seventeen', 'nct', 'mamamoo', 'super junior', 'shinee', 'wonder girls',
            '방탄소년단', '블랙핑크', '트와이스', '레드벨벳', '소녀시대',
            '아이유', 'korea', 'k-pop', 'kpop'
        ]

        search_text = f"{artist} {track}".lower()
        return any(indicator in search_text for indicator in korean_indicators)

    def enrich_with_itunes(self, tracks):
        """使用 iTunes API 豐富音樂資料"""
        enriched = []

        for track in tracks:
            try:
                # iTunes 搜索
                search_term = f"{track['artist']} {track['name']}"
                params = {
                    'term': search_term,
                    'media': 'music',
                    'entity': 'song',
                    'limit': 1,
                    'country': 'KR'  # 韓國地區
                }

                response = requests.get(self.itunes_base_url, params=params, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        itunes_track = data['results'][0]

                        enriched.append({
                            'title': track['name'],
                            'artist': track['artist'],
                            'album': itunes_track.get('collectionName', 'Unknown Album'),
                            'year': itunes_track.get('releaseDate', '')[:4] if itunes_track.get('releaseDate') else 'Unknown',
                            'preview_url': itunes_track.get('previewUrl'),
                            'youtube_url': itunes_track.get('trackViewUrl'),  # 使用 iTunes 連結
                            'album_art': itunes_track.get('artworkUrl100'),
                            'genre': itunes_track.get('primaryGenreName', 'K-Pop'),
                            'playcount': track.get('playcount', 0)
                        })
                    else:
                        # 如果 iTunes 找不到，使用 Last.fm 數據
                        enriched.append({
                            'title': track['name'],
                            'artist': track['artist'],
                            'album': 'Unknown Album',
                            'year': 'Unknown',
                            'preview_url': None,
                            'youtube_url': track.get('lastfm_url'),
                            'album_art': None,
                            'genre': 'K-Pop',
                            'playcount': track.get('playcount', 0)
                        })

            except Exception as e:
                logger.error(f"iTunes API error for {track['name']}: {e}")
                enriched.append({
                    'title': track['name'],
                    'artist': track['artist'],
                    'album': 'Unknown Album',
                    'year': 'Unknown',
                    'preview_url': None,
                    'youtube_url': track.get('lastfm_url'),
                    'album_art': None,
                    'genre': 'K-Pop',
                    'playcount': track.get('playcount', 0)
                })

        return enriched

    def recommend(self, state, num=5):
        """主要推薦方法"""
        try:
            # Step 1: 根據情緒生成標籤
            tags = self.mood_to_tags(state)
            logger.info(f"Generated tags for mood: {tags}")

            # Step 2: 使用 Last.fm 搜索
            lastfm_tracks = self.search_lastfm_by_tags(tags, limit=num*2)
            logger.info(f"Found {len(lastfm_tracks)} tracks from Last.fm")

            # Step 3: 使用 iTunes 豐富數據
            enriched_tracks = self.enrich_with_itunes(lastfm_tracks[:num])

            return enriched_tracks

        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            # 降級到簡單回應
            return [{
                'title': 'Spring Day',
                'artist': 'BTS',
                'album': 'You Never Walk Alone',
                'year': '2017',
                'preview_url': None,
                'youtube_url': '#',
                'album_art': None,
                'genre': 'K-Pop',
                'playcount': 0
            }]

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

engine = HybridMusicEngine()
explainer = AIExplainer()

@app.route('/')
def index(): 
    return render_template('index.html', recommendations=None)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get data from standard form instead of JSON
        state = {
            'mood': int(request.form.get('mood', 5)),
            'stress': int(request.form.get('stress', 5)),
            'fatigue': int(request.form.get('fatigue', 5)),
            'weather': request.form.get('weather', 'sunny'),
            'time_preference': request.form.get('time_preference', 'afternoon')
        }
        
        recs = engine.recommend(state)
        exps = explainer.generate(state, recs)
        
        # Combine recs and exps for easier templating
        combined_results = []
        for i, song in enumerate(recs):
            exp = next((e for e in exps if e['song_title'] == song['title']), {'explanation': 'Enjoy this vibe!'})
            song['explanation'] = exp['explanation']
            combined_results.append(song)
            
        return render_template('index.html', 
                             recommendations=combined_results, 
                             user_state=state,
                             scroll_to_results=True)
    except Exception as e:
        logger.error(f"Submit error: {e}")
        return render_template('index.html', error=str(e))

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
