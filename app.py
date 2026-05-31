import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# แก้ไขลิงก์เป็นเพลงแดนซ์ใหม่ล่าสุดของคุณเรียบร้อยครับ
MUSIC_URL = "https://audio.jofreestyler.com/api2/download/d1f8dae8499252a10cd2d6995ee74390/7636781163884973330.mp3"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Downloader - ไม่ติดลายน้ำ</title>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Kanit', sans-serif;
        }
        body {
            background-color: #121214;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            overflow: hidden;
            position: relative;
        }
        .container {
            background: #1e1e24;
            border: 2px solid #ff0050;
            border-radius: 16px;
            padding: 40px 30px;
            width: 100%;
            max-width: 480px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(255, 0, 80, 0.2);
            z-index: 10;
        }
        h1 {
            color: #ff0050;
            font-size: 28px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .subtitle {
            color: #a1a1aa;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 16px;
            background: #2a2a32;
            border: 1px solid #3f3f46;
            border-radius: 8px;
            color: #ffffff;
            font-size: 15px;
            outline: none;
            transition: all 0.3s;
        }
        input:focus {
            border-color: #ff0050;
            box-shadow: 0 0 8px rgba(255, 0, 80, 0.3);
        }
        button {
            width: 100%;
            padding: 16px;
            background: #ff0050;
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
        }
        button:hover {
            background: #e60048;
        }
        button:active {
            transform: scale(0.98);
        }
        .result-area {
            margin-top: 25px;
            display: none;
        }
        .video-title {
            color: #ffffff;
            font-size: 15px;
            margin-bottom: 15px;
            text-align: left;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .download-btn {
            background: #00f2fe;
            color: #121214;
            margin-top: 10px;
            text-decoration: none;
            display: block;
            padding: 16px;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.2s;
        }
        .download-btn:hover {
            background: #00d8e4;
        }
        .error-msg {
            color: #ef4444;
            margin-top: 15px;
            font-size: 14px;
            display: none;
        }
        .loading {
            display: none;
            color: #00f2fe;
            margin-top: 15px;
            font-size: 14px;
        }
    </style>
</head>
<body>

    <audio id="bg-music" autoplay loop>
        <source src="{{ music_url }}" type="audio/mpeg">
    </audio>

    <div class="container">
        <h1>TikTok Downloader</h1>
        <div class="subtitle">วางลิ้งก์วิดีโอ TikTok เพื่อดาวน์โหลดแบบไม่มีลายน้ำ</div>
        
        <div class="input-group">
            <input type="text" id="tiktokUrl" placeholder="วางลิงก์ TikTok ที่นี่... (https://vt.tiktok.com/...)">
        </div>
        
        <button id="searchBtn" onclick="getTiktokVideo()">ค้นหาวิดีโอ</button>

        <div class="loading" id="loadingText">กำลังดึงข้อมูลวิดีโอ กรุณารอสักครู่...</div>
        <div class="error-msg" id="errorText"></div>

        <div class="result-area" id="resultArea">
            <div class="video-title" id="videoTitle"></div>
            <a href="#" class="download-btn" id="dlNoWatermark" target="_blank" download>📥 ดาวน์โหลดวิดีโอ (ไม่มีลายน้ำ)</a>
            <a href="#" class="download-btn" id="dlMusic" target="_blank" style="background: #a1a1aa; color: white;" download>🎵 ดาวน์โหลดเพลงประกอบ</a>
        </div>
    </div>

    <script>
        const audio = document.getElementById('bg-music');

        // สั่งให้เพลงเล่นทันทีเมื่อคลิกหน้าจอครั้งแรก ตามกฎของบราวเซอร์
        document.body.addEventListener('click', () => {
            if (audio.paused) {
                audio.play().catch(e => console.log("Autoplay blocked"));
            }
        }, { once: true });

        async function getTiktokVideo() {
            const urlInput = document.getElementById('tiktokUrl').value.trim();
            const searchBtn = document.getElementById('searchBtn');
            const loadingText = document.getElementById('loadingText');
            const errorText = document.getElementById('errorText');
            const resultArea = document.getElementById('resultArea');

            if (!urlInput) {
                alert('กรุณาใส่ลิงก์ TikTok ก่อนครับ');
                return;
            }

            searchBtn.disabled = true;
            loadingText.style.display = 'block';
            errorText.style.display = 'none';
            resultArea.style.display = 'none';

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ 'url': urlInput })
                });

                const data = await response.json();

                if (data.success) {
                    document.getElementById('videoTitle').innerText = data.title;
                    document.getElementById('dlNoWatermark').href = data.video_nowatermark;
                    document.getElementById('dlMusic').href = data.music;
                    resultArea.style.display = 'block';
                } else {
                    errorText.innerText = data.message || 'เกิดข้อผิดพลาด ไม่สามารถดึงวิดีโอได้';
                    errorText.style.display = 'block';
                }
            } catch (error) {
                errorText.innerText = 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณาลองใหม่อีกครั้ง';
                errorText.style.display = 'block';
            } finally {
                searchBtn.disabled = false;
                loadingText.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

def get_tiktok_video(url):
    try:
        api_url = "https://www.tikwm.com/api/"
        payload = {'url': url}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }
        response = requests.post(api_url, data=payload, headers=headers)
        data = response.json()
        
        if data.get('code') == 0:
            return {
                'success': True,
                'title': data['data'].get('title', 'วิดีโอ TikTok'),
                'video_nowatermark': data['data'].get('play'),
                'music': data['data'].get('music')
            }
        return {'success': False, 'message': 'ไม่พบวิดีโอ หรือลิงก์ไม่ถูกต้อง'}
    except Exception as e:
        return {'success': False, 'message': f'เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}'}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, music_url=MUSIC_URL)

@app.route('/api/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    if not video_url:
        return jsonify({'success': False, 'message': 'กรุณาใส่ลิงก์ TikTok'})
    result = get_tiktok_video(video_url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    