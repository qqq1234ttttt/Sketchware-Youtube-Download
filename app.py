import os
from flask import Flask, jsonify, render_template, request
from yt_dlp import YoutubeDL

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info')
def get_info():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'success': False, 'error': 'Link မပါဝင်ပါ။'})

    # YouTube ၏ Bot restriction ကို ကျော်လွှားရန် ios နှင့် web client ကို အသုံးပြုထားပါသည်
    ydl_opts = {
        'format': 'best',
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'web']
            }
        },
        'extract_flat': False,
        'skip_download': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'YouTube Video')
            thumbnail_url = info.get('thumbnail', '')

            best_url = info.get('url', '')

            # URL တိုက်ရိုက်မပါလာပါက formats ထဲမှ ရှာမည်
            if not best_url:
                formats = info.get('formats', [])
                for f in formats:
                    if f.get('url') and f.get('vcodec') != 'none':
                        best_url = f.get('url')
                        break
                if not best_url and formats:
                    best_url = formats[0].get('url')

            if not best_url:
                return jsonify({'success': False, 'error': 'Download ရယူနိုင်သော Link မရှိပါ။'})

            return jsonify({
                'success': True,
                'title': video_title,
                'thumbnail': thumbnail_url,
                'download_url': best_url,
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
