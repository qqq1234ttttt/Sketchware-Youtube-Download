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
        # ၁။ ပထမအဆင့် - လင့်ခ်ကို ပို့ပြီး Resource Metadata နှင့် Key များကို တောင်းခံခြင်း
        api_url = f"https://app.argonfetch.dev/api/Fetch/GetResource?url={url}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(api_url, headers=headers, timeout=25)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'API Server Error (Status {response.status_code})'})

        res_data = response.json()
        
        video_title = res_data.get('title', 'KMT YouTube Download')
        thumbnail_url = res_data.get('cover', '') or res_data.get('thumbnail', '')

        # ၂။ ဒုတိယအဆင့် - ရလာသော Renditions များထဲမှ key ကို ယူ၍ Download Stream Link တည်ဆောက်ခြင်း
        download_url = ''
        renditions = res_data.get('renditions', []) or res_data.get('formats', [])
        
        if isinstance(renditions, list) and len(renditions) > 0:
            # ပထမဆုံးရတဲ့ item သို့မဟုတ် အသင့်တော်ဆုံး quality ကို ယူခြင်း
            item = renditions
            key = item.get('key', '')
            if key:
                # Video နဲ့ Audio ပေါင်းပြီးသား Combined Stream လမ်းကြောင်းကို ဖန်တီးခြင်း
                download_url = f"https://app.argonfetch.dev/api/Stream/Combined/{key}"

        if not download_url:
            # Fallback အနေဖြင့် တစ်ခြား url ပါလာပါက ယူရန်
            download_url = res_data.get('url', '')

        if not download_url:
            return jsonify({'success': False, 'error': 'Download Link ရှာမတွေ့ပါ။'})

        return jsonify({
            'success': True,
            'title': video_title,
            'thumbnail': thumbnail_url,
            'download_url': download_url,
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
