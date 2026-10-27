import os
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info')
def get_info():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'success': False, 'error': 'Link မပါဝင်ပါ။'})

    try:
        # အခမဲ့နဲ့ တည်ငြိမ်တဲ့ YouTube Downloader API တစ်ခုကို အသုံးပြုခြင်း
        api_url = f"https://apis.davidcyriltech.my.id/youtube/dl?url={url}"
        response = requests.get(api_url, timeout=15)
        res_data = response.json()

        if res_data.get('status') == 200 and 'result' in res_data:
            data = res_data['result']
            video_title = data.get('title', 'YouTube Video')
            thumbnail_url = data.get('thumbnail', '')
            
            # Download link (mp4 format အကောင်းဆုံးကို ယူရန်)
            download_url = data.get('download_url', '')
            if not download_url and 'quality' in data:
                # quality formats ထဲမှ ယူရန်
                download_url = data.get('quality', [{}])[0].get('url', '')

            if not download_url:
                return jsonify({'success': False, 'error': 'Download Link ရှာမတွေ့ပါ။'})

            return jsonify({
                'success': True,
                'title': video_title,
                'thumbnail': thumbnail_url,
                'download_url': download_url,
            })
        else:
            return jsonify({'success': False, 'error': 'API မှ ဗီဒီယိုအချက်အလက် ရယူ၍မရပါ။'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
