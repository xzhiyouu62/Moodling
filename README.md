# 🎵 韓文歌曲推薦AI決策機器人

一個智能的韓文歌曲推薦系統，根據你的心情、壓力、疲勞程度和天氣狀況，為你推薦最適合的韓文歌曲並提供AI解釋。

![專案截圖](https://via.placeholder.com/800x400/667eea/ffffff?text=Korean+Song+AI+Recommender)

## ✨ 特色功能

### 🧠 智能決策引擎
- **多維度分析**：結合心情、課業壓力、疲勞程度、天氣等因素
- **個性化推薦**：根據你的當下狀態提供最適合的歌曲
- **動態評分**：使用先進的算法計算歌曲匹配度

### 🎧 豐富的歌曲資料庫
- **20+首精選韓文歌曲**：涵蓋BTS、IU、BLACKPINK等知名藝人
- **詳細歌曲屬性**：
  - `energy` (能量指數): 0-100，表示歌曲的節奏強度
  - `valence` (快樂指數): 0-100，表示歌曲的情感色彩
  - `tempo` (節拍速度): BPM，歌曲的節拍每分鐘
  - `tags` (標籤): 放鬆、提神、浪漫、動感等情境標籤

### 🤖 AI智能解釋
- **推薦理由說明**：AI分析為什麼推薦特定歌曲
- **匹配因素分析**：詳細說明歌曲與你狀態的匹配點
- **個性化建議**：提供聆聽建議和心情調節提示

### 🌟 現代化用戶界面
- **響應式設計**：支援電腦、平板、手機
- **直觀操作**：滑桿、選項卡等友善的交互元素
- **美觀動畫**：流暢的過渡效果和載入動畫
- **韓流風格**：專為K-pop愛好者設計的視覺風格

### 📊 數據科學整合
- **matplotlib inline支援**：在Jupyter環境中直接顯示圖表
- **numpy & pandas**：強大的數據處理和分析能力
- **數據視覺化**：歌曲特徵分布、用戶行為分析
- **統計分析**：相關性分析、聚類分析、推薦模擬
- **互動式儀表板**：實時數據分析與監控

## 🚀 快速開始

### 環境需求
- Python 3.8 或更高版本
- pip 套件管理器
- 現代化的網頁瀏覽器

### 安裝步驟

1. **克隆專案**
   ```bash
   git clone <your-repo-url>
   cd korean-song-recommender
   ```

2. **建立虛擬環境** (建議)
   ```bash
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env 文件，填入你的API密鑰（可選）
   ```

5. **啟動應用**
   ```bash
   cd backend
   python app.py
   ```

6. **開啟瀏覽器**
   - 主要功能：訪問 `http://localhost:5001` 開始使用！
   - 數據分析：訪問 `http://localhost:5001/analytics` 查看分析儀表板

## 📖 使用指南

### 基本操作流程

1. **填寫當前狀態**
   - 🔸 **心情指數** (1-10)：1=很難過，10=超級開心
   - 🔸 **課業壓力** (1-10)：1=無壓力，10=壓力山大
   - 🔸 **疲勞程度** (1-10)：1=精神飽滿，10=累癱了
   - 🔸 **天氣狀況**：晴天/陰天/雨天
   - 🔸 **時間偏好**：早晨/下午/傍晚/夜晚

2. **選擇特殊需求**（可選）
   - 💪 運動時聆聽
   - 📚 讀書專注
   - 😴 助眠放鬆
   - 🔥 需要激勵

3. **獲得推薦**
   - 點擊「為我推薦歌曲」按鈕
   - 等待AI分析（通常1-3秒）
   - 查看推薦結果和解釋

### 推薦結果解讀

每首推薦歌曲都包含：
- **排名**：根據匹配度排序
- **基本資訊**：歌名、藝人、專輯、年份
- **歌曲特徵**：能量/快樂/節拍指數
- **情境標籤**：適用的聆聽情境
- **YouTube連結**：直接聆聽

AI解釋包含：
- **推薦理由**：為什麼適合你的當前狀態
- **匹配因素**：具體的匹配點分析
- **聆聽建議**：最佳的聆聽時機和方式

### 數據分析功能

#### 📊 分析儀表板功能
1. **統計概覽**
   - 歌曲總數、藝人數量
   - 平均能量、快樂指數、節拍速度
   - 用戶互動統計

2. **歌曲分析**
   - 特徵分布圖表
   - 相關性分析
   - 聚類分析

3. **用戶行為分析**
   - 心情、壓力、疲勞分布
   - 天氣偏好統計
   - 使用時間模式

4. **數據匯出**
   - JSON格式完整數據
   - 統計報告文字格式
   - 圖表影像文件

#### 🔬 Jupyter Notebook分析
使用提供的 `korean_song_analysis.ipynb`：

```python
# 設置環境
%matplotlib inline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 載入數據
df = pd.read_json('data/korean_songs.json')

# 基本分析
df.describe()
df.corr()

# 視覺化
plt.figure(figsize=(12, 8))
plt.scatter(df['energy'], df['valence'], 
           c=df['tempo'], cmap='viridis')
plt.xlabel('Energy')
plt.ylabel('Valence')
plt.colorbar(label='Tempo')
plt.show()
```

#### 📈 API端點
- `GET /api/analytics/stats` - 統計數據
- `GET /api/analytics/charts/distribution` - 分布圖表
- `GET /api/analytics/charts/user-behavior` - 用戶行為圖
- `GET /api/analytics/interactions` - 互動記錄
- `GET /api/analytics/export` - 數據匯出

## 🔧 技術架構

### 後端技術棧
- **Flask 2.3.3**：輕量級Python網頁框架
- **Flask-CORS**：跨域請求支援
- **JSON資料庫**：歌曲資料存儲
- **REST API**：前後端分離架構

### 前端技術棧
- **HTML5/CSS3**：現代化網頁標準
- **JavaScript ES6+**：原生JS，無框架依賴
- **響應式設計**：適配各種螢幕尺寸
- **Web Fonts**：Google Fonts字體支援

### 推薦算法
```python
def calculate_song_score(song, user_state):
    score = 0
    
    # 心情匹配 (權重: 20%)
    if mood >= 8:  # 開心時推薦高valence歌曲
        score += song.valence * 0.02
    elif mood <= 3:  # 難過時推薦低valence歌曲
        score += (100 - song.valence) * 0.015
        
    # 疲勞度匹配 (權重: 15%)
    if fatigue >= 7:  # 疲勞時推薦低energy歌曲
        score += (100 - song.energy) * 0.015
    else:  # 精神時推薦高energy歌曲
        score += song.energy * 0.015
        
    # 壓力匹配 (權重: 15%)
    if stress >= 7 and 'relaxing' in song.tags:
        score += 30  # 高壓力時推薦放鬆歌曲
        
    # 天氣影響 (權重: 10%)
    if weather == 'rainy' and 'melancholic' in song.tags:
        score += 25  # 雨天推薦憂鬱歌曲
        
    return score
```

## 📁 專案結構

```
korean-song-recommender/
├── backend/
│   └── app.py                 # Flask應用主程式
├── frontend/
│   └── index.html             # 主頁面HTML
├── static/
│   ├── css/
│   │   └── style.css          # 樣式表
│   └── js/
│       └── main.js            # JavaScript邏輯
├── data/
│   └── korean_songs.json      # 歌曲資料庫
├── requirements.txt           # Python依賴套件
├── .env.example              # 環境變數範例
└── README.md                 # 說明文件
```

## 🔮 API文檔

### POST /api/recommend
推薦歌曲API

**請求格式：**
```json
{
  "mood": 7,
  "stress": 4,
  "fatigue": 6,
  "weather": "sunny",
  "time_preference": "afternoon",
  "needs": ["study", "motivation"]
}
```

**回應格式：**
```json
{
  "recommendations": [
    {
      "title": "Dynamite",
      "artist": "BTS",
      "album": "Dynamite",
      "year": 2020,
      "energy": 85,
      "valence": 90,
      "tempo": 114,
      "tags": ["energetic", "happy", "uplifting"],
      "youtube_url": "https://www.youtube.com/watch?v=...",
      "description": "充滿活力的快樂歌曲"
    }
  ],
  "explanations": [
    {
      "song_title": "Dynamite",
      "artist": "BTS",
      "explanation": "考慮到您不錯的心情和中等疲勞狀態...",
      "matching_factors": ["心情與歌曲愉悅度匹配", "適合下午聆聽"]
    }
  ],
  "user_state": {...},
  "timestamp": "2024-03-15T10:30:00"
}
```

### GET /api/songs
獲取所有歌曲列表

### GET /api/health
健康檢查端點

## 🎨 自定義與擴展

### 添加新歌曲
編輯 `data/korean_songs.json`：

```json
{
  "title": "新歌名",
  "artist": "藝人名",
  "album": "專輯名",
  "year": 2024,
  "genre": "流派",
  "energy": 75,        // 0-100
  "valence": 80,       // 0-100
  "tempo": 120,        // BPM
  "tags": ["tag1", "tag2"],
  "youtube_url": "https://youtube.com/...",
  "description": "歌曲描述"
}
```

### 調整推薦算法
修改 `backend/app.py` 中的 `calculate_song_score` 方法：

```python
def calculate_song_score(self, song, user_state):
    # 自定義你的評分邏輯
    score = 0
    # 添加新的評分因子
    return score
```

### 新增UI元素
1. 在 `frontend/index.html` 添加HTML結構
2. 在 `static/css/style.css` 添加樣式
3. 在 `static/js/main.js` 添加互動邏輯

## 🐛 故障排除

### 常見問題

**Q: 啟動時出現 "ModuleNotFoundError"**
A: 請確認已安裝所有依賴：`pip install -r requirements.txt`

**Q: 頁面無法正常顯示**
A: 檢查Flask是否正確啟動，訪問 `http://localhost:5001/api/health`

**Q: 推薦結果為空**
A: 確認歌曲資料庫文件存在且格式正確

**Q: AI解釋功能異常**
A: 檢查 `.env` 文件中的API密鑰設定

### 調試模式
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

## 🤝 貢獻指南

我們歡迎任何形式的貢獻！

### 如何貢獻
1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 建立 Pull Request

### 貢獻方向
- 🎵 **擴展歌曲庫**：添加更多韓文歌曲
- 🧠 **改進算法**：優化推薦邏輯
- 🎨 **UI/UX設計**：改善用戶體驗
- 🌐 **多語言支持**：添加其他語言介面
- 📱 **移動端優化**：改善手機體驗

## 📄 授權條款

本專案採用 MIT License 授權 - 詳見 [LICENSE](LICENSE) 文件

## 📞 聯繫我們

- **作者**: Your Name
- **Email**: your.email@example.com
- **GitHub**: [your-username](https://github.com/your-username)

## 🙏 致謝

- **音樂資料來源**: YouTube, Spotify, Apple Music
- **設計靈感**: Material Design, K-pop官方網站
- **技術參考**: Flask官方文檔, MDN Web Docs

---

**🎵 享受你的音樂時光！讓AI為你找到最適合的韓文歌曲！** 🎵