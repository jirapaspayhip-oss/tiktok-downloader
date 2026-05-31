from flask import Flask, request, jsonify, render_template_string, Response
import requests
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ TIKTOK CYBER DOWNLOADER</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>
        html, body { cursor: none !important; overflow-x: hidden; }
        a, button, input, label { cursor: none !important; }

        /* 🖱️ เคอร์เซอร์เมาส์แสงนีออน */
        .cursor-dot { width: 8px; height: 8px; background-color: #22d3ee; position: fixed; pointer-events: none; z-index: 9999; border-radius: 50%; transform: translate(-50%, -50%); }
        .cursor-outline { width: 40px; height: 40px; border: 2px solid #ec4899; position: fixed; pointer-events: none; z-index: 9998; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 15px #ec4899, inset 0 0 10px #ec4899; opacity: 0.8; transition: transform 0.08s ease-out, width 0.2s, height 0.2s, border-color 0.2s; }
        .cursor-hover .cursor-dot { width: 4px; height: 4px; background-color: #ec4899; }
        .cursor-hover .cursor-outline { width: 55px; height: 55px; border-color: #22d3ee; box-shadow: 0 0 25px #22d3ee, inset 0 0 15px #22d3ee; }

        /* 🎥 วิดีโอพื้นหลัง */
        .video-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; overflow: hidden; }
        .video-bg iframe { width: 100vw; height: 56.25vw; min-height: 100vh; min-width: 177.77vh; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); filter: brightness(0.55) contrast(1.15) saturate(1.1); }
    </style>
</head>
<body class="bg-slate-950 text-gray-100 min-h-screen flex flex-col items-center justify-center p-4 antialiased font-sans relative">
    
    <div class="cursor-dot" id="customDot"></div>
    <div class="cursor-outline" id="customOutline"></div>

    <div class="video-bg" id="bgContainer"></div>

    <div id="welcomeOverlay" class="fixed inset-0 bg-slate-950 flex flex-col items-center justify-center z-50 transition-opacity duration-700">
        <div class="text-center p-8 rounded-3xl border border-pink-500/30 bg-slate-900/80 backdrop-blur-xl max-w-sm" style="box-shadow: 0 0 30px rgba(236, 72, 153, 0.3);">
            <h2 class="text-2xl font-black bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent uppercase mb-2">⚡ SYSTEM READY</h2>
            <p class="text-xs text-slate-400 mb-6 font-mono">CLICK TO ACTIVATE AUDIO & VIDEO PATH</p>
            <button id="enterBtn" class="px-8 py-3.5 bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 font-bold rounded-xl shadow-lg uppercase text-xs font-mono tracking-widest transition-all">
                ENTER SYSTEM
            </button>
        </div>
    </div>

    <div class="w-full max-w-md bg-slate-900/75 backdrop-blur-xl p-8 rounded-3xl border border-pink-500/40 relative overflow-hidden" style="box-shadow: 0 0 30px rgba(236, 72, 153, 0.25);">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500"></div>
        <div class="text-center mb-8">
            <h1 class="text-3xl font-extrabold tracking-wider bg-gradient-to-r from-pink-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent uppercase">🔥 TikTok Cyber</h1>
            <p class="text-[10px] uppercase font-mono tracking-widest text-cyan-400 mt-1">ILLSLICK TRACK + AUDIO SYNCED</p>
        </div>
        <form id="downloadForm" class="space-y-5">
            <input type="url" id="videoUrl" required placeholder="วางลิงก์ TikTok ตรงนี้..." class="w-full px-5 py-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-pink-500 focus:ring-1 focus:ring-pink-500 text-sm font-mono">
            <div class="bg-slate-950/90 p-1.5 rounded-2xl border border-slate-800/80 flex justify-between items-center text-xs font-mono">
                <label class="w-1/2 text-center py-2.5 cursor-pointer flex items-center justify-center space-x-2"><input type="radio" name="downloadType" value="mp4" checked class="accent-pink-500"><span>🎥 VIDEO MP4 HD</span></label>
                <div class="w-px h-6 bg-slate-800"></div>
                <label class="w-1/2 text-center py-2.5 cursor-pointer flex items-center justify-center space-x-2"><input type="radio" name="downloadType" value="mp3" class="accent-cyan-400"><span>🎵 AUDIO MP3</span></label>
            </div>
            <button type="submit" id="submitBtn" class="w-full py-4 bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 font-bold rounded-2xl shadow-lg uppercase text-sm font-mono">LAUNCH EXTRACT</button>
        </form>
        <div id="resultSection" class="mt-8 hidden border-t border-slate-800 pt-6 text-center">
            <img id="videoCover" src="" class="w-36 h-36 mx-auto rounded-2xl object-cover border border-slate-700 shadow-2xl mb-4">
            <p id="videoTitle" class="text-sm text-slate-300 mb-2 px-1 line-clamp-2 text-left bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/50"></p>
            <p id="videoAuthor" class="text-xs text-cyan-400 mb-5 font-mono font-bold"></p>
            <a id="downloadBtn" href="" class="block w-full py-4 bg-emerald-600 hover:bg-emerald-500 font-bold rounded-2xl text-center shadow-lg uppercase text-sm font-mono" style="box-shadow: 0 0 20px rgba(16, 185, 129, 0.6);">⚡ DOWNLOAD FILE NOW</a>
        </div>
    </div>

    <script>
        const dot = document.getElementById('customDot');
        const outline = document.getElementById('customOutline');

        // ควบคุมตำแหน่งเมาส์นีออน
        window.addEventListener('mousemove', (e) => {
            dot.style.left = `${e.clientX}px`; dot.style.top = `${e.clientY}px`;
            outline.style.left = `${e.clientX}px`; outline.style.top = `${e.clientY}px`;
        });

        // จัดการ Hover เมาส์
        function refreshCursorListeners() {
            document.querySelectorAll('a, button, input, label').forEach(el => {
                el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
                el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
            });
        }
        refreshCursorListeners();

        // 🔊 สคริปต์กดปุ่มเพื่อเล่นเพลงพร้อมวิดีโอ
        document.getElementById('enterBtn').addEventListener('click', () => {
            const overlay = document.getElementById('welcomeOverlay');
            overlay.classList.add('opacity-0');
            setTimeout(() => overlay.remove(), 700); // ลบหน้าต่างต้อนรับออกหลังจางหาย

            // ฝังวิดีโอ YouTube แบบเปิดเสียง (mute=0) และให้เปิดเล่นทันที (autoplay=1)
            document.getElementById('bgContainer').innerHTML = `<iframe src="https://www.youtube.com/embed/fXw1PERFGMs?autoplay=1&mute=0&loop=1&playlist=fXw1PERFGMs&controls=0&showinfo=0&rel=0&modestbranding=1&iv_load_policy=3" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>`;
        });

        // ระบบดาวน์โหลด TikTok
        document.getElementById('downloadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('videoUrl').value;
            const type = document.querySelector('input[name="downloadType"]:checked').value;
            const submitBtn = document.getElementById('submitBtn');
            const resultSection = document.getElementById('resultSection');
            resultSection.classList.add('hidden');
            submitBtn.innerText = '🛰️ CODESYNC IN PROGRESS...';
            submitBtn.disabled = true;
            try {
                const formData = new FormData(); formData.append('url', url); formData.append('type', type);
                const response = await fetch('/api/download', { method: 'POST', body: formData });
                const data = await response.json();
                if (data.success) {
                    document.getElementById('videoCover').src = data.cover;
                    document.getElementById('videoTitle').innerText = data.title;
                    document.getElementById('videoAuthor').innerText = '👤 AUTHOR: @' + data.author.toUpperCase();
                    document.getElementById('downloadBtn').href = `/api/fetch_file?file_url=${encodeURIComponent(data.file_url)}&id=${data.id}&ext=${type}&author=${encodeURIComponent(data.author)}`;
                    resultSection.classList.remove('hidden');
                    setTimeout(refreshCursorListeners, 100);
                } else { alert('⚡ CYBER ERROR: ' + data.message); }
            } catch (error) { alert('⚡ SYSTEM ERROR: Connection failed.'); }
            finally { submitBtn.innerText = 'LAUNCH EXTRACT'; submitBtn.disabled = false; }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    download_type = request.form.get('type', 'mp4')
    if not video_url: return jsonify({'success': False, 'message': 'กรุณาใส่ลิงก์'})
    try:
        api_url = "https://www.tikwm.com/api/"
        response = requests.post(api_url, data={'url': video_url}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        data = response.json()
        if data.get('code') == 0 and 'data' in data:
            res_data = data['data']
            video_id = res_data.get('id', 'file')
            author_info = res_data.get('author', {})
            author_name = author_info.get('unique_id') or author_info.get('nickname') or "User"
            author_name = re.sub(r'[^a-zA-Z0-9_\-]', '', author_name)
            target_link = res_data.get('music') if download_type == 'mp3' else (res_data.get('hdplay') or res_data.get('play'))
            if target_link:
                if target_link.startswith('//'): target_link = 'https:' + target_link
                elif not target_link.startswith('http'): target_link = 'https://www.tikwm.com' + target_link
                return jsonify({'success': True, 'title': res_data.get('title', 'Video'), 'cover': res_data.get('cover', ''), 'file_url': target_link, 'id': video_id, 'author': author_name})
        return jsonify({'success': False, 'message': 'ไม่พบข้อมูลคลิป'})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

@app.route('/api/fetch_file')
def fetch_file():
    file_url = request.args.get('file_url')
    file_id = request.args.get('id', 'file')
    ext = request.args.get('ext', 'mp4')
    author = request.args.get('author', 'User')
    try:
        req = requests.get(file_url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
        response = Response(req.iter_content(chunk_size=1024*1024), content_type=req.headers.get('Content-Type'))
        response.headers['Content-Disposition'] = f'attachment; filename=@{author}_{file_id}.{ext}'
        return response
    except Exception as e: return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    