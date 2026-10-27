import os
from flask import Flask, jsonify, render_template_string, request
from yt_dlp import YoutubeDL

app = Flask(__name__, template_folder='.')

# HTML / CSS / JS UI (တဇိုင်းလန်းလန်း Dark Theme Design)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KMT YouTube Downloader</title>
    <style>
        :root {
            --bg-color: #080D18;
            --card-bg: #111A2E;
            --accent-color: #4F46E5;
            --accent-hover: #6366F1;
            --text-color: #F3F4F6;
            --text-muted: #9CA3AF;
            --border-color: #1E293B;
            --danger-color: #EF4444;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            width: 100%;
            max-width: 480px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 22px;
            color: #FFFFFF;
            letter-spacing: 0.5px;
        }
        .input-group {
            position: relative;
            margin-bottom: 16px;
        }
        input[type="text"] {
            width: 100%;
            padding: 14px 90px 14px 16px;
            background: #0B1120;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-color);
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            border-color: var(--accent-color);
        }
        .btn-actions {
            position: absolute;
            right: 6px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 4px;
        }
        .icon-btn {
            background: #1E293B;
            border: none;
            color: var(--text-muted);
            padding: 6px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s, color 0.2s;
        }
        .icon-btn:hover {
            background: var(--accent-color);
            color: #FFF;
        }
        .search-btn {
            width: 100%;
            padding: 14px;
            background: var(--accent-color);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        .search-btn:hover {
            background: var(--accent-hover);
        }
        .loader {
            display: none;
            text-align: center;
            margin-top: 20px;
            color: var(--text-muted);
            font-size: 14px;
        }
        .spinner {
            width: 24px;
            height: 24px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top: 3px solid var(--accent-color);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 10px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .result-card {
            display: none;
            margin-top: 20px;
            background: #0B1120;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
        }
        .thumbnail {
            width: 100%;
            height: 180px;
            object-fit: cover;
            background: #000;
        }
        .video-info {
            padding: 14px;
        }
        .video-title {
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 12px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .download-btn {
            display: block;
            width: 100%;
            text-align: center;
            padding: 12px;
            background: #10B981;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            transition: background 0.3s;
        }
        .download-btn:hover {
            background: #059669;
        }
        .error-msg {
            display: none;
            margin-top: 15px;
            padding: 12px;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid var(--danger-color);
            color: #F87171;
            border-radius: 8px;
            font-size: 13px;
            text-align: center;
        }
    </style>
</head>
<body>

    <div class="container">
        <h2>KMT YouTube Downloader</h2>
        
        <div class="input-group">
            <input type="text" id="urlInput" placeholder="YouTube Link ထည့်ပါ...">
            <div class="btn-actions">
                <button class="icon-btn" onclick="pasteText()" title="Paste">Paste</button>
                <button class="icon-btn" onclick="copyText()" title="Copy">Copy</button>
                <button class="icon-btn" onclick="clearText()" title="Clear">Clear</button>
            </div>
        </div>
        
        <button class="search-btn" onclick="fetchVideoInfo()">ဗီဒီယို ရှာမည်</button>

        <div class="loader" id="loader">
            <div class="spinner"></div>
            ဗီဒီယို အချက်အလက်များကို ရှာဖွေနေပါသည်...
        </div>

        <div class="error-msg" id="errorMsg"></div>

        <div class="result-card" id="resultCard">
            <img id="vidThumb" class="thumbnail" src="" alt="Thumbnail">
            <div class="video-info">
                <div id="vidTitle" class="video-title"></div>
                <a id="downloadLink" href="#" class="download-btn">Download ယူမည်</a>
            </div>
        </div>
    </div>

    <script>
        async function pasteText() {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById('urlInput').value = text;
            } catch (err) {
                alert('Clipboard မှ ဖတ်၍မရပါ။');
            }
        }

        function copyText() {
            const input = document.getElementById('urlInput');
            input.select();
            document.execCommand('copy');
        }

        function clearText() {
            document.getElementById('urlInput').value = '';
            document.getElementById('resultCard').style.display = 'none';
            document.getElementById('errorMsg').style.display = 'none';
        }

        async function fetchVideoInfo() {
            const url = document.getElementById('urlInput').value.trim();
            const loader = document.getElementById('loader');
            const resultCard = document.getElementById('resultCard');
            const errorMsg = document.getElementById('errorMsg');

            if (!url) {
                alert('ကျေးဇူးပြု၍ YouTube Link ထည့်ပါ။');
                return;
            }

            loader.style.display = 'block';
            resultCard.style.display = 'none';
            errorMsg.style.display = 'none';

            try {
                let response = await fetch('/get_info?url=' + encodeURIComponent(url));
                let data = await response.json();

                loader.style.display = 'none';

                if (data.success) {
                    document.getElementById('vidThumb').src = data.thumbnail;
                    document.getElementById('vidTitle').innerText = data.title;
                    document.getElementById('downloadLink').href = data.download_url;
                    resultCard.style.display = 'block';
                } else {
                    errorMsg.innerText = data.error || 'ဗီဒီယို ရှာမတွေ့ပါ။';
                    errorMsg.style.display = 'block';
                }
            } catch (err) {
                loader.style.display = 'none';
                errorMsg.innerText = 'ဆာဗာသို့ ချိတ်ဆက်၍ မရပါ။';
                errorMsg.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_info')
def get_info():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'success': False, 'error': 'Link မပါဝင်ပါ။'})
    
    ydl_opts = {'extract_flat': False, 'skip_download': True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'YouTube Video')
            thumbnail_url = info.get('thumbnail', '')
            
            # Direct Download stream url ရယူရန်
            formats = info.get('formats', [])
            best_url = ''
            for f in formats:
                if f.get('ext') == 'mp4' and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    best_url = f.get('url')
                    break
            if not best_url and formats:
                best_url = formats[0].get('url')

            return jsonify({
                'success': True,
                'title': video_title,
                'thumbnail': thumbnail_url,
                'download_url': best_url
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
